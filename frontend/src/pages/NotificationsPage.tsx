import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    ListItemSecondaryAction,
    Avatar,
    Button,
    Chip,
    IconButton,
    Tabs,
    Tab,
    CircularProgress,
    Alert,
    Divider,
    Menu,
    MenuItem
} from '@mui/material';
import {
    Favorite,
    Message,
    Star,
    Person,
    MarkEmailRead,
    MoreVert,
    Delete,
    Visibility
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';

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

const NotificationsPage: React.FC = () => {
    const navigate = useNavigate();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentTab, setCurrentTab] = useState(0);
    const [unreadCount, setUnreadCount] = useState(0);
    const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
    const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);

    useEffect(() => {
        loadNotifications();
    }, [currentTab]);

    const loadNotifications = async () => {
        try {
            setLoading(true);
            setError(null);

            const params = new URLSearchParams();
            params.append('limit', '50');
            if (currentTab === 1) {
                params.append('unread_only', 'true');
            }

            const response: NotificationListResponse = await api.get(`/api/v1/notifications/?${params}`);
            setNotifications(response.notifications);
            setUnreadCount(response.unread_count);
        } catch (err: any) {
            setError(err.message || 'Failed to load notifications');
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setCurrentTab(newValue);
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

    const handleMenuClick = (event: React.MouseEvent<HTMLElement>, notification: Notification) => {
        event.stopPropagation();
        setMenuAnchor(event.currentTarget);
        setSelectedNotification(notification);
    };

    const handleMenuClose = () => {
        setMenuAnchor(null);
        setSelectedNotification(null);
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

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - date.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
        return date.toLocaleDateString();
    };

    const filteredNotifications = currentTab === 1
        ? notifications.filter(n => !n.is_read)
        : notifications;

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    Notifications
                </Typography>
                {unreadCount > 0 && (
                    <Button
                        variant="outlined"
                        startIcon={<MarkEmailRead />}
                        onClick={handleMarkAllRead}
                    >
                        Mark All Read ({unreadCount})
                    </Button>
                )}
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} action={
                    <Button color="inherit" size="small" onClick={loadNotifications}>
                        Retry
                    </Button>
                }>
                    {error}
                </Alert>
            )}

            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                <Tabs value={currentTab} onChange={handleTabChange}>
                    <Tab label={`All (${notifications.length})`} />
                    <Tab label={`Unread (${unreadCount})`} />
                </Tabs>
            </Box>

            {/* Notifications list */}
            {filteredNotifications.length === 0 ? (
                <Box textAlign="center" py={8}>
                    <Typography variant="h6" gutterBottom>
                        {currentTab === 1 ? 'No unread notifications' : 'No notifications yet'}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        {currentTab === 1
                            ? 'All caught up! Check back later for new notifications.'
                            : 'We\'ll notify you when something interesting happens!'
                        }
                    </Typography>
                </Box>
            ) : (
                <List>
                    {filteredNotifications.map((notification, index) => (
                        <React.Fragment key={notification.id}>
                            <ListItem
                                button
                                onClick={() => handleNotificationClick(notification)}
                                sx={{
                                    bgcolor: notification.is_read ? 'transparent' : 'action.hover',
                                    borderRadius: 1,
                                    mb: 1,
                                    border: notification.is_read ? 'none' : '1px solid',
                                    borderColor: notification.is_read ? 'transparent' : 'primary.light'
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
                                                variant="subtitle1"
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
                                            {!notification.is_read && (
                                                <Chip
                                                    label="New"
                                                    color="primary"
                                                    size="small"
                                                    variant="outlined"
                                                />
                                            )}
                                        </Box>
                                    }
                                    secondary={
                                        <Box>
                                            <Typography
                                                variant="body1"
                                                color="text.secondary"
                                                sx={{
                                                    fontWeight: notification.is_read ? 'normal' : 'medium',
                                                    mb: 0.5
                                                }}
                                            >
                                                {notification.message}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                {formatDate(notification.created_at)}
                                                {notification.read_at && (
                                                    <> • Read {formatDate(notification.read_at)}</>
                                                )}
                                            </Typography>
                                        </Box>
                                    }
                                />

                                <ListItemSecondaryAction>
                                    <IconButton
                                        onClick={(e) => handleMenuClick(e, notification)}
                                        size="small"
                                    >
                                        <MoreVert />
                                    </IconButton>
                                </ListItemSecondaryAction>
                            </ListItem>
                            {index < filteredNotifications.length - 1 && <Divider />}
                        </React.Fragment>
                    ))}
                </List>
            )}

            {/* Context menu */}
            <Menu
                anchorEl={menuAnchor}
                open={Boolean(menuAnchor)}
                onClose={handleMenuClose}
            >
                {selectedNotification && !selectedNotification.is_read && (
                    <MenuItem onClick={async () => {
                        if (selectedNotification) {
                            await api.post(`/api/v1/notifications/${selectedNotification.id}/read`);
                            setNotifications(prev =>
                                prev.map(n =>
                                    n.id === selectedNotification.id
                                        ? { ...n, is_read: true, read_at: new Date().toISOString() }
                                        : n
                                )
                            );
                            setUnreadCount(prev => Math.max(0, prev - 1));
                        }
                        handleMenuClose();
                    }}>
                        <MarkEmailRead sx={{ mr: 1 }} />
                        Mark as Read
                    </MenuItem>
                )}
                {selectedNotification?.action_url && (
                    <MenuItem onClick={() => {
                        if (selectedNotification?.action_url) {
                            navigate(selectedNotification.action_url);
                        }
                        handleMenuClose();
                    }}>
                        <Visibility sx={{ mr: 1 }} />
                        View Details
                    </MenuItem>
                )}
            </Menu>
        </Container>
    );
};

export default NotificationsPage;