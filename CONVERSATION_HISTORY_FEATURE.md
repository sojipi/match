# Conversation History Feature

## Overview
Added functionality to view historical AI conversation messages that are stored in the database.

## Implementation

### Backend Changes

#### 1. Updated Sessions API (`backend/app/api/v1/endpoints/sessions.py`)

**Endpoint**: `GET /api/v1/sessions/{session_id}/messages`

**Features**:
- Fetches real conversation messages from database (replaced mock data)
- Includes authentication and authorization checks
- Supports pagination (limit and offset parameters)
- Returns session metadata along with messages
- Verifies user has access to the session

**Response Format**:
```json
{
  "messages": [
    {
      "message_id": "uuid",
      "sender_type": "user_avatar",
      "sender_name": "Alex's Avatar",
      "content": "Message content",
      "timestamp": "2026-02-06T14:00:00",
      "emotion_indicators": ["friendly", "curious"]
    }
  ],
  "total_count": 25,
  "has_more": false,
  "session": {
    "session_id": "uuid",
    "status": "completed",
    "started_at": "2026-02-06T14:00:00",
    "ended_at": "2026-02-06T14:30:00"
  }
}
```

### Frontend Changes

#### 1. New Page: ConversationHistoryPage (`frontend/src/pages/ConversationHistoryPage.tsx`)

**Features**:
- Displays all messages from a conversation session
- Shows sender avatars (AI avatar vs matchmaker)
- Displays emotion indicators as chips
- Shows session metadata (status, start/end times)
- Formats timestamps in local time
- Includes back button to return to matches
- Loading and error states

**UI Components**:
- Message list with avatars
- Sender name and timestamp
- Message content
- Emotion indicator chips
- Session status chip
- Total message count

#### 2. Updated App Routing (`frontend/src/App.tsx`)

**New Route**: `/conversation/:sessionId`
- Protected route requiring authentication
- Wrapped in AppLayout
- Displays ConversationHistoryPage component

#### 3. Updated MatchesPage (`frontend/src/pages/MatchesPage.tsx`)

**New Features**:
- Added "View Conversation History" menu item
- Added History icon import
- New handler: `handleViewConversationHistory(matchId)`
- Navigates to `/conversation/{matchId}` when clicked

**Menu Structure**:
```
Match Options Menu:
├── View Compatibility Report
├── View Conversation History  ← NEW
├── Start Conversation
├── ─────────────────
├── Block User
└── Report User
```

## User Flow

1. **Access History**:
   - User goes to Matches page
   - Clicks the three-dot menu (⋮) on a match card
   - Selects "View Conversation History"

2. **View Messages**:
   - System navigates to `/conversation/{sessionId}`
   - Loads all messages from that session
   - Displays messages in chronological order
   - Shows sender information and timestamps

3. **Navigate Back**:
   - User clicks back arrow
   - Returns to Matches page

## Data Flow

```
Frontend                    Backend                     Database
   │                           │                            │
   ├─ GET /api/v1/sessions/   │                            │
   │  {sessionId}/messages ───>│                            │
   │                           ├─ Verify user access        │
   │                           ├─ Query messages ──────────>│
   │                           │<─ Return messages ─────────┤
   │<─ Return JSON response ───┤                            │
   │                           │                            │
   └─ Display messages         │                            │
```

## Security

- ✅ Authentication required (JWT token)
- ✅ Authorization check (user must be part of the session)
- ✅ Protected routes on frontend
- ✅ Session ownership verification

## Features

### Message Display
- **Sender identification**: Different avatars for AI avatars vs matchmaker
- **Color coding**: Primary color for avatars, secondary for matchmaker
- **Timestamps**: Formatted in local timezone
- **Emotion indicators**: Displayed as chips below messages
- **Message count**: Shows total number of messages

### Session Information
- **Status chip**: Shows session status (completed, active, etc.)
- **Start time**: When conversation began
- **End time**: When conversation ended
- **Duration**: Can be calculated from start/end times

## API Parameters

### GET /api/v1/sessions/{session_id}/messages

**Path Parameters**:
- `session_id` (required): UUID of the conversation session

**Query Parameters**:
- `limit` (optional, default: 50): Maximum number of messages to return
- `offset` (optional, default: 0): Number of messages to skip (for pagination)

**Headers**:
- `Authorization: Bearer {token}` (required)

## Error Handling

### Backend Errors:
- **404**: Session not found
- **403**: User doesn't have access to this session
- **500**: Server error loading messages

### Frontend Handling:
- Loading spinner while fetching
- Error alert with message
- Back button available even on error
- Graceful handling of empty message lists

## Future Enhancements

1. **Pagination**: Load more messages on scroll
2. **Search**: Search within conversation messages
3. **Export**: Download conversation as PDF or text
4. **Filters**: Filter by sender type or emotion
5. **Session List**: Show all sessions for a match
6. **Real-time Updates**: Live updates if conversation is ongoing
7. **Message Actions**: React to messages, bookmark important ones
8. **Analytics**: Show conversation statistics and insights

## Testing

### Manual Testing Checklist:
- [ ] Can access conversation history from matches page
- [ ] Messages display in correct order
- [ ] Sender names and avatars show correctly
- [ ] Timestamps are formatted properly
- [ ] Emotion indicators display as chips
- [ ] Session metadata shows correctly
- [ ] Back button returns to matches
- [ ] Error handling works for invalid session IDs
- [ ] Authorization prevents viewing other users' conversations
- [ ] Loading state displays while fetching

## Files Modified

### Backend:
- `backend/app/api/v1/endpoints/sessions.py` - Implemented real message fetching

### Frontend:
- `frontend/src/pages/ConversationHistoryPage.tsx` - New page (created)
- `frontend/src/App.tsx` - Added route
- `frontend/src/pages/MatchesPage.tsx` - Added menu item and handler

## Related Features

- AI Conversation Sessions (WebSocket)
- Match History
- Compatibility Reports
- User Profiles

## Notes

- Currently uses match ID as session ID (temporary)
- In production, should fetch the latest or specific session ID for a match
- Messages are loaded all at once (consider pagination for long conversations)
- Emotion indicators are stored as JSON array in database
