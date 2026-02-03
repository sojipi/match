/**
 * Personality Visualization Component
 * Shows personality profile in visual format
 */
import React from 'react';
import {
    Card,
    CardContent,
    Typography,
    Box,
    Grid,
    LinearProgress,
    Avatar,
    Chip,
    Stack,
    Divider
} from '@mui/material';
import { motion } from 'framer-motion';
import {
    Psychology,
    Work,
    Groups,
    Favorite,
    TrendingUp,
    Star,
    Chat,
    Handshake
} from '@mui/icons-material';
import { PersonalityProfile } from '../../types/personality';

interface PersonalityVisualizationProps {
    profile: PersonalityProfile;
    showDetails?: boolean;
}

const PersonalityVisualization: React.FC<PersonalityVisualizationProps> = ({
    profile,
    showDetails = true
}) => {
    const bigFiveTraits = [
        {
            key: 'openness',
            label: 'Openness',
            description: 'Openness to new experiences and ideas',
            icon: <Psychology />,
            color: '#9c27b0',
            value: profile.openness || 0
        },
        {
            key: 'conscientiousness',
            label: 'Conscientiousness',
            description: 'Organization, responsibility, and self-discipline',
            icon: <Work />,
            color: '#2196f3',
            value: profile.conscientiousness || 0
        },
        {
            key: 'extraversion',
            label: 'Extraversion',
            description: 'Social energy and outgoingness',
            icon: <Groups />,
            color: '#ff9800',
            value: profile.extraversion || 0
        },
        {
            key: 'agreeableness',
            label: 'Agreeableness',
            description: 'Cooperation and trust in others',
            icon: <Favorite />,
            color: '#4caf50',
            value: profile.agreeableness || 0
        },
        {
            key: 'neuroticism',
            label: 'Emotional Stability',
            description: 'Emotional resilience and stability',
            icon: <TrendingUp />,
            color: '#f44336',
            value: profile.neuroticism ? 1 - profile.neuroticism : 0 // Invert for stability
        }
    ];

    const getScoreLabel = (score: number) => {
        if (score >= 0.8) return 'Very High';
        if (score >= 0.6) return 'High';
        if (score >= 0.4) return 'Moderate';
        if (score >= 0.2) return 'Low';
        return 'Very Low';
    };

    const getScoreColor = (score: number) => {
        if (score >= 0.7) return 'success';
        if (score >= 0.4) return 'warning';
        return 'error';
    };

    const topValues = Object.entries(profile.values || {})
        .sort(([, a], [, b]) => (b as number) - (a as number))
        .slice(0, 3);

    return (
        <Card>
            <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                    <Typography variant="h5" component="h2">
                        Your Personality Profile
                    </Typography>
                    <Chip
                        label={`${Math.round(profile.completeness_score * 100)}% Complete`}
                        color={profile.completeness_score >= 0.8 ? 'success' : 'warning'}
                        variant="outlined"
                    />
                </Box>

                {/* Big Five Traits */}
                <Typography variant="h6" gutterBottom sx={{ mt: 3, mb: 2 }}>
                    Personality Dimensions
                </Typography>

                <Grid container spacing={2}>
                    {bigFiveTraits.map((trait, index) => (
                        <Grid item xs={12} sm={6} key={trait.key}>
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: index * 0.1 }}
                            >
                                <Box
                                    sx={{
                                        p: 2,
                                        border: 1,
                                        borderColor: 'divider',
                                        borderRadius: 1,
                                        height: '100%'
                                    }}
                                >
                                    <Box display="flex" alignItems="center" mb={1}>
                                        <Avatar
                                            sx={{
                                                bgcolor: trait.color,
                                                width: 32,
                                                height: 32,
                                                mr: 2
                                            }}
                                        >
                                            {trait.icon}
                                        </Avatar>
                                        <Box flexGrow={1}>
                                            <Typography variant="subtitle2" fontWeight="bold">
                                                {trait.label}
                                            </Typography>
                                            <Chip
                                                label={getScoreLabel(trait.value)}
                                                size="small"
                                                color={getScoreColor(trait.value) as any}
                                                variant="outlined"
                                            />
                                        </Box>
                                    </Box>

                                    <Box sx={{ mb: 1 }}>
                                        <LinearProgress
                                            variant="determinate"
                                            value={trait.value * 100}
                                            sx={{
                                                height: 8,
                                                borderRadius: 4,
                                                bgcolor: 'grey.200',
                                                '& .MuiLinearProgress-bar': {
                                                    bgcolor: trait.color
                                                }
                                            }}
                                        />
                                    </Box>

                                    {showDetails && (
                                        <Typography variant="caption" color="text.secondary">
                                            {trait.description}
                                        </Typography>
                                    )}
                                </Box>
                            </motion.div>
                        </Grid>
                    ))}
                </Grid>

                {/* Values Section */}
                {topValues.length > 0 && (
                    <>
                        <Divider sx={{ my: 3 }} />
                        <Typography variant="h6" gutterBottom>
                            Top Values
                        </Typography>
                        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                            {topValues.map(([value, importance], index) => (
                                <motion.div
                                    key={value}
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ duration: 0.3, delay: index * 0.1 }}
                                >
                                    <Chip
                                        icon={<Star />}
                                        label={`${value} (${Math.round((importance as number) * 100)}%)`}
                                        color="primary"
                                        variant="outlined"
                                        sx={{ mb: 1 }}
                                    />
                                </motion.div>
                            ))}
                        </Stack>
                    </>
                )}

                {/* Communication & Conflict Resolution */}
                {(profile.communication_style || profile.conflict_resolution_style) && (
                    <>
                        <Divider sx={{ my: 3 }} />
                        <Typography variant="h6" gutterBottom>
                            Communication Style
                        </Typography>
                        <Grid container spacing={2}>
                            {profile.communication_style && (
                                <Grid item xs={12} sm={6}>
                                    <Box display="flex" alignItems="center">
                                        <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                                            <Chat />
                                        </Avatar>
                                        <Box>
                                            <Typography variant="subtitle2" color="text.secondary">
                                                Communication
                                            </Typography>
                                            <Typography variant="body2">
                                                {profile.communication_style}
                                            </Typography>
                                        </Box>
                                    </Box>
                                </Grid>
                            )}
                            {profile.conflict_resolution_style && (
                                <Grid item xs={12} sm={6}>
                                    <Box display="flex" alignItems="center">
                                        <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                                            <Handshake />
                                        </Avatar>
                                        <Box>
                                            <Typography variant="subtitle2" color="text.secondary">
                                                Conflict Resolution
                                            </Typography>
                                            <Typography variant="body2">
                                                {profile.conflict_resolution_style}
                                            </Typography>
                                        </Box>
                                    </Box>
                                </Grid>
                            )}
                        </Grid>
                    </>
                )}

                {/* Profile Completeness */}
                {profile.completeness_score < 1.0 && (
                    <Box sx={{ mt: 3, p: 2, bgcolor: 'info.50', borderRadius: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                            💡 Complete more assessment questions to get a more detailed personality profile
                            and better match recommendations.
                        </Typography>
                    </Box>
                )}
            </CardContent>
        </Card>
    );
};

export default PersonalityVisualization;