/**
 * Avatar Visualization Component
 */
import React from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Chip,
    LinearProgress,
    Paper,
    List,
    ListItem,
    ListItemIcon,
    ListItemText
} from '@mui/material';
import {
    Psychology as PsychologyIcon,
    Chat as ChatIcon,
    Favorite as FavoriteIcon,
    EmojiEmotions as EmojiIcon,
    Star as StarIcon,
    TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

import { AIAvatar, AvatarVisualization as AvatarVizData } from '../../types/avatar';

interface AvatarVisualizationProps {
    avatar: AIAvatar;
}

const AvatarVisualization: React.FC<AvatarVisualizationProps> = ({ avatar }) => {

    const getPersonalityVisualizations = (): AvatarVizData[] => {
        const bigFive = avatar.personality_traits?.big_five || {};

        return [
            {
                trait: 'Openness',
                score: bigFive.openness || 0.5,
                label: 'Open to Experience',
                description: 'Creativity, curiosity, and openness to new ideas',
                color: '#FF6B6B',
                category: 'personality'
            },
            {
                trait: 'Conscientiousness',
                score: bigFive.conscientiousness || 0.5,
                label: 'Conscientiousness',
                description: 'Organization, responsibility, and self-discipline',
                color: '#4ECDC4',
                category: 'personality'
            },
            {
                trait: 'Extraversion',
                score: bigFive.extraversion || 0.5,
                label: 'Extraversion',
                description: 'Social energy and outgoing nature',
                color: '#45B7D1',
                category: 'personality'
            },
            {
                trait: 'Agreeableness',
                score: bigFive.agreeableness || 0.5,
                label: 'Agreeableness',
                description: 'Cooperation, trust, and empathy',
                color: '#96CEB4',
                category: 'personality'
            },
            {
                trait: 'Neuroticism',
                score: bigFive.neuroticism || 0.5,
                label: 'Emotional Sensitivity',
                description: 'Emotional reactivity and stress sensitivity',
                color: '#FFEAA7',
                category: 'personality'
            }
        ];
    };

    const getCommunicationVisualizations = (): AvatarVizData[] => {
        const patterns = avatar.communication_patterns || {};

        return [
            {
                trait: 'Directness',
                score: patterns.directness || 0.5,
                label: 'Communication Directness',
                description: 'How direct and straightforward in communication',
                color: '#FF7675',
                category: 'communication'
            },
            {
                trait: 'Emotional Expression',
                score: patterns.emotional_expression || 0.5,
                label: 'Emotional Expression',
                description: 'How openly emotions are expressed',
                color: '#FD79A8',
                category: 'communication'
            },
            {
                trait: 'Assertiveness',
                score: avatar.response_style?.assertiveness || 0.5,
                label: 'Assertiveness',
                description: 'Confidence in expressing opinions and needs',
                color: '#FDCB6E',
                category: 'communication'
            }
        ];
    };

    const getEmotionalVisualizations = (): AvatarVizData[] => {
        const emotional = avatar.emotional_range || {};

        return [
            {
                trait: 'Expressiveness',
                score: emotional.expressiveness || 0.5,
                label: 'Emotional Expressiveness',
                description: 'How openly emotions are shown',
                color: '#E17055',
                category: 'emotional'
            },
            {
                trait: 'Stability',
                score: emotional.emotional_stability || 0.5,
                label: 'Emotional Stability',
                description: 'Ability to remain calm under pressure',
                color: '#00B894',
                category: 'emotional'
            },
            {
                trait: 'Empathy',
                score: emotional.empathy || 0.5,
                label: 'Empathy',
                description: 'Understanding and sharing others\' feelings',
                color: '#00CEC9',
                category: 'emotional'
            }
        ];
    };

    const getSkillsVisualizations = (): AvatarVizData[] => {
        const skills = avatar.conversation_skills || {};

        return [
            {
                trait: 'Topic Initiation',
                score: skills.topic_initiation || 0.5,
                label: 'Starting Conversations',
                description: 'Ability to initiate new topics',
                color: '#A29BFE',
                category: 'skills'
            },
            {
                trait: 'Emotional Support',
                score: skills.emotional_support || 0.5,
                label: 'Emotional Support',
                description: 'Providing comfort and understanding',
                color: '#FD79A8',
                category: 'skills'
            },
            {
                trait: 'Conflict Resolution',
                score: skills.conflict_resolution || 0.5,
                label: 'Conflict Resolution',
                description: 'Handling disagreements constructively',
                color: '#FDCB6E',
                category: 'skills'
            }
        ];
    };

    const renderVisualizationCard = (title: string, icon: React.ReactNode, visualizations: AvatarVizData[]) => (
        <Card>
            <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                    {icon}
                    <Typography variant="h6" component="h3">
                        {title}
                    </Typography>
                </Box>

                <Box>
                    {visualizations.map((viz) => (
                        <Box key={viz.trait} mb={2}>
                            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                                <Typography variant="body2" fontWeight="medium">
                                    {viz.label}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {Math.round(viz.score * 100)}%
                                </Typography>
                            </Box>

                            <LinearProgress
                                variant="determinate"
                                value={viz.score * 100}
                                sx={{
                                    height: 8,
                                    borderRadius: 4,
                                    backgroundColor: 'grey.200',
                                    '& .MuiLinearProgress-bar': {
                                        backgroundColor: viz.color,
                                        borderRadius: 4
                                    }
                                }}
                            />

                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                                {viz.description}
                            </Typography>
                        </Box>
                    ))}
                </Box>
            </CardContent>
        </Card>
    );

    const renderValues = () => {
        const values = avatar.personality_traits?.values || {};

        if (Object.keys(values).length === 0) {
            return (
                <Typography variant="body2" color="text.secondary" style={{ fontStyle: 'italic' }}>
                    No values defined yet. Complete more personality assessment questions.
                </Typography>
            );
        }

        const sortedValues = Object.entries(values)
            .sort(([, a], [, b]) => (b as number) - (a as number))
            .slice(0, 6);

        return (
            <Box>
                {sortedValues.map(([value, importance], index) => (
                    <Box key={value} display="flex" alignItems="center" gap={1} mb={1}>
                        <Chip
                            label={`#${index + 1}`}
                            size="small"
                            color="primary"
                            variant="outlined"
                        />
                        <Typography variant="body2" sx={{ flexGrow: 1 }}>
                            {value}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={0.5}>
                            {Array.from({ length: 5 }, (_, i) => (
                                <StarIcon
                                    key={i}
                                    sx={{
                                        fontSize: 16,
                                        color: i < (importance as number) * 5 ? 'gold' : 'grey.300'
                                    }}
                                />
                            ))}
                        </Box>
                    </Box>
                ))}
            </Box>
        );
    };

    const renderCommunicationStyle = () => {
        const patterns = avatar.communication_patterns || {};
        const responseStyle = avatar.response_style || {};

        const styles = [
            { label: 'Communication Style', value: patterns.style || 'Not defined' },
            { label: 'Listening Style', value: patterns.listening_style || 'Not defined' },
            { label: 'Humor Usage', value: patterns.humor_usage || 'Not defined' },
            { label: 'Response Length', value: responseStyle.response_length || 'Not defined' },
            { label: 'Formality Level', value: responseStyle.formality_level || 'Not defined' },
            { label: 'Conflict Approach', value: patterns.conflict_approach || 'Not defined' }
        ];

        return (
            <List dense>
                {styles.map((style) => (
                    <ListItem key={style.label} sx={{ px: 0 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                            <ChatIcon sx={{ fontSize: 20, color: 'text.secondary' }} />
                        </ListItemIcon>
                        <ListItemText
                            primary={style.label}
                            secondary={style.value}
                            primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                            secondaryTypographyProps={{ variant: 'body2' }}
                        />
                    </ListItem>
                ))}
            </List>
        );
    };

    return (
        <Box>
            <Grid container spacing={3}>
                {/* Personality Traits */}
                <Grid item xs={12} md={6}>
                    {renderVisualizationCard(
                        'Personality Traits',
                        <PsychologyIcon color="primary" />,
                        getPersonalityVisualizations()
                    )}
                </Grid>

                {/* Communication Patterns */}
                <Grid item xs={12} md={6}>
                    {renderVisualizationCard(
                        'Communication Style',
                        <ChatIcon color="primary" />,
                        getCommunicationVisualizations()
                    )}
                </Grid>

                {/* Emotional Range */}
                <Grid item xs={12} md={6}>
                    {renderVisualizationCard(
                        'Emotional Range',
                        <FavoriteIcon color="primary" />,
                        getEmotionalVisualizations()
                    )}
                </Grid>

                {/* Conversation Skills */}
                <Grid item xs={12} md={6}>
                    {renderVisualizationCard(
                        'Conversation Skills',
                        <EmojiIcon color="primary" />,
                        getSkillsVisualizations()
                    )}
                </Grid>

                {/* Core Values */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                                <StarIcon color="primary" />
                                <Typography variant="h6" component="h3">
                                    Core Values
                                </Typography>
                            </Box>
                            {renderValues()}
                        </CardContent>
                    </Card>
                </Grid>

                {/* Communication Details */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                                <ChatIcon color="primary" />
                                <Typography variant="h6" component="h3">
                                    Communication Details
                                </Typography>
                            </Box>
                            {renderCommunicationStyle()}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default AvatarVisualization;