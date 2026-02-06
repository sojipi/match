# Quota Error Handling Improvements

## Overview
Enhanced the Gemini API quota error handling to immediately stop conversations and properly guide users to configure their own API keys.

## Changes Made

### 1. Backend - AI Agent Service (`backend/app/services/ai_agent_service.py`)

#### Problem:
- Quota errors were being caught and suppressed in multiple layers
- Conversation continued even after quota errors
- Fallback responses masked the real issue

#### Solution:
- **Removed error suppression in `generate_response()`**: Let quota errors propagate up
- **Updated `_generate_agentscope_response()`**: Re-raise `GEMINI_QUOTA_EXCEEDED` errors instead of falling back
- **Error propagation**: Quota errors now bubble up to the conversation loop where they can be properly handled

```python
# Before: Errors were caught and fallback was used
async def generate_response(...):
    try:
        return await self._generate_agentscope_response(...)
    except Exception as e:
        return await self._generate_fallback_response(...)  # Masked the error

# After: Quota errors propagate
async def generate_response(...):
    # Don't catch quota errors - let them propagate
    return await self._generate_agentscope_response(...)
```

### 2. Backend - WebSocket Manager (`backend/app/websocket/manager.py`)

#### Problem:
- Conversation loop continued after quota errors
- Session was not properly marked as terminated
- Only one error message was sent

#### Solution:
- **Mark session as TERMINATED**: When quota error occurs, update session status to `TERMINATED`
- **Send multiple notifications**: 
  1. `gemini_quota_exceeded` event with details
  2. `session_status_change` event to update UI state
- **Stop conversation immediately**: Exception breaks the conversation loop

```python
if "GEMINI_QUOTA_EXCEEDED" in error_str or "429" in error_str:
    # Mark session as terminated
    await db.execute(
        update(ConversationSession)
        .where(ConversationSession.id == session_id)
        .values(
            status=SessionStatus.TERMINATED.value,
            ended_at=datetime.utcnow()
        )
    )
    
    # Send quota exceeded notification
    await manager.broadcast_to_session({
        "type": "gemini_quota_exceeded",
        ...
    }, session_id)
    
    # Send session status change
    await manager.broadcast_to_session({
        "type": "session_status_change",
        "status": "terminated",
        "reason": "quota_exceeded",
        ...
    }, session_id)
```

### 3. Frontend - Live Matching Theater (`frontend/src/components/matching/LiveMatchingTheater.tsx`)

#### Problem:
- Dialog could be dismissed without action
- No clear path forward for users
- "Later" button was ambiguous

#### Solution:
- **Improved dialog UX**:
  - Added `disableEscapeKeyDown` to prevent accidental dismissal
  - Changed "Later" to "Close" for clarity
  - Added `autoFocus` to "Go to Settings" button
  - Updated text to explain both options
  
- **Automatic navigation**:
  - Clicking "Close" redirects to matches page
  - Clicking "Go to Settings" navigates to settings page
  - No way to stay on broken conversation page

```typescript
const handleCloseQuotaDialog = () => {
    setState(prev => ({ ...prev, showQuotaExceededDialog: false }));
    // Redirect to matches page when closing
    navigate('/matches');
};

const handleGoToSettings = () => {
    navigate('/settings');
};
```

## Error Flow

### When Quota Error Occurs:

1. **Gemini API returns 429 error**
   ```
   Error: 429 RESOURCE_EXHAUSTED
   Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests
   ```

2. **UserAvatarAgentScope.reply() catches and re-raises**
   ```python
   if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
       raise Exception("GEMINI_QUOTA_EXCEEDED")
   ```

3. **Error propagates through agent layers**
   - `_generate_agentscope_response()` re-raises quota errors
   - `generate_response()` doesn't catch them
   - Error reaches `start_ai_conversation()` loop

4. **Conversation loop breaks**
   - Exception caught in outer try/except
   - Conversation stops immediately
   - No more API calls attempted

5. **Session marked as terminated**
   ```python
   status=SessionStatus.TERMINATED.value
   ```

6. **Frontend receives two events**
   - `gemini_quota_exceeded`: Shows dialog
   - `session_status_change`: Updates session state

7. **User sees dialog with two options**
   - "Close": Returns to matches page
   - "Go to Settings": Navigates to API key configuration

## User Experience

### Before:
1. Quota error occurs
2. Conversation continues with fallback responses
3. User doesn't know what's wrong
4. Multiple failed API calls waste quota
5. Dialog appears but can be dismissed
6. User might stay on broken page

### After:
1. Quota error occurs
2. Conversation stops immediately ✅
3. Clear dialog explains the issue ✅
4. No more failed API calls ✅
5. Dialog requires action (can't dismiss with ESC) ✅
6. Both options navigate away from broken page ✅
7. "Go to Settings" is highlighted and focused ✅

## Testing Checklist

- [x] Quota error stops conversation immediately
- [x] Session marked as TERMINATED in database
- [x] Dialog appears with clear message
- [x] "Close" button redirects to matches page
- [x] "Go to Settings" button navigates to settings
- [x] Dialog cannot be dismissed with ESC key
- [x] "Go to Settings" button has auto-focus
- [x] No fallback responses after quota error
- [x] All TypeScript/Python compilation passes

## Benefits

1. **Immediate feedback**: Users know right away when quota is exceeded
2. **No wasted calls**: Conversation stops, preventing further quota usage
3. **Clear guidance**: Dialog explains the problem and solution
4. **Forced action**: Users must choose a path forward
5. **Better UX**: No confusing fallback responses or broken states
6. **Proper state management**: Session correctly marked as terminated

## Related Files

- `backend/app/services/ai_agent_service.py` - Error propagation
- `backend/app/websocket/manager.py` - Session termination and notifications
- `frontend/src/components/matching/LiveMatchingTheater.tsx` - Dialog and navigation
- `frontend/src/pages/SettingsPage.tsx` - API key configuration (English)

## Next Steps (Optional)

1. Add retry logic with exponential backoff for transient errors
2. Show remaining quota to users before starting conversations
3. Add API key validation before saving in settings
4. Implement usage tracking per user
5. Add admin dashboard for monitoring quota usage
