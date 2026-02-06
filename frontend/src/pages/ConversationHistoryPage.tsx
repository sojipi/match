/**
 * Conversation History Page - View past AI conversation sessions
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container,
    Box,
    Paper,
    Typography,
    IconButton,
    Tooltip,
    CircularProgress,
    Alert,
    Avatar,
    Chip,
    Divider
} from '@mui/material';
import { ArrowBack, SmartToy, Person } from '@mui/icons-material';
import { api } from '../utils/api';

interface ConversationMessage {
    message_id: string;
    sender_type: string;
    sender_name: string;
    content: string;
    timestamp: string;
    emotion_indicators: string[];
}

interface SessionInfo {
    session_id: string;
    status: string;
    started_at: string | null;
    ended_at: string | null;
}

interface MessagesResponse {
    messages: ConversationMessage[];
    total_count: number;
    has_more: boolean;
    session: SessionInfo;
}

const ConversationHistoryPage: React.FC = () => {
    const { sessionId } = useParams<{ sessionId: string }>();
    const navigate = useNavigate();
    const [messages, setMessages] = useState<ConversationMessage[]>([]);
    const [session, setSession] = useState<SessionInfo | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (sessionId) {
            loadMessages();
        }
    }, [sessionId]);

    const loadMessages = async () => {
        try {
            setLoading(true);
            const response = await api.get<MessagesResponse>(
                `/api/v1/sessions/${sessionId}/messages?limit=100`
            );
            setMessages(response.messages);
            setSession(response.session);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load conversation history');
        } finally {
            setLoading(false);
        }
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleString();
    };

    const getMessageIcon = (senderType: string) => {
        if (senderType === 'user_avatar') {
            return <SmartToy />;
        } else if (senderType === 'matchmaker_agent') {
            return <Person />;
        }
        return <SmartToy />;
    };

    const getMessageColor = (senderType: string) => {
        if (senderType === 'matchmaker_agent') {
            return 'secondary';
        }
        return 'primary';
    };

    if (loading) {
        return (
            <Container maxWidth="md" sx={{ py: 4 }}>
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                    <CircularProgress />
                </Box>
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxWidth="md" sx={{ py: 4 }}>
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
                <IconButton onClick={() => navigate('/matches')}>
                    <ArrowBack />
                </IconButton>
            </Container>
        );
    }

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            <Box sx={{ mb: 3 }}>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Tooltip title="Back to Matches">
                        <IconButton onClick={() => navigate('/matches')}>
                            <ArrowBack />
                        </IconButton>
                    </Tooltip>
                    <Typography variant="h4">
                        Conversation History
                    </Typography>
                </Box>

                {session && (
                    <Paper sx={{ p: 2, mb: 2 }}>
                        <Box display="flex" gap={2} alignItems="center">
                            <Chip
                                label={session.status}
                                color={session.status === 'completed' ? 'success' : 'default'}
                                size="small"
                            />
                            {session.started_at && (
                                <Typography variant="body2" color="text.secondary">
                                    Started: {formatTimestamp(session.started_at)}
                                </Typography>
                            )}
                            {session.ended_at && (
                                <Typography variant="body2" color="text.secondary">
                                    Ended: {formatTimestamp(session.ended_at)}
                                </Typography>
                            )}
                        </Box>
                    </Paper>
                )}
            </Box>

            <Paper sx={{ p: 2 }}>
                {messages.length === 0 ? (
                    <Box textAlign="center" py={4}>
                        <Typography variant="body1" color="text.secondary">
                            No messages in this conversation
                        </Typography>
                    </Box>
                ) : (
                    <Box>
                        {messages.map((message, index) => (
                            <Box key={message.message_id}>
                                <Box display="flex" gap={2} py={2}>
                                    <Avatar sx={{ bgcolor: `${getMessageColor(message.sender_type)}.main` }}>
                                        {getMessageIcon(message.sender_type)}
                                    </Avatar>
                                    <Box flex={1}>
                                        <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                                            <Typography variant="subtitle2" fontWeight="bold">
                                                {message.sender_name}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                {formatTimestamp(message.timestamp)}
                                            </Typography>
                                        </Box>
                                        <Typography variant="body1" paragraph>
                                            {message.content}
                                        </Typography>
                                        {message.emotion_indicators && message.emotion_indicators.length > 0 && (
                                            <Box display="flex" gap={0.5} flexWrap="wrap">
                                                {message.emotion_indicators.map((emotion, idx) => (
                                                    <Chip
                                                        key={idx}
                                                        label={emotion}
                                                        size="small"
                                                        variant="outlined"
                                                    />
                                                ))}
                                            </Box>
                                        )}
                                    </Box>
                                </Box>
                                {index < messages.length - 1 && <Divider />}
                            </Box>
                        ))}
                    </Box>
                )}
            </Paper>

            <Box mt={2} textAlign="center">
                <Typography variant="body2" color="text.secondary">
                    Total messages: {messages.length}
                </Typography>
            </Box>
        </Container>
    );
};

export default ConversationHistoryPage;
