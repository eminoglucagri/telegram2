"""Script to generate Telegram session string.

Run this script once to authenticate and get a session string.
Store the session string in your .env file.

Usage:
    python scripts/login.py
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    print("Telegram Session Generator")
    print("=" * 40)
    print()
    
    api_id = input("Enter your API ID: ").strip()
    api_hash = input("Enter your API Hash: ").strip()
    phone = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
    
    print()
    print("Connecting to Telegram...")
    
    client = TelegramClient(StringSession(), int(api_id), api_hash)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print(f"Sending code to {phone}...")
        await client.send_code_request(phone)
        
        code = input("Enter the code you received: ").strip()
        
        try:
            await client.sign_in(phone, code)
        except Exception as e:
            if "Two-step" in str(e) or "2FA" in str(e):
                password = input("Enter your 2FA password: ").strip()
                await client.sign_in(password=password)
            else:
                raise
    
    # Get session string
    session_string = client.session.save()
    
    # Get user info
    me = await client.get_me()
    
    print()
    print("=" * 40)
    print("Login successful!")
    print(f"Logged in as: {me.first_name} (@{me.username})")
    print()
    print("Your session string (add to .env as TELEGRAM_SESSION_STRING):")
    print()
    print(session_string)
    print()
    print("=" * 40)
    print("IMPORTANT: Keep this session string secret!")
    print("Add it to your .env file as:")
    print(f"TELEGRAM_SESSION_STRING={session_string}")
    
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
