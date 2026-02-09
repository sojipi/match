import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Chip,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TextField,
    Rating,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress,
    Alert
} from '@mui/material';
import {
    PlayArrow,
    Schedule,
    Star,
    People,
    Category,
    Warning
} from '@mui/icons-material';

interface Scenario {
    id: string;
    name: string;
    title: string;
    description: string;
    category: string;
    difficulty_level: number;
    estimated_duration_minutes: number;
    personality_dimensions: string[];
    value_dimensions: string[];
    tags: string[];
    user_rating: number;
    usage_count: number;
    success_rate: number;
    content_warnings: string[];
}

interface ScenarioRecommendation extends Scenario {
    personality_match_score: number;
}

interface ScenarioLibraryProps {
    matchUserId?: string;
    matchId?: string;
    onScenarioSelect: (scenario: Scenario) => void;
    showRecommendations?: boolean;
}

const ScenarioLibrary: React.FC<ScenarioLibraryProps> = ({
    matchUserId,
    matchId,
    onScenarioSelect,
    showRecommendations = true
}) => {
    const [scenarios, setScenarios] = useState<Scenario[]>([]);
    const [recommendations, setRecommendations] = useState<ScenarioRecommendation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedCategory, setSelectedCategory] = useState<string>('');
    const [selectedDifficulty, setSelectedDifficulty] = useState<number | ''>('');
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
    const [detailsOpen, setDetailsOpen] = useState(false);

    const categories = [
        { value: 'financial', label: 'Financial Decisions' },
        { value: 'family', label: 'Family Matters' },
        { value: 'lifestyle', label: 'Lifestyle Choices' },
        { value: 'career', label: 'Career & Work' },
        { value: 'social', label: 'Social Situations' },
        { value: 'conflict_resolution', label: 'Conflict Resolution' },
        { value: 'values', label: 'Values & Beliefs' },
        { value: 'communication', label: 'Communication' },
        { value: 'future_planning', label: 'Future Planning' },
        { value: 'daily_life', label: 'Daily Life' }
    ];

    const difficultyLevels = [
        { value: 1, label: 'Easy' },
        { value: 2, label: 'Moderate' },
        { value: 3, label: 'Challenging' },
        { value: 4, label: 'Difficult' },
        { value: 5, label: 'Expert' }
    ];

    useEffect(() => {
        loadScenarios();
        if (showRecommendations && matchUserId) {
            loadRecommendations();
        }
    }, [selectedCategory, selectedDifficulty, matchUserId, showRecommendations]);

    const loadScenarios = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (selectedCategory) params.append('category', selectedCategory);
            if (selectedDifficulty) params.append('difficulty', selectedDifficulty.toString());

            const response = await fetch(`/api/v1/scenarios/library?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load scenarios');
            }

            const data = await response.json();
            setScenarios(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load scenarios');
        } finally {
            setLoading(false);
        }
    };

    const loadRecommendations = async () => {
        if (!matchUserId) return;

        try {
            const params = new URLSearchParams();
            params.append('user2_id', matchUserId);
            if (matchId) params.append('match_id', matchId);

            const response = await fetch(`/api/v1/scenarios/recommendations?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load recommendations');
            }

            const data = await response.json();
            setRecommendations(data);
        } catch (err) {
            console.error('Failed to load recommendations:', err);
        }
    };

    const filteredScenarios = scenarios.filter(scenario =>
        scenario.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        scenario.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (scenario.tags && scenario.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())))
    );

    const handleScenarioClick = (scenario: Scenario) => {
        setSelectedScenario(scenario);
        setDetailsOpen(true);
    };

    const handleStartScenario = () => {
        if (selectedScenario) {
            onScenarioSelect(selectedScenario);
            setDetailsOpen(false);
        }
    };

    const getDifficultyColor = (level: number) => {
        switch (level) {
            case 1: return 'success';
            case 2: return 'info';
            case 3: return 'warning';
            case 4: return 'error';
            case 5: return 'secondary';
            default: return 'default';
        }
    };

    const getCategoryIcon = (category: string) => {
        // Return appropriate icon based on category
        return <Category />;
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" sx={{ mb: 2 }}>
                {error}
            </Alert>
        );
    }

    return (
        <Box>
            {/* Recommendations Section */}
            {showRecommendations && recommendations.length > 0 && (
                <Box mb={4}>
                    <Typography variant="h6" gutterBottom>
                        Recommended for You
                    </Typography>
                    <Grid container spacing={2}>
                        {recommendations.slice(0, 3).map((scenario) => (
                            <Grid item xs={12} md={4} key={scenario.id}>
                                <Card
                                    sx={{
                                        cursor: 'pointer',
                                        border: '2px solid',
                                        borderColor: 'primary.main',
                                        '&:hover': {
                                            boxShadow: 4,
                                            transform: 'translateY(-2px)',
                                            transition: 'all 0.2s'
                                        }
                                    }}
                                    onClick={() => handleScenarioClick(scenario)}
                                >
                                    <CardContent>
                                        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                                            <Typography variant="h6" component="h3" noWrap>
                                                {scenario.title}
                                            </Typography>
                                            <Chip
                                                label={`${Math.round(scenario.personality_match_score * 100)}% match`}
                                                color="primary"
                                                size="small"
                                            />
                                        </Box>
                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                            {scenario.description.substring(0, 100)}...
                                        </Typography>
                                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                                            <Schedule fontSize="small" />
                                            <Typography variant="caption">
                                                {scenario.estimated_duration_minutes} min
                                            </Typography>
                                            <Rating value={scenario.user_rating} readOnly size="small" />
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>
                </Box>
            )}

            {/* Filters */}
            <Box mb={3}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={4}>
                        <TextField
                            fullWidth
                            label="Search scenarios"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            size="small"
                        />
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <FormControl fullWidth size="small">
                            <InputLabel>Category</InputLabel>
                            <Select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                label="Category"
                            >
                                <MenuItem value="">All Categories</MenuItem>
                                {categories.map((cat) => (
                                    <MenuItem key={cat.value} value={cat.value}>
                                        {cat.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <FormControl fullWidth size="small">
                            <InputLabel>Difficulty</InputLabel>
                            <Select
                                value={selectedDifficulty}
                                onChange={(e) => setSelectedDifficulty(e.target.value as number)}
                                label="Difficulty"
                            >
                                <MenuItem value="">All Levels</MenuItem>
                                {difficultyLevels.map((level) => (
                                    <MenuItem key={level.value} value={level.value}>
                                        {level.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                </Grid>
            </Box>

            {/* Scenario Grid */}
            <Grid container spacing={3}>
                {filteredScenarios.map((scenario) => (
                    <Grid item xs={12} md={6} lg={4} key={scenario.id}>
                        <Card
                            sx={{
                                height: '100%',
                                cursor: 'pointer',
                                '&:hover': {
                                    boxShadow: 4,
                                    transform: 'translateY(-2px)',
                                    transition: 'all 0.2s'
                                }
                            }}
                            onClick={() => handleScenarioClick(scenario)}
                        >
                            <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                                    <Typography variant="h6" component="h3">
                                        {scenario.title}
                                    </Typography>
                                    <Chip
                                        label={difficultyLevels.find(l => l.value === scenario.difficulty_level)?.label}
                                        color={getDifficultyColor(scenario.difficulty_level) as any}
                                        size="small"
                                    />
                                </Box>

                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, flexGrow: 1 }}>
                                    {scenario.description}
                                </Typography>

                                <Box mb={2}>
                                    <Typography variant="caption" color="text.secondary">
                                        Category: {categories.find(c => c.value === scenario.category)?.label}
                                    </Typography>
                                </Box>

                                <Box display="flex" flexWrap="wrap" gap={0.5} mb={2}>
                                    {scenario.tags && scenario.tags.slice(0, 3).map((tag) => (
                                        <Chip key={tag} label={tag} size="small" variant="outlined" />
                                    ))}
                                    {scenario.tags && scenario.tags.length > 3 && (
                                        <Chip label={`+${scenario.tags.length - 3} more`} size="small" variant="outlined" />
                                    )}
                                </Box>

                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                    <Box display="flex" alignItems="center" gap={1}>
                                        <Schedule fontSize="small" />
                                        <Typography variant="caption">
                                            {scenario.estimated_duration_minutes} min
                                        </Typography>
                                    </Box>
                                    <Box display="flex" alignItems="center" gap={1}>
                                        <Rating value={scenario.user_rating} readOnly size="small" />
                                        <Typography variant="caption">
                                            ({scenario.usage_count})
                                        </Typography>
                                    </Box>
                                </Box>

                                {scenario.content_warnings && scenario.content_warnings.length > 0 && (
                                    <Box mt={1} display="flex" alignItems="center" gap={1}>
                                        <Warning fontSize="small" color="warning" />
                                        <Typography variant="caption" color="warning.main">
                                            Content warnings apply
                                        </Typography>
                                    </Box>
                                )}
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Scenario Details Dialog */}
            <Dialog
                open={detailsOpen}
                onClose={() => setDetailsOpen(false)}
                maxWidth="md"
                fullWidth
            >
                {selectedScenario && (
                    <>
                        <DialogTitle>
                            <Box display="flex" justifyContent="space-between" alignItems="center">
                                <Typography variant="h5">
                                    {selectedScenario.title}
                                </Typography>
                                <Chip
                                    label={difficultyLevels.find(l => l.value === selectedScenario.difficulty_level)?.label}
                                    color={getDifficultyColor(selectedScenario.difficulty_level) as any}
                                />
                            </Box>
                        </DialogTitle>
                        <DialogContent>
                            <Typography variant="body1" paragraph>
                                {selectedScenario.description}
                            </Typography>

                            <Grid container spacing={2} sx={{ mb: 2 }}>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Category
                                    </Typography>
                                    <Typography variant="body2">
                                        {categories.find(c => c.value === selectedScenario.category)?.label}
                                    </Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Duration
                                    </Typography>
                                    <Typography variant="body2">
                                        {selectedScenario.estimated_duration_minutes} minutes
                                    </Typography>
                                </Grid>
                            </Grid>

                            {selectedScenario.personality_dimensions && selectedScenario.personality_dimensions.length > 0 && (
                                <Box mb={2}>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Personality Dimensions Explored
                                    </Typography>
                                    <Box display="flex" flexWrap="wrap" gap={1}>
                                        {selectedScenario.personality_dimensions.map((dim) => (
                                            <Chip key={dim} label={dim} size="small" color="primary" variant="outlined" />
                                        ))}
                                    </Box>
                                </Box>
                            )}

                            {selectedScenario.value_dimensions && selectedScenario.value_dimensions.length > 0 && (
                                <Box mb={2}>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Values Explored
                                    </Typography>
                                    <Box display="flex" flexWrap="wrap" gap={1}>
                                        {selectedScenario.value_dimensions.map((val) => (
                                            <Chip key={val} label={val} size="small" color="secondary" variant="outlined" />
                                        ))}
                                    </Box>
                                </Box>
                            )}

                            {selectedScenario.content_warnings && selectedScenario.content_warnings.length > 0 && (
                                <Alert severity="warning" sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Content Warnings
                                    </Typography>
                                    <ul>
                                        {selectedScenario.content_warnings.map((warning, index) => (
                                            <li key={index}>{warning}</li>
                                        ))}
                                    </ul>
                                </Alert>
                            )}

                            <Box display="flex" justifyContent="space-between" alignItems="center">
                                <Box display="flex" alignItems="center" gap={2}>
                                    <Rating value={selectedScenario.user_rating} readOnly />
                                    <Typography variant="body2">
                                        {selectedScenario.usage_count} users completed
                                    </Typography>
                                </Box>
                                <Typography variant="body2" color="success.main">
                                    {Math.round(selectedScenario.success_rate * 100)}% success rate
                                </Typography>
                            </Box>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setDetailsOpen(false)}>
                                Cancel
                            </Button>
                            <Button
                                variant="contained"
                                startIcon={<PlayArrow />}
                                onClick={handleStartScenario}
                            >
                                Start Scenario
                            </Button>
                        </DialogActions>
                    </>
                )}
            </Dialog>
        </Box>
    );
};

export default ScenarioLibrary;