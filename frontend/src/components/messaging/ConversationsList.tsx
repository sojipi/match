import React, { useState, useEffect } from 'react';
import {
    Box,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    ListItemButton,
    Avatar,
    Typography,
    Badge,
    CircularProgress,
    Alert,
    IconButton,
    Menu,
    MenuItem,
    Divider
} from '@mui/material';
import {
    MoreVert,
    Archive,
    Unarchive,
    VolumeOff,
    VolumeUp
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { api } from '../../utils/api';

interface Conversation {
    id: string;
    match_id: string;
    other_user: {
        id: string;
        name: string;
        photo_url?: string;
    };
    last_message: {
        content: string;
        sender_id: string;
        created_at: string;
    } | null;
    unread_count: number;
    is_muted: boolean;
    is_archived: boolean;
    last_message_at: string | null;
    created_at: string;
}

interface ConversationsListProps {
    onSelectConversation?: (conversation: Conversation) => void;
}

const ConversationsList: React.FC<ConversationsListProps> = ({ onSelectConversation }) => {
    const navigate = useNavigate();
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);

    useEffect(() => {
        loadConversations();

        // Poll for new messages every 10 seconds
        const interval = setInterval(loadConversations, 10000);

        return () => clearInterval(interval);
    }, []);

    const loadConversations = async () => {
        try {
            setError(null);
            const data = await api.get('/api/v1/messages/conversations');
            setConversations(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load conversations');
        } finally {
            setLoading(false);
        }
    };

    const handleConversationClick = (conversation: Conversation) => {
        if (onSelectConversation) {
            onSelectConversation(conversation);
        } else {
            navigate(`/messages/${conversation.match_id}`);
        }
    };

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, conversation: Conversation) => {
        event.stopPropagation();
        setAnchorEl(event.currentTarget);
        setSelectedConversation(conversation);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedConversation(null);
    };

    const handleArchive = async () => {
        if (!selectedConversation) return;

        try {
            if (selectedConversation.is_archived) {
                await api.post(`/api/v1/messages/conversation/${selectedConversation.match_id}/unarchive`);
            } else {
                await api.post(`/api/v1/messages/conversation/${selectedConversation.match_id}/archive`);
            }

            await loadConversations();
        } catch (err: any) {
            setError(err.message || 'Failed to archive conversation');
        } finally {
            handleMenuClose();
        }
    };

    const handleMute = async () => {
        if (!selectedConversation) return;

        try {
            if (selectedConversation.is_muted) {
                await api.post(`/api/v1/messages/conversation/${selectedConversation.match_id}/unmute`);
            } else {
                await api.post(`/api/v1/messages/conversation/${selectedConversation.match_id}/mute`);
            }

            await loadConversations();
        } catch (err: any) {
            setError(err.message || 'Failed to mute conversation');
        } finally {
            handleMenuClose();
        }
    };

    const formatTime = (dateString: string | null) => {
        if (!dateString) return '';

        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - date.getTime());
        const diffMinutes = Math.ceil(diffTime / (1000 * 60));
        const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffMinutes < 60) {
            return `${diffMinutes}m`;
        } else if (diffHours < 24) {
            return `${diffHours}h`;
        } else if (diffDays < 7) {
            return `${diffDays}d`;
        } else {
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            {error && (
                <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {conversations.length === 0 ? (
                <Box textAlign="center" py={4} px={2}>
                    <Typography variant="body1" color="text.secondary">
                        No conversations yet
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Start matching to begin conversations!
                    </Typography>
                </Box>
            ) : (
                <List sx={{ p: 0 }}>
                    {conversations.map((conversation, index) => (
                        <React.Fragment key={conversation.id}>
                            <ListItemButton
                                onClick={() => handleConversationClick(conversation)}
                                sx={{
                                    backgroundColor: conversation.unread_count > 0 ? 'action.hover' : 'transparent'
                                }}
                            >
                                <ListItemAvatar>
                                    <Badge
                                        badgeContent={conversation.unread_count}
                                        color="error"
                                        overlap="circular"
                                    >
                                        <Avatar
                                            src={conversation.other_user.photo_url}
                                            alt={conversation.other_user.name}
                                        >
                                            {conversation.other_user.name.charAt(0)}
                                        </Avatar>
                                    </Badge>
                                </ListItemAvatar>

                                <ListItemText
                                    primary={
                                        <Box display="flex" justifyContent="space-between" alignItems="center">
                                            <Typography
                                                variant="subtitle1"
                                                sx={{
                                                    fontWeight: conversation.unread_count > 0 ? 'bold' : 'normal'
                                                }}
                                            >
                                                {conversation.other_user.name}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                {formatTime(conversation.last_message_at)}
                                            </Typography>
                                        </Box>
                                    }
                                    secondary={
                                        <Box display="flex" alignItems="center" gap={0.5}>
                                            {conversation.is_muted && (
                                                <VolumeOff sx={{ fontSize: 14, color: 'text.secondary' }} />
                                            )}
                                            <Typography
                                                variant="body2"
                                                color="text.secondary"
                                                sx={{
                                                    fontWeight: conversation.unread_count > 0 ? 'medium' : 'normal',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    whiteSpace: 'nowrap'
                                                }}
                                            >
                                                {conversation.last_message?.content || 'No messages yet'}
                                            </Typography>
                                        </Box>
                                    }
                                />

                                <IconButton
                                    edge="end"
                                    onClick={(e) => handleMenuOpen(e, conversation)}
                                >
                                    <MoreVert />
                                </IconButton>
                            </ListItemButton>
                            {index < conversations.length - 1 && <Divider />}
                        </React.Fragment>
                    ))}
                </List>
            )}

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
            >
                <MenuItem onClick={handleMute}>
                    {selectedConversation?.is_muted ? (
                        <>
                            <VolumeUp sx={{ mr: 1 }} />
                            Unmute
                        </>
                    ) : (
                        <>
                            <VolumeOff sx={{ mr: 1 }} />
                            Mute
                        </>
                    )}
                </MenuItem>
                <MenuItem onClick={handleArchive}>
                    {selectedConversation?.is_archived ? (
                        <>
                            <Unarchive sx={{ mr: 1 }} />
                            Unarchive
                        </>
                    ) : (
                        <>
                            <Archive sx={{ mr: 1 }} />
                            Archive
                        </>
                    )}
                </MenuItem>
            </Menu>
        </Box>
    );
};

export default ConversationsList;
