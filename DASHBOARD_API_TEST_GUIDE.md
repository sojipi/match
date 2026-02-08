# Dashboard API Testing Guide

## Problem

The Dashboard API endpoint (`/api/v1/users/dashboard`) is returning 500 errors.

## Test Scripts

I've created two test scripts to help diagnose and verify the issue:

### 1. Direct Database Query Test (Recommended First)

**File**: `test_dashboard_queries.py`

This script tests the SQL queries directly without going through the API, which helps isolate whether the problem is in the queries or elsewhere.

**How to run**:
```bash
# From the project root directory
python test_dashboard_queries.py
```

**What it tests**:
- ✅ Mutual matches count query
- ✅ Active conversations count query
- ✅ Compatibility reports count query
- ✅ AI sessions count query
- ✅ Unread notifications count query

**Expected output**:
```
🚀 Starting Dashboard Query Tests

============================================================
Testing Dashboard Database Queries
============================================================

1. Finding a test user...
✅ Found user: user@example.com (ID: xxx-xxx-xxx)

2. Testing mutual matches query...
✅ Total mutual matches: 0

3. Testing active conversations query...
✅ Active conversations: 0

4. Testing compatibility reports query...
✅ Compatibility reports: 0

5. Testing AI sessions query...
✅ AI sessions: 0

6. Testing unread notifications query...
✅ Unread notifications: 0

============================================================
✅ ALL QUERIES PASSED!
============================================================
```

---

### 2. API Endpoint Test

**File**: `test_dashboard_api.py`

This script tests the actual HTTP API endpoint.

**How to run**:

1. First, get your JWT token:
   - Log in to the application in your browser
   - Open Developer Tools (F12)
   - Go to Application/Storage > Local Storage
   - Copy the 'token' value

2. Edit `test_dashboard_api.py` and replace:
   ```python
   TOKEN = "YOUR_JWT_TOKEN_HERE"
   ```
   with your actual token

3. Run the script:
   ```bash
   python test_dashboard_api.py
   ```

**What it tests**:
- ✅ Authentication (401 without token)
- ✅ API endpoint response (200 with valid token)
- ✅ Response structure validation
- ✅ Response time measurement

---

## Current Issue Analysis

Based on the error message:
```
invalid input value for enum matchstatus: "mutual"
```

### Root Cause

The issue was that I incorrectly added `.value` to enum comparisons. In SQLAlchemy with PostgreSQL enums:

- ✅ **CORRECT**: `Match.status == MatchStatus.MUTUAL` (use enum object)
- ❌ **WRONG**: `Match.status == MatchStatus.MUTUAL.value` (don't use .value)

### Fix Applied

Reverted all enum comparisons back to using enum objects directly:

```python
# Correct usage
Match.status == MatchStatus.MUTUAL
MatchSession.status == MatchSessionStatus.COMPLETED
```

### Exception

`ConversationSession.status` is a `String` column, not an enum, so it uses string comparison:
```python
ConversationSession.status == "active"  # Correct - it's a String column
```

---

## How to Verify the Fix

### Step 1: Run Database Query Test
```bash
python test_dashboard_queries.py
```

If this passes, the queries are working correctly.

### Step 2: Restart Backend Server
```bash
# Stop the current server (Ctrl+C)
# Then restart it
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Test in Browser
1. Navigate to http://localhost:3000/dashboard
2. Check browser console for errors
3. Check backend logs for errors

### Step 4: Run API Test (Optional)
```bash
# After getting your JWT token
python test_dashboard_api.py
```

---

## Expected Dashboard Response

When working correctly, the API should return:

```json
{
  "stats": {
    "total_matches": 0,
    "active_conversations": 0,
    "compatibility_reports": 0,
    "ai_sessions": 0,
    "unread_notifications": 0
  },
  "activity_feed": [],
  "compatibility_trends": [],
  "recommendations": [],
  "profile_completeness": 0.5
}
```

---

## Troubleshooting

### If database query test fails:

1. **Check database connection**:
   - Verify PostgreSQL is running
   - Check `.env` file has correct DATABASE_URL

2. **Check if tables exist**:
   ```bash
   # Connect to PostgreSQL
   psql -U postgres -d matchmaking
   
   # List tables
   \dt
   
   # Check if matches table exists
   \d matches
   ```

3. **Check if user exists**:
   ```sql
   SELECT id, email FROM users LIMIT 1;
   ```

### If API test fails with 401:

- Token expired - get a new one
- Token format wrong - should be just the token string, no "Bearer " prefix in the TOKEN variable

### If API test fails with 500:

- Check backend logs for detailed error
- Run database query test to isolate the issue

---

## Files Modified

- `backend/app/api/v1/endpoints/users.py` - Fixed enum comparisons (removed `.value`)

## Status

✅ Fixed - Enum comparisons corrected
⏳ Pending verification with test scripts

---

**Date**: 2026-02-08
**Issue**: Enum comparison errors in dashboard queries
**Resolution**: Use enum objects directly, not `.value`
