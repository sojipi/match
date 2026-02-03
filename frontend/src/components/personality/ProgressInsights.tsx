/**
 * Progress Insights Component
 * Shows real-time personality insights during assessment
 */
import React from 'react';
import {
    Card,
    CardContent,
    Typography,
    Box,
    LinearProgress,
    Chip,
    Stack,
    Avatar
} from '@mui/material';
import { motion } from 'framer-motion';
import {
    Psychology,
    TrendingUp,
    Groups,
    Favorite,
    Work,
    Star
} from '@mui/icons-material';
import { PersonalityInsight } from '../../types/personality';

interface ProgressInsightsProps {
    insights: PersonalityInsight[];
}

const ProgressInsights: React.FC<ProgressInsightsProps> = ({ insights }) => {
    const getTraitIcon = (trait: string) => {
        const traitLower = trait.toLowerCase();
        switch (traitLower) {
            case 'openness': return <Psychology />;
            case 'conscientiousness': return <Work />;
            case 'extraversion': return <Groups />;
            case 'agreeableness': return <Favorite />;
            case 'neuroticism': return <TrendingUp />;
            default: return <Star />;
        }
    };

    const getTraitColor = (trait: string) => {
        const traitLower = trait.toLowerCase();
        switch (traitLower) {
            case 'openness': return '#9c27b0';
            case 'conscientiousness': return '#2196f3';
            case 'extraversion': return '#ff9800';
            case 'agreeableness': return '#4caf50';
            case 'neuroticism': return '#f44336';
            default: return '#757575';
        }
    };

    const getScoreLabel = (score: number) => {
        if (score >= 0.8) return 'Very High';
        if (score >= 0.6) return 'High';
        if (score >= 0.4) return 'Moderate';
        if (score >= 0.2) return 'Low';
        return 'Very Low';
    };

    if (insights.length === 0) {
        return null;
    }

    return (
        <Card sx={{ mb: 3, bgcolor: 'primary.50' }}>
            <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <Psychology sx={{ mr: 1 }} />
                    Your Personality Insights
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Based on your responses so far, here's what we're learning about you:
                </Typography>

                <Stack spacing={2}>
                    {insights.map((insight, index) => (
                        <motion.div
                            key={insight.trait}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                        >
                            <Box
                                sx={{
                                    p: 2,
                                    bgcolor: 'background.paper',
                                    borderRadius: 1,
                                    border: 1,
                                    borderColor: 'divider'
                                }}
                            >
                                <Box display="flex" alignItems="center" mb={1}>
                                    <Avatar
                                        sx={{
                                            bgcolor: getTraitColor(insight.trait),
                                            width: 32,
                                            height: 32,
                                            mr: 2
                                        }}
                                    >
                                        {getTraitIcon(insight.trait)}
                                    </Avatar>
                                    <Box flexGrow={1}>
                                        <Typography variant="subtitle2" fontWeight="bold">
                                            {insight.trait}
                                        </Typography>
                                        <Box display="flex" alignItems="center" gap={1}>
                                            <Chip
                                                label={getScoreLabel(insight.score)}
                                                size="small"
                                                sx={{
                                                    bgcolor: getTraitColor(insight.trait),
                                                    color: 'white',
                                                    fontSize: '0.75rem'
                                                }}
                                            />
                                            <Typography variant="caption" color="text.secondary">
                                                {Math.round(insight.confidence * 100)}% confidence
                                            </Typography>
                                        </Box>
                                    </Box>
                                </Box>

                                <Box sx={{ mb: 1 }}>
                                    <LinearProgress
                                        variant="determinate"
                                        value={insight.score * 100}
                                        sx={{
                                            height: 6,
                                            borderRadius: 3,
                                            bgcolor: 'grey.200',
                                            '& .MuiLinearProgress-bar': {
                                                bgcolor: getTraitColor(insight.trait)
                                            }
                                        }}
                                    />
                                </Box>

                                <Typography variant="body2" color="text.secondary">
                                    {insight.description}
                                </Typography>
                            </Box>
                        </motion.div>
                    ))}
                </Stack>

                <Box sx={{ mt: 2, p: 1, bgcolor: 'info.50', borderRadius: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                        💡 These insights will become more accurate as you complete more questions.
                        Your final personality profile will be much more detailed!
                    </Typography>
                </Box>
            </CardContent>
        </Card>
    );
};

export default ProgressInsights;