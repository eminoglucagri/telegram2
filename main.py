"""Main entry point for running the Telegram Agent.

This module provides different ways to run the application:
1. API Server only
2. Bot only
3. Both together
"""

import asyncio
import argparse
import sys
from typing import Optional

import uvicorn
import structlog

from src.utils.logger import setup_logging
from src.core.config import settings

logger = structlog.get_logger(__name__)


async def run_bot():
    """Run the Telegram bot."""
    from src.core.bot import bot
    from src.database.base import get_db, init_db
    
    setup_logging()
    logger.info("Initializing database...")
    await init_db()
    
    logger.info("Connecting to Telegram...")
    try:
        await bot.connect()
        logger.info("Bot connected successfully!")
        
        # Register message handlers here
        # Example:
        # from src.modules.conversation.handler import handle_new_message
        # bot.add_handler("new_message", handle_new_message)
        
        logger.info("Bot is running. Press Ctrl+C to stop.")
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await bot.disconnect()


def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info" if settings.debug else "warning"
    )


async def run_all():
    """Run both API and bot together."""
    import threading
    
    # Run API in a separate thread
    api_thread = threading.Thread(
        target=run_api,
        kwargs={"host": "0.0.0.0", "port": 8000, "reload": False},
        daemon=True
    )
    api_thread.start()
    logger.info("API server started in background")
    
    # Run bot in main thread
    await run_bot()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Telegram Stealth Marketing Agent"
    )
    parser.add_argument(
        "--mode",
        choices=["api", "bot", "all"],
        default="api",
        help="Run mode: api (default), bot, or all"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API port (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.mode == "api":
        logger.info(f"Starting API server on {args.host}:{args.port}")
        run_api(args.host, args.port, args.reload)
    
    elif args.mode == "bot":
        logger.info("Starting Telegram bot...")
        asyncio.run(run_bot())
    
    elif args.mode == "all":
        logger.info("Starting both API and bot...")
        asyncio.run(run_all())


if __name__ == "__main__":
    main()
