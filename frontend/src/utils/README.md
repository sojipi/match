# API Client Usage Guide

## Overview

The API client (`api.ts`) provides a centralized way to make authenticated HTTP requests with automatic token refresh handling.

## Features

- **Automatic Authentication**: Automatically adds Bearer token to requests
- **Token Refresh**: Automatically refreshes expired tokens and retries failed requests
- **Error Handling**: Consistent error handling across all API calls
- **Type Safety**: Full TypeScript support with generic types

## Basic Usage

```typescript
import apiClient from '../utils/api';

// GET request
const user = await apiClient.get('/api/v1/users/me');

// POST request
const newMatch = await apiClient.post('/api/v1/matches', {
    user2_id: 'some-uuid',
});

// PUT request
const updatedProfile = await apiClient.put('/api/v1/users/profile', {
    bio: 'Updated bio',
});

// PATCH request
const partialUpdate = await apiClient.patch('/api/v1/users/settings', {
    notification_preferences: { email: true },
});

// DELETE request
await apiClient.delete('/api/v1/matches/some-uuid');
```

## Advanced Usage

### Skip Authentication

For public endpoints that don't require authentication:

```typescript
const publicData = await apiClient.get('/api/v1/public/stats', {
    skipAuth: true,
});
```

### Custom Headers

```typescript
const data = await apiClient.post('/api/v1/upload', formData, {
    headers: {
        'Content-Type': 'multipart/form-data',
    },
});
```

### Type Safety

Use TypeScript generics for type-safe responses:

```typescript
interface User {
    id: string;
    email: string;
    username: string;
}

const user = await apiClient.get<User>('/api/v1/users/me');
// user is now typed as User
```

## How Token Refresh Works

1. When a request receives a 401 Unauthorized response
2. The client automatically calls `/api/v1/auth/refresh` with the refresh token
3. If successful, the original request is retried with the new access token
4. If refresh fails, the user is redirected to the login page

## Migration from Fetch

### Before (using fetch directly)

```typescript
const response = await fetch('/api/v1/users/me', {
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    },
});

if (!response.ok) {
    throw new Error('Request failed');
}

const user = await response.json();
```

### After (using API client)

```typescript
const user = await apiClient.get('/api/v1/users/me');
```

## Error Handling

The API client throws errors for failed requests. Use try-catch to handle them:

```typescript
try {
    const user = await apiClient.get('/api/v1/users/me');
    console.log('User:', user);
} catch (error) {
    console.error('Failed to fetch user:', error.message);
    // Handle error (show notification, etc.)
}
```

## Integration with Redux

The API client automatically updates the Redux store when tokens are refreshed. This is configured in `main.tsx`:

```typescript
window.dispatchTokenUpdate = (token: string) => {
    store.dispatch(updateToken(token));
};
```

## Best Practices

1. **Always use the API client** instead of fetch for authenticated requests
2. **Use TypeScript generics** for type-safe responses
3. **Handle errors appropriately** with try-catch blocks
4. **Use skipAuth** only for truly public endpoints
5. **Keep the base URL empty** (defaults to same origin) unless calling external APIs
