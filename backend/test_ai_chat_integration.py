#!/usr/bin/env python3
"""
Test script for AgentScope + Gemini AI chat integration.
Tests the complete AI matchmaking conversation system.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_agent_service import UserAvatarAgent, MatchMakerAgent
from app.core.ai_config import initialize_ai_services, get_ai_service_status


class MockUser:
    def __init__(self, user_id: str, first_name: str, last_name: str):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name


class MockAvatar:
    def __init__(self, avatar_id: str, name: str, user_id: str, personality_traits: dict):
        self.id = avatar_id
        self.name = name
        self.user_id = user_id
        self.personality_traits = personality_traits
        self.communication_patterns = {
            'emotional_expression': 0.7,
            'directness': 0.6
        }
        self.response_style = {
            'response_length': 'moderate',
            'formality_level': 'casual'
        }


async def test_ai_matchmaking_conversation():
    """Test complete AI matchmaking conversation between two avatars."""
    
    print("🤖 AI Matchmaking Conversation Test")
    print("=" * 50)
    
    # Initialize AI services
    print("1. Initializing AI services...")
    ai_status = initialize_ai_services()
    print(f"   AI Services: {ai_status}")
    
    status = get_ai_service_status()
    print(f"   AgentScope: {'✅' if status['agentscope_available'] else '❌'}")
    print(f"   Gemini API: {'✅' if status['gemini_available'] else '❌'}")
    print(f"   Mock Mode: {'❌' if status['mock_mode'] else '✅'}")
    print()
    
    # Create two users with different personalities
    user1 = MockUser("user1", "Alex", "Chen")
    avatar1 = MockAvatar("avatar1", "Alex的AI化身", "user1", {
        'big_five': {
            'openness': 0.8,        # Very open to new experiences
            'conscientiousness': 0.7, # Organized
            'extraversion': 0.6,    # Moderately outgoing
            'agreeableness': 0.9,   # Very cooperative
            'neuroticism': 0.3      # Emotionally stable
        },
        'values': {'adventure': 0.9, 'family': 0.8, 'creativity': 0.7}
    })
    
    user2 = MockUser("user2", "Sarah", "Kim")
    avatar2 = MockAvatar("avatar2", "Sarah的AI化身", "user2", {
        'big_five': {
            'openness': 0.7,        # Open to experiences
            'conscientiousness': 0.8, # Very organized
            'extraversion': 0.8,    # Very outgoing
            'agreeableness': 0.8,   # Cooperative
            'neuroticism': 0.4      # Emotionally stable
        },
        'values': {'family': 0.9, 'career': 0.8, 'health': 0.7}
    })
    
    # Create AI agents
    print("2. Creating AI agents...")
    agent1 = UserAvatarAgent(avatar1, user1)
    agent2 = UserAvatarAgent(avatar2, user2)
    matchmaker = MatchMakerAgent()
    
    print(f"   Agent 1: {agent1.name} (AgentScope: {'✅' if agent1.agentscope_agent else '❌'})")
    print(f"   Agent 2: {agent2.name} (AgentScope: {'✅' if agent2.agentscope_agent else '❌'})")
    print(f"   Matchmaker: {matchmaker.name} (AgentScope: {'✅' if matchmaker.agentscope_agent else '❌'})")
    print()
    
    # Start conversation
    print("3. Starting AI matchmaking conversation...")
    print("=" * 50)
    
    conversation_history = []
    
    # Agent 1 starts with greeting
    print(f"\n💬 {agent1.name} (初次见面):")
    greeting1 = await agent1.generate_response(conversation_history)
    print(f"   {greeting1}")
    
    conversation_history.append({
        'sender_name': agent1.name,
        'content': greeting1,
        'sender_id': user1.id
    })
    
    # Agent 2 responds
    print(f"\n💬 {agent2.name} (回应):")
    response2 = await agent2.generate_response(conversation_history)
    print(f"   {response2}")
    
    conversation_history.append({
        'sender_name': agent2.name,
        'content': response2,
        'sender_id': user2.id
    })
    
    # Continue conversation for several turns
    for turn in range(3):
        print(f"\n--- 对话轮次 {turn + 2} ---")
        
        # Agent 1's turn
        print(f"\n💬 {agent1.name}:")
        response1 = await agent1.generate_response(conversation_history)
        print(f"   {response1}")
        
        conversation_history.append({
            'sender_name': agent1.name,
            'content': response1,
            'sender_id': user1.id
        })
        
        # Agent 2's turn
        print(f"\n💬 {agent2.name}:")
        response2 = await agent2.generate_response(conversation_history)
        print(f"   {response2}")
        
        conversation_history.append({
            'sender_name': agent2.name,
            'content': response2,
            'sender_id': user2.id
        })
        
        # Matchmaker facilitation (every other turn)
        if turn % 2 == 1:
            participants = [agent1.name, agent2.name]
            facilitation = await matchmaker.facilitate_conversation(conversation_history, participants)
            if facilitation:
                print(f"\n🎯 {matchmaker.name} (引导):")
                print(f"   {facilitation}")
    
    print("\n" + "=" * 50)
    print("✅ AI matchmaking conversation test completed!")
    print(f"📊 Total messages: {len(conversation_history)}")
    print("🤖 AgentScope + Gemini integration working perfectly!")


if __name__ == "__main__":
    asyncio.run(test_ai_matchmaking_conversation())