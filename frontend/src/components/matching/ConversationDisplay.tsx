/**
 * Conversation Display - Shows AI avatar messages in theater style
 */
import React, { useState, useRef, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Avatar,
    Chip,
    IconButton,
    Tooltip,
    Badge,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Fade,
    Zoom
} from '@mui/material';
import {
    Favorite,
    ThumbUp,
    EmojiEmotions,
    Warning,
    Star,
    Psychology,
    TrendingUp,
    MoreVert
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';

import { ConversationMessage, UserReaction } from '../../types/matching';

interface ConversationDisplayProps {
    messages: ConversationMessage[];
    userReactions: UserReaction[];
    onReaction: (messageId: string, reactionType: string) => void;
    selectedMessage?: string;
}

const ConversationDisplay: React.FC<ConversationDisplayProps> = ({
    messages,
    userReactions,
    onReaction,
    selectedMessage
}) => {
    const [reactionMenuAnchor, setReactionMenuAnchor] = useState<null | HTMLElement>(null);
    const [selectedMessageId, setSelectedMessageId] = useState<string>('');
    const messagesContainerRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (messagesContainerRef.current) {
            messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
    }, [messages]);

    const handleReactionClick = (event: React.MouseEvent<HTMLElement>, messageId: string) => {
        setReactionMenuAnchor(event.currentTarget);
        setSelectedMessageId(messageId);
    };

    const handleReactionSelect = (reactionType: string) => {
        if (selectedMessageId) {
            onReaction(selectedMessageId, reactionType);
        }
        setReactionMenuAnchor(null);
        setSelectedMessageId('');
    };

    const getMessageReactions = (messageId: string) => {
        return userReactions.filter(reaction => reaction.message_id === messageId);
    };

    const getEmotionColor = (emotion: string): string => {
        const emotionColors: Record<string, string> = {
            excited: '#FF6B6B',
            happy: '#4ECDC4',
            curious: '#45B7D1',
            warm: '#FFA07A',
            passionate: '#FF1744',
            concerned: '#FF9800',
            surprised: '#9C27B0',
            thoughtful: '#607D8B',
            friendly: '#4CAF50',
            engaged: '#2196F3'
        };
        return emotionColors[emotion] || '#757575';
    };

    const getSenderAvatar = (message: ConversationMessage) => {
        const isUserAvatar = message.sender_type === 'user_avatar';
        const avatarColor = message.sender_name.includes('Alex') ? '#1976d2' : '#d32f2f';

        return (
            <Avatar
                sx={{
                    bgcolor: avatarColor,
                    width: 48,
                    height: 48,
                    border: message.is_highlighted ? '3px solid #FFD700' : 'none',
                    boxShadow: message.is_highlighted ? '0 0 20px rgba(255, 215, 0, 0.5)' : 'none'
                }}
            >
                {message.sender_name.charAt(0)}
            </Avatar>
        );
    };

    const MessageBubble: React.FC<{ message: ConversationMessage; index: number }> = ({ message, index }) => {
        const reactions = getMessageReactions(message.message_id);
        const isHighlighted = message.is_highlighted || message.message_id === selectedMessage;
        const isLeft = message.sender_name.includes('Alex');

        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                style={{
                    display: 'flex',
                    flexDirection: isLeft ? 'row' : 'row-reverse',
                    alignItems: 'flex-start',
                    gap: 12,
                    marginBottom: 16,
                    padding: '0 16px'
                }}
            >
                {/* Avatar */}
                <Box sx={{ flexShrink: 0 }}>
                    {getSenderAvatar(message)}
                </Box>

                {/* Message Content */}
                <Box sx={{ flex: 1, maxWidth: '70%' }}>
                    {/* Sender Name and Timestamp */}
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            mb: 0.5,
                            justifyContent: isLeft ? 'flex-start' : 'flex-end'
                        }}
                    >
                        <Typography variant="caption" color="text.secondary">
                            {message.sender_name}
                        </Typography>
                        <Typography variant="caption" color="text.disabled">
                            {format(new Date(message.timestamp), 'HH:mm')}
                        </Typography>
                        {message.compatibility_impact && message.compatibility_impact > 0.05 && (
                            <Tooltip title={`Compatibility impact: +${(message.compatibility_impact * 100).toFixed(1)}%`}>
                                <TrendingUp sx={{ fontSize: 14, color: 'success.main' }} />
                            </Tooltip>
                        )}
                    </Box>

                    {/* Message Bubble */}
                    <Paper
                        elevation={isHighlighted ? 8 : 2}
                        sx={{
                            p: 2,
                            bgcolor: isLeft ? 'primary.light' : 'secondary.light',
                            color: isLeft ? 'primary.contrastText' : 'secondary.contrastText',
                            borderRadius: 2,
                            position: 'relative',
                            border: isHighlighted ? '2px solid #FFD700' : 'none',
                            boxShadow: isHighlighted ? '0 0 20px rgba(255, 215, 0, 0.3)' : undefined,
                            animation: isHighlighted ? 'pulse 2s infinite' : 'none',
                            '@keyframes pulse': {
                                '0%': { boxShadow: '0 0 20px rgba(255, 215, 0, 0.3)' },
                                '50%': { boxShadow: '0 0 30px rgba(255, 215, 0, 0.6)' },
                                '100%': { boxShadow: '0 0 20px rgba(255, 215, 0, 0.3)' }
                            }
                        }}
                    >
                        <Typography variant="body1" sx={{ mb: 1 }}>
                            {message.content}
                        </Typography>

                        {/* Emotion Indicators */}
                        {message.emotion_indicators.length > 0 && (
                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 1 }}>
                                {message.emotion_indicators.map((emotion, idx) => (
                                    <Chip
                                        key={idx}
                                        label={emotion}
                                        size="small"
                                        sx={{
                                            bgcolor: getEmotionColor(emotion),
                                            color: 'white',
                                            fontSize: '0.7rem',
                                            height: 20
                                        }}
                                    />
                                ))}
                            </Box>
                        )}

                        {/* Highlight Badge */}
                        {message.is_highlighted && (
                            <Chip
                                icon={<Star />}
                                label="Key Moment"
                                size="small"
                                color="warning"
                                sx={{
                                    position: 'absolute',
                                    top: -8,
                                    right: -8,
                                    fontSize: '0.7rem'
                                }}
                            />
                        )}

                        {/* Reaction Button */}
                        <IconButton
                            size="small"
                            onClick={(e) => handleReactionClick(e, message.message_id)}
                            sx={{
                                position: 'absolute',
                                bottom: -8,
                                right: isLeft ? -8 : 'auto',
                                left: isLeft ? 'auto' : -8,
                                bgcolor: 'background.paper',
                                '&:hover': { bgcolor: 'background.default' }
                            }}
                        >
                            <EmojiEmotions fontSize="small" />
                        </IconButton>
                    </Paper>

                    {/* User Reactions */}
                    {reactions.length > 0 && (
                        <Box
                            sx={{
                                display: 'flex',
                                gap: 0.5,
                                mt: 1,
                                justifyContent: isLeft ? 'flex-start' : 'flex-end'
                            }}
                        >
                            <AnimatePresence>
                                {reactions.map((reaction, idx) => (
                                    <motion.div
                                        key={reaction.reaction_id}
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        exit={{ scale: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                    >
                                        <Tooltip title={`${reaction.user_name} reacted with ${reaction.reaction_type}`}>
                                            <Chip
                                                label={getReactionEmoji(reaction.reaction_type)}
                                                size="small"
                                                variant="outlined"
                                                sx={{ fontSize: '0.8rem' }}
                                            />
                                        </Tooltip>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </Box>
                    )}
                </Box>
            </motion.div>
        );
    };

    const getReactionEmoji = (reactionType: string): string => {
        const reactionEmojis: Record<string, string> = {
            like: '👍',
            love: '❤️',
            laugh: '😂',
            surprise: '😮',
            concern: '😟'
        };
        return reactionEmojis[reactionType] || '👍';
    };

    return (
        <Box
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.paper'
            }}
        >
            {/* Messages Container */}
            <Box
                ref={messagesContainerRef}
                sx={{
                    flex: 1,
                    overflowY: 'auto',
                    py: 2,
                    '&::-webkit-scrollbar': {
                        width: 8
                    },
                    '&::-webkit-scrollbar-track': {
                        bgcolor: 'background.default'
                    },
                    '&::-webkit-scrollbar-thumb': {
                        bgcolor: 'divider',
                        borderRadius: 4
                    }
                }}
            >
                {messages.length === 0 ? (
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '100%',
                            gap: 2,
                            color: 'text.secondary'
                        }}
                    >
                        <Psychology sx={{ fontSize: 64, opacity: 0.5 }} />
                        <Typography variant="h6">AI Theater Ready</Typography>
                        <Typography variant="body2" textAlign="center">
                            Start the conversation to watch your AI avatars interact in real-time
                        </Typography>
                    </Box>
                ) : (
                    <AnimatePresence>
                        {messages.map((message, index) => (
                            <MessageBubble
                                key={message.message_id}
                                message={message}
                                index={index}
                            />
                        ))}
                    </AnimatePresence>
                )}
            </Box>

            {/* Reaction Menu */}
            <Menu
                anchorEl={reactionMenuAnchor}
                open={Boolean(reactionMenuAnchor)}
                onClose={() => setReactionMenuAnchor(null)}
                transformOrigin={{ horizontal: 'center', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'center', vertical: 'bottom' }}
            >
                {[
                    { type: 'like', emoji: '👍', label: 'Like' },
                    { type: 'love', emoji: '❤️', label: 'Love' },
                    { type: 'laugh', emoji: '😂', label: 'Funny' },
                    { type: 'surprise', emoji: '😮', label: 'Surprising' },
                    { type: 'concern', emoji: '😟', label: 'Concerning' }
                ].map((reaction) => (
                    <MenuItem
                        key={reaction.type}
                        onClick={() => handleReactionSelect(reaction.type)}
                    >
                        <ListItemIcon>
                            <span style={{ fontSize: '1.2rem' }}>{reaction.emoji}</span>
                        </ListItemIcon>
                        <ListItemText>{reaction.label}</ListItemText>
                    </MenuItem>
                ))}
            </Menu>
        </Box>
    );
};

export default ConversationDisplay;