import React, { useState, useEffect } from 'react';
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
    TrendingUp
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

    const handleViewCompatibility = (matchId: string) => {
        // Navigate to compatibility report
        navigate(`/compatibility/${matchId}`);
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
        if (score >= 0.8) return 'Excellent';
        if (score >= 0.6) return 'Good';
        return 'Fair';
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
                        Retry
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
                    Your Matches
                </Typography>
                <Button
                    variant="contained"
                    onClick={() => navigate('/discover')}
                    startIcon={<Favorite />}
                >
                    Discover More
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
                                Total Matches
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
                                High Compatibility
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
                                Active Conversations
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
                                Total Conversations
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                <Tabs value={currentTab} onChange={handleTabChange}>
                    <Tab label={`All (${matches.length})`} />
                    <Tab label="Recent" />
                    <Tab label="High Compatibility" />
                    <Tab label="Active Conversations" />
                </Tabs>
            </Box>

            {/* Matches list */}
            {filteredMatches.length === 0 ? (
                <Box textAlign="center" py={8}>
                    <Typography variant="h6" gutterBottom>
                        No matches found
                    </Typography>
                    <Typography variant="body1" color="text.secondary" paragraph>
                        {currentTab === 0
                            ? "Start discovering matches to see them here!"
                            : "No matches match the current filter."
                        }
                    </Typography>
                    <Button
                        variant="contained"
                        onClick={() => navigate('/discover')}
                        startIcon={<Favorite />}
                    >
                        Discover Matches
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
                                                {getCompatibilityLabel(match.compatibility_score)} compatibility
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                Matched {formatDate(match.created_at)}
                                                {match.last_interaction && (
                                                    <> • Last interaction {formatDate(match.last_interaction)}</>
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
                                                handleStartConversation(match.id);
                                            }}
                                        >
                                            Chat
                                        </Button>
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            startIcon={<Visibility />}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleViewCompatibility(match.id);
                                            }}
                                        >
                                            View Report
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
                                        label={`${Math.round(selectedMatch.compatibility_score * 100)}% Compatible`}
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
                                            Conversations
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={6}>
                                    <Box textAlign="center">
                                        <Typography variant="h4" color="success.main">
                                            {Math.round(selectedMatch.compatibility_score * 100)}%
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Compatibility
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>

                            <Box mt={3}>
                                <Typography variant="body2" color="text.secondary">
                                    Matched on {formatDate(selectedMatch.created_at)}
                                </Typography>
                                {selectedMatch.last_interaction && (
                                    <Typography variant="body2" color="text.secondary">
                                        Last interaction: {formatDate(selectedMatch.last_interaction)}
                                    </Typography>
                                )}
                            </Box>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setShowMatchDetails(false)}>
                                Close
                            </Button>
                            <Button
                                variant="outlined"
                                startIcon={<Visibility />}
                                onClick={() => {
                                    setShowMatchDetails(false);
                                    handleViewCompatibility(selectedMatch.id);
                                }}
                            >
                                View Report
                            </Button>
                            <Button
                                variant="contained"
                                startIcon={<Message />}
                                onClick={() => {
                                    setShowMatchDetails(false);
                                    handleStartConversation(selectedMatch.id);
                                }}
                            >
                                Start Conversation
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
                        handleViewCompatibility(selectedMatchForMenu.id);
                    }
                    handleMenuClose();
                }}>
                    <Visibility sx={{ mr: 1 }} />
                    View Compatibility Report
                </MenuItem>
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleStartConversation(selectedMatchForMenu.id);
                    }
                    handleMenuClose();
                }}>
                    <Message sx={{ mr: 1 }} />
                    Start Conversation
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleBlockUser(selectedMatchForMenu.id);
                    }
                }}>
                    <Block sx={{ mr: 1 }} />
                    Block User
                </MenuItem>
                <MenuItem onClick={() => {
                    if (selectedMatchForMenu) {
                        handleReportUser(selectedMatchForMenu.id);
                    }
                }}>
                    <Report sx={{ mr: 1 }} />
                    Report User
                </MenuItem>
            </Menu>
        </Container>
    );
};

export default MatchesPage;