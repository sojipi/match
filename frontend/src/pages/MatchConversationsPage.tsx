/**
 * Match Conversations Page - View all conversation sessions for a match
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
    List,
    ListItem,
    ListItemButton,
    ListItemText,
    Chip,
    Divider
} from '@mui/material';
import { ArrowBack, Chat } from '@mui/icons-material';
import { api } from '../utils/api';

interface ConversationSession {
    session_id: string;
    status: string;
    session_type: string;
    started_at: string | null;
    ended_at: string | null;
    message_count: number;
    created_at: string;
}

interface SessionsResponse {
    match_id: string;
    sessions: ConversationSession[];
    total_count: number;
}

const MatchConversationsPage: React.FC = () => {
    const { matchId } = useParams<{ matchId: string }>();
    const navigate = useNavigate();
    const [sessions, setSessions] = useState<ConversationSession[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (matchId) {
            loadSessions();
        }
    }, [matchId]);

    const loadSessions = async () => {
        try {
            setLoading(true);
            const response = await api.get<SessionsResponse>(
                `/api/v1/sessions/match/${matchId}/sessions`
            );
            setSessions(response.sessions);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load conversation sessions');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString: string | null) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'completed':
                return 'success';
            case 'active':
                return 'primary';
            case 'terminated':
                return 'error';
            default:
                return 'default';
        }
    };

    const handleSessionClick = (sessionId: string) => {
        navigate(`/conversation/${sessionId}`);
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
                        Conversation Sessions
                    </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                    Select a conversation to view its history
                </Typography>
            </Box>

            {sessions.length === 0 ? (
                <Paper sx={{ p: 4, textAlign: 'center' }}>
                    <Chat sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        No Conversations Yet
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Start a conversation with this match to see it here
                    </Typography>
                </Paper>
            ) : (
                <Paper>
                    <List>
                        {sessions.map((session, index) => (
                            <React.Fragment key={session.session_id}>
                                <ListItem disablePadding>
                                    <ListItemButton onClick={() => handleSessionClick(session.session_id)}>
                                        <ListItemText
                                            primary={
                                                <Box display="flex" alignItems="center" gap={1}>
                                                    <Typography variant="subtitle1">
                                                        {session.session_type === 'conversation' ? 'AI Conversation' : session.session_type}
                                                    </Typography>
                                                    <Chip
                                                        label={session.status}
                                                        color={getStatusColor(session.status)}
                                                        size="small"
                                                    />
                                                </Box>
                                            }
                                            secondary={
                                                <Box>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Started: {formatDate(session.started_at)}
                                                    </Typography>
                                                    {session.ended_at && (
                                                        <Typography variant="body2" color="text.secondary">
                                                            Ended: {formatDate(session.ended_at)}
                                                        </Typography>
                                                    )}
                                                    <Typography variant="body2" color="text.secondary">
                                                        Messages: {session.message_count}
                                                    </Typography>
                                                </Box>
                                            }
                                        />
                                    </ListItemButton>
                                </ListItem>
                                {index < sessions.length - 1 && <Divider />}
                            </React.Fragment>
                        ))}
                    </List>
                </Paper>
            )}

            <Box mt={2} textAlign="center">
                <Typography variant="body2" color="text.secondary">
                    Total sessions: {sessions.length}
                </Typography>
            </Box>
        </Container>
    );
};

export default MatchConversationsPage;
