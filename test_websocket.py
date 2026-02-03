#!/usr/bin/env python3
"""
Simple WebSocket client to test the AI Matchmaker WebSocket endpoint
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    uri = "ws://localhost:8000/ws/session/test-session-123?token=demo_token"
    
    try:
        print(f"Connecting to {uri}")
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")
            
            # Send a test message
            test_message = {
                "type": "start_conversation",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"Sent: {test_message}")
            
            # Listen for messages for 30 seconds
            try:
                async with asyncio.timeout(30):
                    async for message in websocket:
                        data = json.loads(message)
                        print(f"Received: {data}")
                        
                        # Send a reaction to AI messages
                        if data.get("type") == "ai_message":
                            reaction = {
                                "type": "user_feedback",
                                "feedback": {
                                    "message_id": data.get("message_id"),
                                    "reaction": "like"
                                },
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            await websocket.send(json.dumps(reaction))
                            print(f"Sent reaction: {reaction}")
                            
            except asyncio.TimeoutError:
                print("Test completed after 30 seconds")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing AI Matchmaker WebSocket connection...")
    asyncio.run(test_websocket())