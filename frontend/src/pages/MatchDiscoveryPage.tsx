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
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Slider,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    CircularProgress,
    Alert,
    Fab,
    Badge
} from '@mui/material';
import {
    Favorite,
    Close,
    FilterList,
    Refresh,
    LocationOn,
    Star,
    Message,
    Visibility
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';

interface PotentialMatch {
    user_id: string;
    display_name: string;
    age?: number;
    location: string;
    primary_photo_url?: string;
    bio_preview: string;
    compatibility_preview: number;
    shared_interests: string[];
    personality_highlights: string[];
    is_online: boolean;
    mutual_connections: number;
}

interface MatchFilters {
    age_min?: number;
    age_max?: number;
    max_distance?: number;
}

interface MatchDiscoveryResponse {
    matches: PotentialMatch[];
    total_count: number;
    has_more: boolean;
    recommendations: string[];
}

const MatchDiscoveryPage: React.FC = () => {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const [matches, setMatches] = useState<PotentialMatch[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [showFilters, setShowFilters] = useState(false);
    const [filters, setFilters] = useState<MatchFilters>({
        age_min: 18,
        age_max: 50,
        max_distance: 50
    });
    const [totalCount, setTotalCount] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [recommendations, setRecommendations] = useState<string[]>([]);
    const [likeLoading, setLikeLoading] = useState(false);
    const [passLoading, setPassLoading] = useState(false);

    useEffect(() => {
        loadMatches();
    }, []);

    const loadMatches = async (newFilters?: MatchFilters) => {
        try {
            setLoading(true);
            setError(null);

            const params = new URLSearchParams();
            params.append('limit', '20');
            params.append('offset', '0');

            const activeFilters = newFilters || filters;
            if (activeFilters.age_min) params.append('age_min', activeFilters.age_min.toString());
            if (activeFilters.age_max) params.append('age_max', activeFilters.age_max.toString());
            if (activeFilters.max_distance) params.append('max_distance', activeFilters.max_distance.toString());

            const response: MatchDiscoveryResponse = await api.get(`/api/v1/matches/discover?${params}`);

            setMatches(response.matches);
            setTotalCount(response.total_count);
            setHasMore(response.has_more);
            setRecommendations(response.recommendations || []);
            setCurrentIndex(0);
        } catch (err: any) {
            setError(err.message || 'Failed to load matches');
        } finally {
            setLoading(false);
        }
    };

    const handleLike = async () => {
        if (currentIndex >= matches.length) return;

        const currentMatch = matches[currentIndex];
        setLikeLoading(true);

        try {
            const response = await api.post(`/api/v1/matches/like/${currentMatch.user_id}`);

            if (response.is_mutual) {
                // Show mutual match notification
                alert(`🎉 It's a match with ${currentMatch.display_name}!`);
                navigate('/matches');
            } else {
                // Move to next match
                nextMatch();
            }
        } catch (err: any) {
            setError(err.message || 'Failed to like user');
        } finally {
            setLikeLoading(false);
        }
    };

    const handlePass = async () => {
        if (currentIndex >= matches.length) return;

        const currentMatch = matches[currentIndex];
        setPassLoading(true);

        try {
            await api.post(`/api/v1/matches/pass/${currentMatch.user_id}`);
            nextMatch();
        } catch (err: any) {
            setError(err.message || 'Failed to pass on user');
        } finally {
            setPassLoading(false);
        }
    };

    const nextMatch = () => {
        if (currentIndex < matches.length - 1) {
            setCurrentIndex(currentIndex + 1);
        } else if (hasMore) {
            // Load more matches
            loadMatches();
        }
    };

    const handleApplyFilters = () => {
        setShowFilters(false);
        loadMatches(filters);
    };

    const getCompatibilityColor = (score: number) => {
        if (score >= 0.8) return '#4caf50'; // Green
        if (score >= 0.6) return '#ff9800'; // Orange
        return '#f44336'; // Red
    };

    const getCompatibilityLabel = (score: number) => {
        if (score >= 0.8) return 'Excellent Match';
        if (score >= 0.6) return 'Good Match';
        return 'Potential Match';
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
                    <Button color="inherit" size="small" onClick={() => loadMatches()}>
                        Retry
                    </Button>
                }>
                    {error}
                </Alert>
            </Container>
        );
    }

    if (matches.length === 0) {
        return (
            <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
                <Typography variant="h5" gutterBottom>
                    No matches found
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
                    Try adjusting your filters or check back later for new matches.
                </Typography>
                <Button variant="contained" onClick={() => setShowFilters(true)}>
                    Adjust Filters
                </Button>
            </Container>
        );
    }

    const currentMatch = matches[currentIndex];

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    Discover Matches
                </Typography>
                <Box>
                    <IconButton onClick={() => setShowFilters(true)} color="primary">
                        <FilterList />
                    </IconButton>
                    <IconButton onClick={() => loadMatches()} color="primary">
                        <Refresh />
                    </IconButton>
                </Box>
            </Box>

            {/* Progress indicator */}
            <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                    {currentIndex + 1} of {matches.length} matches
                </Typography>
                <Box width="100%" bgcolor="grey.300" borderRadius={1} height={4} mt={1}>
                    <Box
                        width={`${((currentIndex + 1) / matches.length) * 100}%`}
                        bgcolor="primary.main"
                        height="100%"
                        borderRadius={1}
                    />
                </Box>
            </Box>

            {/* Current match card */}
            <Card sx={{ maxWidth: 600, mx: 'auto', mb: 4 }}>
                {currentMatch.primary_photo_url && (
                    <CardMedia
                        component="img"
                        height="400"
                        image={currentMatch.primary_photo_url}
                        alt={currentMatch.display_name}
                        sx={{ objectFit: 'cover' }}
                    />
                )}

                <CardContent>
                    {/* User info */}
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Box>
                            <Typography variant="h5" component="h2">
                                {currentMatch.display_name}
                                {currentMatch.age && `, ${currentMatch.age}`}
                                {currentMatch.is_online && (
                                    <Chip
                                        label={t('messages.online')}
                                        size="small"
                                        color="success"
                                        sx={{ ml: 1 }}
                                    />
                                )}
                            </Typography>
                            <Box display="flex" alignItems="center" mt={1}>
                                <LocationOn fontSize="small" color="action" />
                                <Typography variant="body2" color="text.secondary" ml={0.5}>
                                    {currentMatch.location}
                                </Typography>
                            </Box>
                        </Box>

                        {/* Compatibility score */}
                        <Box textAlign="center">
                            <Box
                                sx={{
                                    width: 60,
                                    height: 60,
                                    borderRadius: '50%',
                                    bgcolor: getCompatibilityColor(currentMatch.compatibility_preview),
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: 'white',
                                    fontWeight: 'bold'
                                }}
                            >
                                {Math.round(currentMatch.compatibility_preview * 100)}%
                            </Box>
                            <Typography variant="caption" display="block" mt={0.5}>
                                {getCompatibilityLabel(currentMatch.compatibility_preview)}
                            </Typography>
                        </Box>
                    </Box>

                    {/* Bio */}
                    <Typography variant="body1" paragraph>
                        {currentMatch.bio_preview}
                    </Typography>

                    {/* Personality highlights */}
                    {currentMatch.personality_highlights.length > 0 && (
                        <Box mb={2}>
                            <Typography variant="subtitle2" gutterBottom>
                                Personality Highlights
                            </Typography>
                            <Box display="flex" flexWrap="wrap" gap={1}>
                                {currentMatch.personality_highlights.map((highlight, index) => (
                                    <Chip
                                        key={index}
                                        label={highlight}
                                        variant="outlined"
                                        size="small"
                                        icon={<Star />}
                                    />
                                ))}
                            </Box>
                        </Box>
                    )}

                    {/* Shared interests */}
                    {currentMatch.shared_interests.length > 0 && (
                        <Box mb={2}>
                            <Typography variant="subtitle2" gutterBottom>
                                Shared Interests
                            </Typography>
                            <Box display="flex" flexWrap="wrap" gap={1}>
                                {currentMatch.shared_interests.map((interest, index) => (
                                    <Chip
                                        key={index}
                                        label={interest}
                                        color="primary"
                                        variant="outlined"
                                        size="small"
                                    />
                                ))}
                            </Box>
                        </Box>
                    )}

                    {/* Mutual connections */}
                    {currentMatch.mutual_connections > 0 && (
                        <Typography variant="body2" color="text.secondary">
                            {currentMatch.mutual_connections} mutual connections
                        </Typography>
                    )}
                </CardContent>
            </Card>

            {/* Action buttons */}
            <Box display="flex" justifyContent="center" gap={4} mb={4}>
                <Fab
                    color="default"
                    onClick={handlePass}
                    disabled={passLoading}
                    sx={{ width: 70, height: 70 }}
                >
                    {passLoading ? <CircularProgress size={24} /> : <Close />}
                </Fab>

                <Fab
                    color="primary"
                    onClick={handleLike}
                    disabled={likeLoading}
                    sx={{ width: 70, height: 70 }}
                >
                    {likeLoading ? <CircularProgress size={24} /> : <Favorite />}
                </Fab>
            </Box>

            {/* Recommendations */}
            {recommendations.length > 0 && (
                <Box mb={4}>
                    <Typography variant="h6" gutterBottom>
                        Tips to improve your matches
                    </Typography>
                    {recommendations.map((rec, index) => (
                        <Alert key={index} severity="info" sx={{ mb: 1 }}>
                            {rec}
                        </Alert>
                    ))}
                </Box>
            )}

            {/* Filters Dialog */}
            <Dialog open={showFilters} onClose={() => setShowFilters(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Filter Matches</DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2 }}>
                        {/* Age range */}
                        <Typography gutterBottom>Age Range</Typography>
                        <Box sx={{ px: 2, mb: 3 }}>
                            <Slider
                                value={[filters.age_min || 18, filters.age_max || 50]}
                                onChange={(_, newValue) => {
                                    const [min, max] = newValue as number[];
                                    setFilters({ ...filters, age_min: min, age_max: max });
                                }}
                                valueLabelDisplay="auto"
                                min={18}
                                max={80}
                                marks={[
                                    { value: 18, label: '18' },
                                    { value: 30, label: '30' },
                                    { value: 50, label: '50' },
                                    { value: 80, label: '80' }
                                ]}
                            />
                        </Box>

                        {/* Distance */}
                        <Typography gutterBottom>Maximum Distance (km)</Typography>
                        <Box sx={{ px: 2, mb: 3 }}>
                            <Slider
                                value={filters.max_distance || 50}
                                onChange={(_, newValue) => {
                                    setFilters({ ...filters, max_distance: newValue as number });
                                }}
                                valueLabelDisplay="auto"
                                min={5}
                                max={500}
                                marks={[
                                    { value: 5, label: '5km' },
                                    { value: 25, label: '25km' },
                                    { value: 100, label: '100km' },
                                    { value: 500, label: '500km' }
                                ]}
                            />
                        </Box>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowFilters(false)}>Cancel</Button>
                    <Button onClick={handleApplyFilters} variant="contained">
                        Apply Filters
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Floating action button for matches */}
            <Fab
                color="secondary"
                sx={{ position: 'fixed', bottom: 16, right: 16 }}
                onClick={() => navigate('/matches')}
            >
                <Badge badgeContent={0} color="error">
                    <Message />
                </Badge>
            </Fab>
        </Container>
    );
};

export default MatchDiscoveryPage;