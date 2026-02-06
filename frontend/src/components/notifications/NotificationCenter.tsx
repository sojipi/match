import React, { useState, useEffect } from 'react';
import {
    Box,
    IconButton,
    Badge,
    Popover,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    ListItemSecondaryAction,
    Avatar,
    Typography,
    Button,
    Divider,
    Chip,
    CircularProgress,
    Alert
} from '@mui/material';
import {
    Notifications,
    NotificationsNone,
    Favorite,
    Message,
    Star,
    Person,
    CheckCircle,
    MarkEmailRead
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { api } from '../../utils/api';

interface NotificationUser {
    id: string;
    name: string;
    photo_url?: string;
}

interface Notification {
    id: string;
    type: string;
    title: string;
    message: string;
    is_read: boolean;
    created_at: string;
    read_at?: string;
    action_url?: string;
    data: Record<string, any>;
    related_user?: NotificationUser;
}

interface NotificationListResponse {
    notifications: Notification[];
    unread_count: number;
    total_count: number;
}

const NotificationCenter: React.FC = () => {
    const navigate = useNavigate();
    const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const open = Boolean(anchorEl);

    useEffect(() => {
        // Load unread count on mount
        loadUnreadCount();

        // Set up polling for new notifications
        const interval = setInterval(loadUnreadCount, 30000); // Every 30 seconds

        return () => clearInterval(interval);
    }, []);

    const loadUnreadCount = async () => {
        try {
            const response = await api.get('/api/v1/notifications/unread-count');
            setUnreadCount(response.unread_count);
        } catch (err: any) {
            console.error('Failed to load unread count:', err);
        }
    };

    const loadNotifications = async () => {
        try {
            setLoading(true);
            setError(null);

            const response: NotificationListResponse = await api.get('/api/v1/notifications/?limit=20');
            setNotifications(response.notifications);
            setUnreadCount(response.unread_count);
        } catch (err: any) {
            setError(err.message || 'Failed to load notifications');
        } finally {
            setLoading(false);
        }
    };

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
        if (notifications.length === 0) {
            loadNotifications();
        }
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleNotificationClick = async (notification: Notification) => {
        // Mark as read if not already read
        if (!notification.is_read) {
            try {
                await api.post(`/api/v1/notifications/${notification.id}/read`);

                // Update local state
                setNotifications(prev =>
                    prev.map(n =>
                        n.id === notification.id
                            ? { ...n, is_read: true, read_at: new Date().toISOString() }
                            : n
                    )
                );
                setUnreadCount(prev => Math.max(0, prev - 1));
            } catch (err: any) {
                console.error('Failed to mark notification as read:', err);
            }
        }

        // Navigate to action URL if available
        if (notification.action_url) {
            navigate(notification.action_url);
        }

        handleClose();
    };

    const handleMarkAllRead = async () => {
        try {
            await api.post('/api/v1/notifications/read-all');

            // Update local state
            setNotifications(prev =>
                prev.map(n => ({
                    ...n,
                    is_read: true,
                    read_at: new Date().toISOString()
                }))
            );
            setUnreadCount(0);
        } catch (err: any) {
            setError(err.message || 'Failed to mark all notifications as read');
        }
    };

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'match':
            case 'mutual_match':
                return <Favorite color="error" />;
            case 'message':
                return <Message color="primary" />;
            case 'like':
            case 'super_like':
                return <Favorite color="secondary" />;
            case 'profile_view':
                return <Person color="action" />;
            default:
                return <Star color="action" />;
        }
    };

    const getNotificationColor = (type: string) => {
        switch (type) {
            case 'mutual_match':
                return 'error';
            case 'match':
                return 'primary';
            case 'like':
            case 'super_like':
                return 'secondary';
            case 'message':
                return 'info';
            default:
                return 'default';
        }
    };

    const formatTimeAgo = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - date.getTime());
        const diffMinutes = Math.ceil(diffTime / (1000 * 60));
        const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffMinutes < 60) {
            return `${diffMinutes}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return date.toLocaleDateString();
        }
    };

    return (
        <>
            <IconButton
                color="inherit"
                onClick={handleClick}
                aria-label="notifications"
            >
                <Badge badgeContent={unreadCount} color="error">
                    {unreadCount > 0 ? <Notifications /> : <NotificationsNone />}
                </Badge>
            </IconButton>

            <Popover
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                }}
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                }}
                PaperProps={{
                    sx: { width: 400, maxHeight: 600 }
                }}
            >
                <Box p={2}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h6">
                            Notifications
                        </Typography>
                        {unreadCount > 0 && (
                            <Button
                                size="small"
                                startIcon={<MarkEmailRead />}
                                onClick={handleMarkAllRead}
                            >
                                Mark all read
                            </Button>
                        )}
                    </Box>

                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    {loading ? (
                        <Box display="flex" justifyContent="center" py={4}>
                            <CircularProgress />
                        </Box>
                    ) : notifications.length === 0 ? (
                        <Box textAlign="center" py={4}>
                            <NotificationsNone sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                            <Typography variant="body1" color="text.secondary">
                                No notifications yet
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                We'll notify you when something interesting happens!
                            </Typography>
                        </Box>
                    ) : (
                        <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                            {notifications.map((notification, index) => (
                                <React.Fragment key={notification.id}>
                                    <ListItem
                                        button
                                        onClick={() => handleNotificationClick(notification)}
                                        sx={{
                                            bgcolor: notification.is_read ? 'transparent' : 'action.hover',
                                            borderRadius: 1,
                                            mb: 0.5
                                        }}
                                    >
                                        <ListItemAvatar>
                                            {notification.related_user ? (
                                                <Avatar
                                                    src={notification.related_user.photo_url}
                                                    alt={notification.related_user.name}
                                                >
                                                    {notification.related_user.name.charAt(0)}
                                                </Avatar>
                                            ) : (
                                                <Avatar>
                                                    {getNotificationIcon(notification.type)}
                                                </Avatar>
                                            )}
                                        </ListItemAvatar>

                                        <ListItemText
                                            primary={
                                                <Box display="flex" alignItems="center" gap={1}>
                                                    <Typography
                                                        variant="subtitle2"
                                                        sx={{
                                                            fontWeight: notification.is_read ? 'normal' : 'bold'
                                                        }}
                                                    >
                                                        {notification.title}
                                                    </Typography>
                                                    {notification.type === 'mutual_match' && (
                                                        <Chip
                                                            label="Match!"
                                                            color="error"
                                                            size="small"
                                                        />
                                                    )}
                                                </Box>
                                            }
                                            secondary={
                                                <Box>
                                                    <Typography
                                                        variant="body2"
                                                        color="text.secondary"
                                                        sx={{
                                                            fontWeight: notification.is_read ? 'normal' : 'medium'
                                                        }}
                                                    >
                                                        {notification.message}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary">
                                                        {formatTimeAgo(notification.created_at)}
                                                    </Typography>
                                                </Box>
                                            }
                                        />

                                        <ListItemSecondaryAction>
                                            {!notification.is_read && (
                                                <Box
                                                    sx={{
                                                        width: 8,
                                                        height: 8,
                                                        borderRadius: '50%',
                                                        bgcolor: 'primary.main'
                                                    }}
                                                />
                                            )}
                                        </ListItemSecondaryAction>
                                    </ListItem>
                                    {index < notifications.length - 1 && <Divider />}
                                </React.Fragment>
                            ))}
                        </List>
                    )}

                    {notifications.length > 0 && (
                        <Box textAlign="center" mt={2}>
                            <Button
                                variant="text"
                                onClick={() => {
                                    navigate('/notifications');
                                    handleClose();
                                }}
                            >
                                View All Notifications
                            </Button>
                        </Box>
                    )}
                </Box>
            </Popover>
        </>
    );
};

export default NotificationCenter;