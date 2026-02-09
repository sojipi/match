import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Box,
    Container,
    Typography,
    Grid,
    Card,
    CardContent,
    CardMedia,
    Button,
    Chip,
    Avatar,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Tabs,
    Tab,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress,
    Alert,
    Badge,
    Divider,
    Menu,
    MenuItem
} from '@mui/material';
import {
    Message,
    Favorite,
    Star,
    MoreVert,
    Block,
    Report,
    Visibility,
    Schedule,
    TrendingUp,
    History,
    Psychology
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';

interface MatchUser {
    id: string;
    name: string;
    photo_url?: string;
}

interface MatchHistoryItem {
    id: string;
    user: MatchUser;
    compatibility_score: number;
    status: string;
    conversation_count: number;
    last_interaction?: string;
    created_at: string;
}

interface MatchHistoryResponse {
    matches: MatchHistoryItem[];
}

const MatchesPage: React.FC = () => {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const [matches, setMatches] = useState<MatchHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentTab, setCurrentTab] = useState(0);
    const [selectedMatch, setSelectedMatch] = useState<MatchHistoryItem | null>(null);
    const [showMatchDetails, setShowMatchDetails] = useState(false);
    const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
    const [selectedMatchForMenu, setSelectedMatchForMenu] = useState<MatchHistoryItem | null>(null);

    useEffect(() => {
        loadMatches();
    }, []);

    const loadMatches = async () => {
        try {
            setLoading(true);
            setError(null);

            const response: MatchHistoryResponse = await api.get('/api/v1/matches/history');
            setMatches(response.matches);
        } catch (err: any) {
            setError(err.message || 'Failed to load matches');
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setCurrentTab(newValue);
    };

    const handleMatchClick = (match: MatchHistoryItem) => {
        setSelectedMatch(match);
        setShowMatchDetails(true);
    };

    const handleMenuClick = (event: React.MouseEvent<HTMLElement>, match: MatchHistoryItem) => {
        event.stopPropagation();
        setMenuAnchor(event.currentTarget);
        setSelectedMatchForMenu(match);
    };

    const handleMenuClose = () => {
        setMenuAnchor(null);
        setSelectedMatchForMenu(null);
    };

    const handleStartConversation = async (matchId: string) => {
        try {
            setLoading(true);
            setError(null);

            // Create a new conversation session
            const response = await api.post('/api/v1/sessions/create', {
                match_id: matchId,
                session_type: 'conversation'
            });

            // Navigate to theater with the session ID
            navigate(`/theater/${response.session_id}`);
        } catch (err: any) {
            setError(err.message || 'Failed to start conversation');
            setLoading(false);
        }
    };

    const handleViewCompatibility = (match: MatchHistoryItem) => {
        // Navigate to compatibility report using the matched user's ID
        navigate(`/compatibility/${match.user.id}`);
    };

    const handleViewConversationHistory = (matchId: string) => {
        // Navigate to sessions list for this match
        navigate(`/match/${matchId}/conversations`);
    };

    const handleStartScenarioSimulation = (match: MatchHistoryItem) => {
        // Navigate to scenario simulation page
        navigate(`/scenario-simulation/${match.id}`, {
            state: {
                matchUserId: match.user.id,
                matchUserName: match.user.name
            }
        });
    };

    const handleBlockUser = async (matchId: string) => {
        try {
            // TODO: Implement block user API
            console.log('Block user:', matchId);
            handleMenuClose();
        } catch (err: any) {
            setError(err.message || 'Failed to block user');
        }
    };

    const handleReportUser = async (matchId: string) => {
        try {
            // TODO: Implement report user API
            console.log('Report user:', matchId);
            handleMenuClose();
        } catch (err: any) {
            setError(err.message || 'Failed to report user');
        }
    };

    const getCompatibilityColor = (score: number) => {
        if (score >= 0.8) return 'success';
        if (score >= 0.6) return 'warning';
        return 'error';
    };

    const getCompatibilityLabel = (score: number) => {
        if (score >= 0.8) return t('matches.compatibility.excellent');
        if (score >= 0.6) return t('matches.compatibility.good');
        return t('matches.compatibility.fair');
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - date.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 1) return t('matches.time.yesterday');
        if (diffDays < 7) return t('matches.time.daysAgo', { days: diffDays });
        if (diffDays < 30) return t('matches.time.weeksAgo', { weeks: Math.ceil(diffDays / 7) });
        return date.toLocaleDateString();
    };

    const filterMatches = (matches: MatchHistoryItem[]) => {
        switch (currentTab) {
            case 0: // All matches
                return matches;
            case 1: // Recent matches
                return matches.filter(match => {
                    const matchDate = new Date(match.created_at);
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    return matchDate >= weekAgo;
                });
            case 2: // High compatibility
                return matches.filter(match => match.compatibility_score >= 0.8);
            case 3: // Active conversations
                return matches.filter(match => match.conversation_count > 0);
            default:
                return matches;
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    if (error) {
        return (
            <Container maxWidth="md" sx={{ mt: 4 }}>
                <Alert severity="error" action={
                    <Button color="inherit" size="small" onClick={loadMatches}>
                        {t('common.retry')}
                    </Button>
                }>
                    {error}
                </Alert>
            </Container>
        );
    }

    const filteredMatches = filterMatches(matches);

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    {t('matches.title')}
                </Typography>
                <Button
                    variant="contained"
                    onClick={() => navigate('/discover')}
                    startIcon={<Favorite />}
                >
                    {t('matches.discoverMore')}
                </Button>
            </Box>

            {/* Stats */}
            <Grid container spacing={3} mb={4}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="primary">
                                {matches.length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {t('matches.stats.totalMatches')}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="success.main">
                                {matches.filter(m => m.compatibility_score >= 0.8).length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {t('matches.stats.highCompatibility')}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="info.main">
                                {matches.filter(m => m.conversation_count > 0).length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {t('matches.stats.activeConversations')}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="warning.main">
                                {matches.reduce((sum, m) => sum + m.conversation_count, 0)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {t('matches.stats.totalConversations')}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                <Tabs value={currentTab} onChange={handleTabChange}>
                    <Tab label={`${t('matches.tabs.all')} (${matches.length})`} />
                    <Tab label={t('matches.tabs.recent')} />
                    <Tab label={t('matches.tabs.highCompatibility')} />
                    <Tab label={t('matches.tabs.activeConversations')} />
                </Tabs>
            </Box>

            {/* Matches list */}
            {filteredMatches.length === 0 ? (
                <Box textAlign="center" py={8}>
                    <Typography variant="h6" gutterBottom>
                        {t('matches.empty.noMatches')}
                    </Typography>
                    <Typography variant="body1" color="text.secondary" paragraph>
                        {currentTab === 0
                            ? t('matches.empty.startDiscovering')
                            : t('matches.empty.noFilter')
                        }
                    </Typography>
                    <Button
                        variant="contained"
                        onClick={() => navigate('/discover')}
                        startIcon={<Favorite />}
                    >
                        {t('matching.discover')}
                    </Button>
                </Box>
            ) : (
                <List>
                    {filteredMatches.map((match, index) => (
                        <React.Fragment key={match.id}>
                            <ListItem
                                button
                                onClick={() => handleMatchClick(match)}
                                sx={{ py: 2 }}
                            >
                                <ListItemAvatar>
                                    <Badge
                                        overlap="circular"
                                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                                        badgeContent={
                                            match.conversation_count > 0 ? (
                                                <Badge
                                                    badgeContent={match.conversation_count}
                                                    color="primary"
                                                    sx={{ '& .MuiBadge-badge': { fontSize: '0.6rem', minWidth: '16px', height: '16px' } }}
                                                />
                                            ) : null
                                        }
                                    >
                                        <Avatar
                                            src={match.user.photo_url}
                                            alt={match.user.name}
                                            sx={{ width: 60, height: 60 }}
                                        >
                                            {match.user.name.charAt(0)}
                                        </Avatar>
                                    </Badge>
                                </ListItemAvatar>

                                <ListItemText
                                    primary={
                                        <Box display="flex" alignItems="center" gap={1}>
                                            <Typography variant="h6">
                                                {match.user.name}
                                            </Typography>
                                            <Chip
                                                label={`${Math.round(match.compatibility_score * 100)}%`}
                                                color={getCompatibilityColor(match.compatibility_score)}
                                                size="small"
                                            />
                                        </Box>
                                    }
                                    secondary={
                                        <Box>
                                            <Typography variant="body2" color="text.secondary">
                                                {getCompatibilityLabel(match.compatibility_score)} {t('matching.compatibility')}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                {t('matches.details.matchedOn')} {formatDate(match.created_at)}
                                                {match.last_interaction && (
                                                    <> • {t('matches.details.lastInteraction')} {formatDate(match.last_interaction)}</>
                                                )}
                                            </Typography>
                                        </Box>
                                    }
                                />

                                <ListItemSecondaryAction>
                                    <Box display="flex" gap={1}>
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            startIcon={<Message />}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                navigate(`/messages/${match.id}`);
                                            }}
                                        >
                                            {t('matches.message')}
                                        </Button>
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            startIcon={<Message />}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleStartConversation(match.id);
                                            }}
                                        >
                                            {t('matches.aiChat')}
                                        </Button>
                                        <Button
                                            variant="contained"
                                            size="small"
                                            color="secondary"
                                            startIcon={<Psychology />}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleStartScenarioSimulation(match);
                                            }}
                                        >
                                            {t('matches.scenario')}
                                        </Button>
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            startIcon={<Visibility />}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleViewCompatibility(match);
                                            }}
                                        >
                                            {t('matches.report')}
                                        </Button>
                                        <IconButton
                                            onClick={(e) => handleMenuClick(e, match)}
                                        >
                                            <MoreVert />
                                        </IconButton>
                                    </Box>
                                </ListItemSecondaryAction>
                            </ListItem>
                            {index < filteredMatches.length - 1 && <Divider />}
                        </React.Fragment>
                    ))}
                </List>
            )}

            {/* Match details dialog */}
            <Dialog
                open={showMatchDetails}
                onClose={() => setShowMatchDetails(false)}
                maxWidth="sm"
                fullWidth
            >
                {selectedMatch && (
                    <>
                        <DialogTitle>
                            <Box display="flex" alignItems="center" gap={2}>
                                <Avatar
                                    src={selectedMatch.user.photo_url}
                                    alt={selectedMatch.user.name}
                                    sx={{ width: 50, height: 50 }}
                                >
                                    {selectedMatch.user.name.charAt(0)}
                                </Avatar>
                                <Box>
                                    <Typography variant="h6">
                                        {selectedMatch.user.name}
                                    </Typography>
                                    <Chip
                                        label={`${Math.round(selectedMatch.compatibility_score * 100)}% ${t('matching.compatibility')}`}
                                        color={getCompatibilityColor(selectedMatch.compatibility_score)}
                                        size="small"
                                    />
                                </Box>
                            </Box>
                        </DialogTitle>
                        <DialogContent>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Box textAlign="center">
                                        <Typography variant="h4" color="primary">
                                            {selectedMatch.conversation_count}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            {t('matches.details.conversations')}
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={6}>
                                    <Box textAlign="center">
                                        <Typography variant="h4" color="success.main">
                                            {Math.round(selectedMatch.compatibility_score * 100)}%
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            {t('matches.details.compatibility')}
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>

                            <Box mt={3}>
                                <Typography variant="body2" color="text.secondary">
                                    {t('matches.details.matchedOn')} {formatDate(selectedMatch.created_at)}
                                </Typography>
                                {selectedMatch.last_interaction && (
                                    <Typography variant="body2" color="text.secondary">
                                        {t('matches.details.lastInteraction')}: {formatDate(selectedMatch.last_interaction)}
                                    </Typography>
                                )}
                            </Box>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setShowMatchDetails(false)}>
                                {t('matches.details.close')}
                            </Button>
                            <Button
                                variant="outlined"
                                startIcon={<Visibility />}
                                onClick={() => {
                                    setShowMatchDetails(false);
                                    handleViewCompatibility(selectedMatch);
                                }}
                            >
                                {t('matches.details.viewReport')}
                            </Button>
                            <Button
                                variant="outlined"
                                startIcon={<Message />}
                                onClick={() => {
                                    setShowMatchDetails(false);
                                    navigate(`/messages/${selectedMatch.id}`);
                                }}
                            >
                                {t('matches.details.directMessage')}
                            </Button>
                            <Button
                                variant="outlined"
                                startIcon={<Message />}
                                onClick={() => {
                                    setShowMatchDetails(false);
                                    handleStartConversation(selectedMatch.id);
                                }}
                            >
                                {t('matches.details.aiConversation')}
                            </Button>
                            <Button
                                variant="contained"
                                color="secondary"
                                startIcon={<Psychology />}
                                onClick={() => {
                                    setShowMatchDetails(false);
                                    handleStartScenarioSimulation(selectedMatch);
                                }}
                            >
                                {t('matches.details.scenarioSimulation')}
                            </Button>
                        </DialogActions>
                    </>
                )}
            </Dialog>

            {/* Context menu */}
            <Menu
                anchorEl={menuAnchor}
                open={Boolean(menuAnchor)}
                onClose={handleMenuClose}
            >
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        navigate(`/messages/${selectedMatchForMenu.id}`);
                    }
                    handleMenuClose();
                }}>
                    <Message sx={{ mr: 1 }} />
                    {t('matches.details.directMessage')}
                </MenuItem>
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleStartConversation(selectedMatchForMenu.id);
                    }
                    handleMenuClose();
                }}>
                    <Message sx={{ mr: 1 }} />
                    {t('matches.details.aiConversation')}
                </MenuItem>
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleStartScenarioSimulation(selectedMatchForMenu);
                    }
                    handleMenuClose();
                }}>
                    <Psychology sx={{ mr: 1 }} />
                    {t('matches.details.scenarioSimulation')}
                </MenuItem>
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleViewCompatibility(selectedMatchForMenu);
                    }
                    handleMenuClose();
                }}>
                    <Visibility sx={{ mr: 1 }} />
                    {t('matches.details.viewReport')}
                </MenuItem>
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleViewConversationHistory(selectedMatchForMenu.id);
                    }
                    handleMenuClose();
                }}>
                    <History sx={{ mr: 1 }} />
                    {t('matches.details.viewHistory')}
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleBlockUser(selectedMatchForMenu.id);
                    }
                }}>
                    <Block sx={{ mr: 1 }} />
                    {t('matches.details.blockUser')}
                </MenuItem>
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleReportUser(selectedMatchForMenu.id);
                    }
                }}>
                    <Report sx={{ mr: 1 }} />
                    {t('matches.details.reportUser')}
                </MenuItem>
            </Menu>
        </Container>
    );
};

export default MatchesPage;