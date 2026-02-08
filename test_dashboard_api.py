"""
Test script for Dashboard API endpoint
Tests the /api/v1/users/dashboard endpoint
"""
import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
DASHBOARD_ENDPOINT = f"{BASE_URL}/api/v1/users/dashboard"

# You need to provide a valid JWT token
# Get this from your browser's developer tools after logging in
TOKEN = "YOUR_JWT_TOKEN_HERE"  # Replace with actual token


async def test_dashboard_api():
    """Test the dashboard API endpoint"""
    
    print("=" * 60)
    print("Testing Dashboard API")
    print("=" * 60)
    print(f"Endpoint: {DASHBOARD_ENDPOINT}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("\n📡 Sending GET request...")
            response = await client.get(DASHBOARD_ENDPOINT, headers=headers)
            
            print(f"\n✅ Status Code: {response.status_code}")
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCCESS! Dashboard data received:")
                print("-" * 60)
                print(json.dumps(data, indent=2, default=str))
                print("-" * 60)
                
                # Validate response structure
                print("\n🔍 Validating response structure...")
                required_fields = ["stats", "activity_feed", "compatibility_trends", "recommendations", "profile_completeness"]
                
                for field in required_fields:
                    if field in data:
                        print(f"  ✓ {field}: Present")
                        if field == "stats":
                            stats = data["stats"]
                            print(f"    - Total Matches: {stats.get('total_matches', 0)}")
                            print(f"    - Active Conversations: {stats.get('active_conversations', 0)}")
                            print(f"    - AI Sessions: {stats.get('ai_sessions', 0)}")
                            print(f"    - Compatibility Reports: {stats.get('compatibility_reports', 0)}")
                    else:
                        print(f"  ✗ {field}: MISSING")
                
                print("\n✅ Test PASSED!")
                return True
                
            elif response.status_code == 401:
                print("\n❌ UNAUTHORIZED - Invalid or expired token")
                print("Please update the TOKEN variable with a valid JWT token")
                print("You can get this from your browser's developer tools after logging in")
                return False
                
            elif response.status_code == 500:
                print("\n❌ SERVER ERROR")
                print("Response:")
                try:
                    error_data = response.json()
                    print(json.dumps(error_data, indent=2))
                except:
                    print(response.text)
                return False
                
            else:
                print(f"\n❌ Unexpected status code: {response.status_code}")
                print("Response:")
                print(response.text)
                return False
                
        except httpx.ConnectError:
            print("\n❌ CONNECTION ERROR")
            print(f"Could not connect to {BASE_URL}")
            print("Make sure the backend server is running on port 8000")
            return False
            
        except Exception as e:
            print(f"\n❌ ERROR: {type(e).__name__}")
            print(f"Message: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def test_without_auth():
    """Test the endpoint without authentication (should fail)"""
    print("\n" + "=" * 60)
    print("Testing without authentication (should return 401)")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(DASHBOARD_ENDPOINT)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 401:
                print("✅ Correctly returns 401 Unauthorized")
                return True
            else:
                print(f"❌ Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False


async def main():
    """Run all tests"""
    print("\n🚀 Starting Dashboard API Tests\n")
    
    # Test without auth first
    await test_without_auth()
    
    # Test with auth
    if TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("\n" + "=" * 60)
        print("⚠️  WARNING: No JWT token provided")
        print("=" * 60)
        print("\nTo test with authentication:")
        print("1. Log in to the application in your browser")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Application/Storage > Local Storage")
        print("4. Copy the 'token' value")
        print("5. Update the TOKEN variable in this script")
        print("6. Run the script again")
        print("\nSkipping authenticated test...")
    else:
        result = await test_dashboard_api()
        if result:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Tests failed!")


if __name__ == "__main__":
    asyncio.run(main())
