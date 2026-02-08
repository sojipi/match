import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Container,
    Box,
    Grid,
    Paper,
    Typography,
    useMediaQuery,
    useTheme,
    CircularProgress,
    Alert
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppSelector } from '../hooks/redux';
import ConversationsList from '../components/messaging/ConversationsList';
import MessageList from '../components/messaging/MessageList';
import { api } from '../utils/api';

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

interface MatchUser {
    id: string;
    name: string;
    photo_url?: string;
}

const MessagesPage: React.FC = () => {
    const theme = useTheme();
    const { t } = useTranslation();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const { matchId } = useParams<{ matchId: string }>();
    const navigate = useNavigate();
    const { user } = useAppSelector(state => state.auth);
    const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
    const [matchUser, setMatchUser] = useState<MatchUser | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (matchId && !selectedConversation) {
            loadMatchInfo(matchId);
        }
    }, [matchId]);

    const loadMatchInfo = async (matchId: string) => {
        try {
            setLoading(true);
            setError(null);

            // Try to get match info from the matches API
            const response = await api.get(`/api/v1/matches/${matchId}`);

            // Determine which user is the other user
            const otherUser = response.user1_id === user?.id
                ? { id: response.user2_id, name: response.user2_name || 'User', photo_url: response.user2_photo }
                : { id: response.user1_id, name: response.user1_name || 'User', photo_url: response.user1_photo };

            setMatchUser(otherUser);
        } catch (err: any) {
            console.error('Failed to load match info:', err);
            setError('Failed to load conversation. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSelectConversation = (conversation: Conversation) => {
        setSelectedConversation(conversation);
        setMatchUser(conversation.other_user);
        if (isMobile) {
            navigate(`/messages/${conversation.match_id}`);
        }
    };

    // Loading state
    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
                <CircularProgress />
            </Box>
        );
    }

    // Error state
    if (error) {
        return (
            <Container maxWidth="md" sx={{ py: 4 }}>
                <Alert severity="error">{error}</Alert>
            </Container>
        );
    }

    // On mobile, show either list or conversation
    if (isMobile) {
        if (matchId && matchUser) {
            // Show conversation
            return (
                <Container maxWidth="lg" sx={{ height: '100vh', display: 'flex', flexDirection: 'column', p: 0 }}>
                    <MessageList
                        matchId={matchId}
                        currentUserId={user?.id || ''}
                        otherUser={matchUser}
                    />
                </Container>
            );
        } else {
            // Show list
            return (
                <Container maxWidth="lg" sx={{ py: 2 }}>
                    <Typography variant="h5" gutterBottom>
                        {t('messages.title')}
                    </Typography>
                    <Paper>
                        <ConversationsList onSelectConversation={handleSelectConversation} />
                    </Paper>
                </Container>
            );
        }
    }

    // On desktop, show split view
    return (
        <Container maxWidth="lg" sx={{ py: 2, height: 'calc(100vh - 100px)' }}>
            <Typography variant="h5" gutterBottom>
                {t('messages.title')}
            </Typography>
            <Grid container spacing={2} sx={{ height: 'calc(100% - 50px)' }}>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ height: '100%', overflow: 'auto' }}>
                        <ConversationsList onSelectConversation={handleSelectConversation} />
                    </Paper>
                </Grid>
                <Grid item xs={12} md={8}>
                    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                        {(selectedConversation || (matchId && matchUser)) ? (
                            <MessageList
                                matchId={matchId || selectedConversation!.match_id}
                                currentUserId={user?.id || ''}
                                otherUser={matchUser || selectedConversation!.other_user}
                            />
                        ) : (
                            <Box
                                display="flex"
                                justifyContent="center"
                                alignItems="center"
                                height="100%"
                            >
                                <Typography variant="body1" color="text.secondary">
                                    {t('messages.selectConversation')}
                                </Typography>
                            </Box>
                        )}
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default MessagesPage;