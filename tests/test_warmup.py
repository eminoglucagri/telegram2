"""Tests for warm-up tracking module."""

import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock


class TestWarmUpStages:
    """Test warm-up stage configurations."""
    
    def test_stage_1_limits(self):
        """Test Stage 1 has minimal limits."""
        from src.modules.warmup.tracker import WarmUpTracker
        
        stage_config = WarmUpTracker.STAGES[1]
        
        assert stage_config["max_messages_per_day"] == 5
        assert stage_config["max_groups"] == 2
        assert "read" in stage_config["allowed_actions"]
        assert "react" in stage_config["allowed_actions"]
        assert "reply" not in stage_config["allowed_actions"]
    
    def test_stage_5_full_access(self):
        """Test Stage 5 has full access."""
        from src.modules.warmup.tracker import WarmUpTracker
        
        stage_config = WarmUpTracker.STAGES[5]
        
        assert stage_config["max_messages_per_day"] == 100
        assert "dm_initiate" in stage_config["allowed_actions"]
    
    def test_stages_progress_correctly(self):
        """Test that stage limits increase progressively."""
        from src.modules.warmup.tracker import WarmUpTracker
        
        prev_messages = 0
        for stage_num in range(1, 6):
            stage = WarmUpTracker.STAGES[stage_num]
            assert stage["max_messages_per_day"] > prev_messages
            prev_messages = stage["max_messages_per_day"]


class TestWarmUpActions:
    """Test action permission checking."""
    
    def test_read_allowed_in_all_stages(self):
        """Read action should be allowed in all stages."""
        from src.modules.warmup.tracker import WarmUpTracker
        
        for stage_num, stage in WarmUpTracker.STAGES.items():
            assert "read" in stage["allowed_actions"]
    
    def test_dm_initiate_only_stage_5(self):
        """DM initiation should only be allowed in stage 5."""
        from src.modules.warmup.tracker import WarmUpTracker
        
        for stage_num, stage in WarmUpTracker.STAGES.items():
            if stage_num < 5:
                assert "dm_initiate" not in stage["allowed_actions"]
            else:
                assert "dm_initiate" in stage["allowed_actions"]


# Add more tests as needed
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
