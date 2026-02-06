#!/usr/bin/env python3
"""
Test script for Gemini API Key feature.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🧪 Testing Gemini API Key Feature")
print("=" * 50)

# Test 1: Check if user_settings endpoint exists
print("\n1. Checking user_settings endpoint...")
try:
    from app.api.v1.endpoints import user_settings
    print("   ✅ user_settings module imported successfully")
    print(f"   ✅ Router: {user_settings.router}")
except Exception as e:
    print(f"   ❌ Failed to import user_settings: {e}")

# Test 2: Check if User model has gemini_api_key field
print("\n2. Checking User model...")
try:
    from app.models.user import User
    from sqlalchemy import inspect
    
    # Check if the column is defined in the model
    mapper = inspect(User)
    columns = [col.key for col in mapper.columns]
    
    if 'gemini_api_key' in columns:
        print("   ✅ User model has gemini_api_key field")
    else:
        print("   ⚠️  User model doesn't have gemini_api_key field yet")
        print(f"   Available columns: {columns}")
except Exception as e:
    print(f"   ❌ Error checking User model: {e}")

# Test 3: Check if UserAvatarAgent accepts user_api_key
print("\n3. Checking UserAvatarAgent...")
try:
    from app.services.ai_agent_service import UserAvatarAgent
    import inspect
    
    sig = inspect.signature(UserAvatarAgent.__init__)
    params = list(sig.parameters.keys())
    
    if 'user_api_key' in params:
        print("   ✅ UserAvatarAgent accepts user_api_key parameter")
    else:
        print("   ❌ UserAvatarAgent doesn't accept user_api_key parameter")
        print(f"   Parameters: {params}")
except Exception as e:
    print(f"   ❌ Error checking UserAvatarAgent: {e}")

# Test 4: Check if API routes are configured
print("\n4. Checking API routes...")
try:
    from app.api.v1.api import api_router
    
    # Get all routes
    routes = []
    for route in api_router.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
    
    settings_routes = [r for r in routes if 'settings' in r]
    if settings_routes:
        print(f"   ✅ Settings routes found: {settings_routes}")
    else:
        print("   ⚠️  No settings routes found")
        print(f"   Available routes: {routes[:10]}...")
except Exception as e:
    print(f"   ❌ Error checking API routes: {e}")

# Test 5: Check frontend SettingsPage
print("\n5. Checking frontend files...")
import os
settings_page_path = "../frontend/src/pages/SettingsPage.tsx"
if os.path.exists(settings_page_path):
    print(f"   ✅ SettingsPage.tsx exists")
else:
    print(f"   ❌ SettingsPage.tsx not found")

print("\n" + "=" * 50)
print("🎉 Feature test completed!")
print("\nNext steps:")
print("1. Run database migration: python run_migration.py")
print("2. Restart backend server")
print("3. Test frontend at http://localhost:3000/settings")