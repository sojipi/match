#!/usr/bin/env python3
"""
Test script to verify conversation duration improvements.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def test_conversation_settings():
    """Test conversation configuration settings."""
    print("🔧 Conversation Configuration Test")
    print("=" * 40)
    
    print(f"MAX_CONVERSATION_TURNS: {settings.MAX_CONVERSATION_TURNS}")
    print(f"CONVERSATION_TIMEOUT_SECONDS: {settings.CONVERSATION_TIMEOUT_SECONDS}")
    print(f"AGENT_RESPONSE_TIMEOUT_SECONDS: {settings.AGENT_RESPONSE_TIMEOUT_SECONDS}")
    
    # Calculate expected conversation duration
    turns = settings.MAX_CONVERSATION_TURNS
    delay_per_turn = 4  # seconds (from websocket manager)
    expected_duration = turns * delay_per_turn
    
    print(f"\nExpected conversation duration:")
    print(f"  - Total turns: {turns}")
    print(f"  - Delay per turn: {delay_per_turn}s")
    print(f"  - Total duration: {expected_duration}s ({expected_duration/60:.1f} minutes)")
    
    if turns >= 12:
        print("✅ Conversation duration improved (was 6 turns, now >= 12)")
    else:
        print("❌ Conversation duration still too short")
    
    return turns >= 12

if __name__ == "__main__":
    success = test_conversation_settings()
    if success:
        print("\n🎉 Conversation duration improvements verified!")
    else:
        print("\n❌ Conversation duration needs adjustment")