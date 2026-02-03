/**
 * Avatar Completeness Analysis Component
 */
import React from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    LinearProgress,
    Alert,
    Button,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Chip,
    Paper
} from '@mui/material';
import {
    CheckCircle as CheckCircleIcon,
    Warning as WarningIcon,
    TrendingUp as TrendingUpIcon,
    Psychology as PsychologyIcon,
    Chat as ChatIcon,
    Favorite as FavoriteIcon,
    EmojiEmotions as EmojiIcon,
    Lightbulb as LightbulbIcon,
    Assignment as AssignmentIcon
} from '@mui/icons-material';

import { AvatarCompletenessAnalysis, AvatarImprovementSuggestion } from '../../types/avatar';

interface AvatarCompletenessProps {
    analysis: AvatarCompletenessAnalysis;
    onImprove?: () => void;
}

const AvatarCompleteness: React.FC<AvatarCompletenessProps> = ({ analysis, onImprove }) => {

    const getScoreColor = (score: number) => {
        if (score >= 0.8) return 'success';
        if (score >= 0.6) return 'warning';
        return 'error';
    };

    const getScoreLabel = (score: number) => {
        if (score >= 0.9) return 'Excellent';
        if (score >= 0.8) return 'Very Good';
        if (score >= 0.7) return 'Good';
        if (score >= 0.6) return 'Fair';
        if (score >= 0.4) return 'Needs Improvement';
        return 'Poor';
    };

    const getCategoryIcon = (category: string) => {
        switch (category) {
            case 'personality_traits': return <PsychologyIcon />;
            case 'communication_patterns': return <ChatIcon />;
            case 'emotional_range': return <FavoriteIcon />;
            case 'conversation_skills': return <EmojiIcon />;
            default: return <AssignmentIcon />;
        }
    };

    const getCategoryTitle = (category: string) => {
        switch (category) {
            case 'personality_traits': return 'Personality Traits';
            case 'communication_patterns': return 'Communication Patterns';
            case 'emotional_range': return 'Emotional Range';
            case 'conversation_skills': return 'Conversation Skills';
            default: return category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
    };

    const getImprovementSuggestions = (): AvatarImprovementSuggestion[] => {
        const suggestions: AvatarImprovementSuggestion[] = [];

        // Analyze each area and create prioritized suggestions
        Object.entries(analysis.areas).forEach(([category, data]) => {
            if (data.score < 0.8) {
                data.suggestions.forEach((suggestion, index) => {
                    suggestions.push({
                        area: getCategoryTitle(category),
                        priority: data.score < 0.5 ? 'high' : data.score < 0.7 ? 'medium' : 'low',
                        action: suggestion,
                        description: `Improve ${getCategoryTitle(category).toLowerCase()}`,
                        estimated_impact: (0.8 - data.score) * 0.5
                    });
                });
            }
        });

        // Add general suggestions
        analysis.suggested_actions.forEach((action) => {
            suggestions.push({
                area: 'General',
                priority: 'medium',
                action: action,
                description: 'General avatar improvement',
                estimated_impact: 0.1
            });
        });

        // Sort by priority and impact
        return suggestions.sort((a, b) => {
            const priorityOrder = { high: 3, medium: 2, low: 1 };
            const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
            if (priorityDiff !== 0) return priorityDiff;
            return b.estimated_impact - a.estimated_impact;
        }).slice(0, 8); // Limit to top 8 suggestions
    };

    const getPriorityColor = (priority: 'high' | 'medium' | 'low') => {
        switch (priority) {
            case 'high': return 'error';
            case 'medium': return 'warning';
            case 'low': return 'info';
        }
    };

    const renderOverallScore = () => (
        <Card sx={{ mb: 3 }}>
            <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <TrendingUpIcon color="primary" sx={{ fontSize: 32 }} />
                    <Box>
                        <Typography variant="h5" component="h2">
                            Avatar Completeness
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Overall assessment of your AI avatar's development
                        </Typography>
                    </Box>
                </Box>

                <Grid container spacing={3}>
                    <Grid item xs={12} sm={4}>
                        <Box textAlign="center">
                            <Typography variant="h3" color={`${getScoreColor(analysis.overall_score)}.main`} fontWeight="bold">
                                {Math.round(analysis.overall_score * 100)}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Overall Score
                            </Typography>
                            <Chip
                                label={getScoreLabel(analysis.overall_score)}
                                color={getScoreColor(analysis.overall_score) as any}
                                size="small"
                                sx={{ mt: 1 }}
                            />
                        </Box>
                    </Grid>

                    <Grid item xs={12} sm={4}>
                        <Box textAlign="center">
                            <Typography variant="h3" color="secondary.main" fontWeight="bold">
                                {Math.round(analysis.authenticity_score * 100)}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Authenticity
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                                How true to your personality
                            </Typography>
                        </Box>
                    </Grid>

                    <Grid item xs={12} sm={4}>
                        <Box textAlign="center">
                            <Typography variant="h3" color="info.main" fontWeight="bold">
                                {Math.round(analysis.consistency_score * 100)}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Consistency
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                                Reliable behavior patterns
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
    );

    const renderAreaAnalysis = () => (
        <Grid container spacing={3} sx={{ mb: 3 }}>
            {Object.entries(analysis.areas).map(([category, data]) => (
                <Grid item xs={12} sm={6} md={3} key={category}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                                {getCategoryIcon(category)}
                                <Typography variant="h6" component="h3" fontSize="1rem">
                                    {getCategoryTitle(category)}
                                </Typography>
                            </Box>

                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                                <LinearProgress
                                    variant="determinate"
                                    value={data.score * 100}
                                    color={getScoreColor(data.score) as any}
                                    sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                                />
                                <Typography variant="body2" fontWeight="bold">
                                    {Math.round(data.score * 100)}%
                                </Typography>
                            </Box>

                            {data.missing.length > 0 && (
                                <Box>
                                    <Typography variant="caption" color="text.secondary" gutterBottom>
                                        Missing:
                                    </Typography>
                                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                                        {data.missing.slice(0, 3).map((item) => (
                                            <Chip
                                                key={item}
                                                label={item}
                                                size="small"
                                                variant="outlined"
                                                color="warning"
                                                sx={{ fontSize: '0.7rem', height: 20 }}
                                            />
                                        ))}
                                        {data.missing.length > 3 && (
                                            <Chip
                                                label={`+${data.missing.length - 3} more`}
                                                size="small"
                                                variant="outlined"
                                                color="warning"
                                                sx={{ fontSize: '0.7rem', height: 20 }}
                                            />
                                        )}
                                    </Box>
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );

    const renderImprovementSuggestions = () => {
        const suggestions = getImprovementSuggestions();

        if (suggestions.length === 0) {
            return (
                <Alert severity="success" sx={{ mb: 3 }}>
                    <Typography variant="body2">
                        Great job! Your avatar is well-developed. Continue using it in conversations to improve authenticity and consistency.
                    </Typography>
                </Alert>
            );
        }

        return (
            <Card>
                <CardContent>
                    <Box display="flex" alignItems="center" gap={1} mb={2}>
                        <LightbulbIcon color="primary" />
                        <Typography variant="h6" component="h3">
                            Improvement Suggestions
                        </Typography>
                    </Box>

                    <Typography variant="body2" color="text.secondary" paragraph>
                        Here are personalized suggestions to improve your avatar's completeness and authenticity:
                    </Typography>

                    <List>
                        {suggestions.map((suggestion, index) => (
                            <ListItem key={index} sx={{ px: 0 }}>
                                <ListItemIcon>
                                    <Chip
                                        label={suggestion.priority.toUpperCase()}
                                        size="small"
                                        color={getPriorityColor(suggestion.priority) as any}
                                        variant="outlined"
                                    />
                                </ListItemIcon>
                                <ListItemText
                                    primary={suggestion.action}
                                    secondary={`${suggestion.area} • Est. impact: +${Math.round(suggestion.estimated_impact * 100)}%`}
                                    primaryTypographyProps={{ variant: 'body2' }}
                                    secondaryTypographyProps={{ variant: 'caption', color: 'text.secondary' }}
                                />
                            </ListItem>
                        ))}
                    </List>

                    {onImprove && (
                        <Box mt={2}>
                            <Button
                                variant="contained"
                                onClick={onImprove}
                                startIcon={<AssignmentIcon />}
                            >
                                Start Improving
                            </Button>
                        </Box>
                    )}
                </CardContent>
            </Card>
        );
    };

    const renderTrainingStatus = () => (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
            <Typography variant="subtitle2" gutterBottom>
                Training Status
            </Typography>
            <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                        Training Sessions: <strong>{analysis.training_status.iterations}</strong>
                    </Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                        Status: <strong>{analysis.training_status.status}</strong>
                    </Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                        Last Training: <strong>
                            {analysis.training_status.last_training
                                ? new Date(analysis.training_status.last_training).toLocaleDateString()
                                : 'Never'
                            }
                        </strong>
                    </Typography>
                </Grid>
            </Grid>
        </Paper>
    );

    return (
        <Box>
            {renderOverallScore()}
            {renderTrainingStatus()}
            {renderAreaAnalysis()}
            {renderImprovementSuggestions()}
        </Box>
    );
};

export default AvatarCompleteness;