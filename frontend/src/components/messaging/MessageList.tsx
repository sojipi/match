import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Paper,
    TextField,
    IconButton,
    Typography,
    Avatar,
    CircularProgress,
    Alert,
    Divider
} from '@mui/material';
import {
    Send,
    Image as ImageIcon,
    EmojiEmotions
} from '@mui/icons-material';
import { api } from '../../utils/api';

interface Message {
    id: string;
    sender_id: string;
    sender_name: string;
    content: string;
    message_type: string;
    media_url?: string;
    is_read: boolean;
    created_at: string;
}

interface MessageListProps {
    matchId: string;
    currentUserId: string;
    otherUser: {
        id: string;
        name: string;
        photo_url?: string;
    };
}

const MessageList: React.FC<MessageListProps> = ({ matchId, currentUserId, otherUser }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        loadMessages();

        // Mark conversation as read when component mounts
        markAsRead();

        // Poll for new messages every 5 seconds
        const interval = setInterval(loadMessages, 5000);

        return () => clearInterval(interval);
    }, [matchId]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const loadMessages = async () => {
        try {
            setError(null);
            const data = await api.get(`/api/v1/messages/conversation/${matchId}`);
            setMessages(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load messages');
        } finally {
            setLoading(false);
        }
    };

    const markAsRead = async () => {
        try {
            await api.post(`/api/v1/messages/conversation/${matchId}/read`);
        } catch (err: any) {
            console.error('Failed to mark messages as read:', err);
        }
    };

    const handleSendMessage = async () => {
        if (!newMessage.trim() || sending) return;

        try {
            setSending(true);
            setError(null);

            const message = await api.post('/api/v1/messages/send', {
                recipient_id: otherUser.id,
                content: newMessage.trim(),
                message_type: 'text'
            });

            // Add message to list
            setMessages(prev => [...prev, message]);
            setNewMessage('');

            // Scroll to bottom
            scrollToBottom();
        } catch (err: any) {
            setError(err.message || 'Failed to send message');
        } finally {
            setSending(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const formatTime = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - date.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 1) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (diffDays < 7) {
            return date.toLocaleDateString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' });
        } else {
            return date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
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
        <Box display="flex" flexDirection="column" height="100%">
            {/* Header */}
            <Paper elevation={1} sx={{ p: 2, borderRadius: 0 }}>
                <Box display="flex" alignItems="center">
                    <Avatar
                        src={otherUser.photo_url}
                        alt={otherUser.name}
                        sx={{ mr: 2 }}
                    >
                        {otherUser.name.charAt(0)}
                    </Avatar>
                    <Typography variant="h6">
                        {otherUser.name}
                    </Typography>
                </Box>
            </Paper>

            {error && (
                <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Messages */}
            <Box
                flex={1}
                overflow="auto"
                p={2}
                sx={{
                    backgroundColor: '#f5f5f5',
                    display: 'flex',
                    flexDirection: 'column'
                }}
            >
                {messages.length === 0 ? (
                    <Box textAlign="center" py={4}>
                        <Typography variant="body1" color="text.secondary">
                            No messages yet. Start the conversation!
                        </Typography>
                    </Box>
                ) : (
                    messages.map((message, index) => {
                        const isCurrentUser = message.sender_id === currentUserId;
                        const showAvatar = index === 0 || messages[index - 1].sender_id !== message.sender_id;

                        return (
                            <Box
                                key={message.id}
                                display="flex"
                                justifyContent={isCurrentUser ? 'flex-end' : 'flex-start'}
                                mb={1}
                            >
                                {!isCurrentUser && showAvatar && (
                                    <Avatar
                                        src={otherUser.photo_url}
                                        alt={otherUser.name}
                                        sx={{ width: 32, height: 32, mr: 1 }}
                                    >
                                        {otherUser.name.charAt(0)}
                                    </Avatar>
                                )}
                                {!isCurrentUser && !showAvatar && (
                                    <Box width={32} mr={1} />
                                )}

                                <Paper
                                    elevation={1}
                                    sx={{
                                        p: 1.5,
                                        maxWidth: '70%',
                                        backgroundColor: isCurrentUser ? 'primary.main' : 'white',
                                        color: isCurrentUser ? 'white' : 'text.primary',
                                        borderRadius: 2
                                    }}
                                >
                                    <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
                                        {message.content}
                                    </Typography>
                                    <Typography
                                        variant="caption"
                                        sx={{
                                            display: 'block',
                                            mt: 0.5,
                                            opacity: 0.7,
                                            textAlign: 'right'
                                        }}
                                    >
                                        {formatTime(message.created_at)}
                                    </Typography>
                                </Paper>
                            </Box>
                        );
                    })
                )}
                <div ref={messagesEndRef} />
            </Box>

            {/* Input */}
            <Paper elevation={3} sx={{ p: 2, borderRadius: 0 }}>
                <Box display="flex" alignItems="center" gap={1}>
                    <IconButton size="small" disabled>
                        <ImageIcon />
                    </IconButton>
                    <IconButton size="small" disabled>
                        <EmojiEmotions />
                    </IconButton>
                    <TextField
                        fullWidth
                        placeholder="Type a message..."
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={sending}
                        multiline
                        maxRows={4}
                        variant="outlined"
                        size="small"
                    />
                    <IconButton
                        color="primary"
                        onClick={handleSendMessage}
                        disabled={!newMessage.trim() || sending}
                    >
                        {sending ? <CircularProgress size={24} /> : <Send />}
                    </IconButton>
                </Box>
            </Paper>
        </Box>
    );
};

export default MessageList;
