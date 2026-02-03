import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Button,
    Grid,
    Alert,
    LinearProgress,
    Chip,
    Stack
} from '@mui/material';
import {
    Psychology,
    TrendingUp,
    Groups,
    Assessment
} from '@mui/icons-material';
import { useAppSelector } from '../hooks/redux';
import { personalityApi } from '../services/personalityApi';
import { PersonalityProfile, AssessmentProgress } from '../types/personality';

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const { user } = useAppSelector(state => state.auth);
    const [personalityProfile, setPersonalityProfile] = useState<PersonalityProfile | null>(null);
    const [assessmentProgress, setAssessmentProgress] = useState<AssessmentProgress | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (user) {
            loadUserData();
        }
    }, [user]);

    const loadUserData = async () => {
        if (!user) return;

        try {
            setIsLoading(true);

            // Try to load existing personality profile
            try {
                const profile = await personalityApi.getProfile(user.id);
                setPersonalityProfile(profile);
            } catch (error) {
                // Profile doesn't exist yet, that's okay
                console.log('No personality profile found');
            }

            // Load assessment progress
            try {
                const progress = await personalityApi.getProgress(user.id);
                setAssessmentProgress(progress);
            } catch (error) {
                console.error('Failed to load assessment progress:', error);
            }
        } catch (error) {
            console.error('Failed to load user data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleStartAssessment = () => {
        navigate('/personality-assessment');
    };

    const getPersonalityStatus = () => {
        if (!personalityProfile) {
            return {
                status: 'not_started',
                message: 'Start your personality assessment to unlock AI matchmaking',
                color: 'warning' as const,
                action: 'Start Assessment'
            };
        }

        if (personalityProfile.completeness_score < 0.8) {
            return {
                status: 'incomplete',
                message: `Your profile is ${Math.round(personalityProfile.completeness_score * 100)}% complete`,
                color: 'info' as const,
                action: 'Complete Assessment'
            };
        }

        return {
            status: 'complete',
            message: 'Your personality profile is complete and ready for matching!',
            color: 'success' as const,
            action: 'View Profile'
        };
    };

    if (isLoading) {
        return (
            <Box p={3}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Dashboard
                </Typography>
                <LinearProgress sx={{ mt: 2 }} />
            </Box>
        );
    }

    const personalityStatus = getPersonalityStatus();

    return (
        <Box p={3}>
            <Typography variant="h4" component="h1" gutterBottom>
                Welcome back, {user?.first_name || 'there'}!
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
                Your AI-powered matchmaking dashboard. Complete your personality assessment
                to start finding compatible matches.
            </Typography>

            <Grid container spacing={3}>
                {/* Personality Assessment Card */}
                <Grid item xs={12} md={8}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <Psychology color="primary" sx={{ mr: 2 }} />
                                <Typography variant="h6">
                                    Personality Assessment
                                </Typography>
                            </Box>

                            <Alert severity={personalityStatus.color} sx={{ mb: 2 }}>
                                {personalityStatus.message}
                            </Alert>

                            {personalityProfile && (
                                <Box mb={2}>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        Profile Completeness
                                    </Typography>
                                    <LinearProgress
                                        variant="determinate"
                                        value={personalityProfile.completeness_score * 100}
                                        sx={{ height: 8, borderRadius: 4, mb: 1 }}
                                    />
                                    <Typography variant="caption" color="text.secondary">
                                        {Math.round(personalityProfile.completeness_score * 100)}% complete
                                    </Typography>
                                </Box>
                            )}

                            {assessmentProgress && assessmentProgress.insights.length > 0 && (
                                <Box mb={2}>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        Current Insights
                                    </Typography>
                                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                                        {assessmentProgress.insights.slice(0, 3).map((insight) => (
                                            <Chip
                                                key={insight.trait}
                                                label={`${insight.trait}: ${Math.round(insight.score * 100)}%`}
                                                size="small"
                                                color="primary"
                                                variant="outlined"
                                            />
                                        ))}
                                    </Stack>
                                </Box>
                            )}

                            <Button
                                variant="contained"
                                onClick={handleStartAssessment}
                                startIcon={<Assessment />}
                                size="large"
                            >
                                {personalityStatus.action}
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>

                {/* AI Avatar Management Card */}
                <Grid item xs={12} md={8}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <Psychology color="primary" sx={{ mr: 2 }} />
                                <Typography variant="h6">
                                    AI Avatar
                                </Typography>
                            </Box>

                            <Typography variant="body2" color="text.secondary" paragraph>
                                Your AI avatar represents your personality in conversations and matchmaking.
                                Create and customize your avatar to ensure authentic interactions.
                            </Typography>

                            <Button
                                variant="outlined"
                                onClick={() => navigate('/avatar')}
                                startIcon={<Psychology />}
                                size="large"
                            >
                                Manage Avatar
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Quick Stats */}
                <Grid item xs={12} md={4}>
                    <Stack spacing={2}>
                        <Card>
                            <CardContent>
                                <Box display="flex" alignItems="center">
                                    <Groups color="primary" sx={{ mr: 2 }} />
                                    <Box>
                                        <Typography variant="h4">0</Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Potential Matches
                                        </Typography>
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent>
                                <Box display="flex" alignItems="center">
                                    <TrendingUp color="primary" sx={{ mr: 2 }} />
                                    <Box>
                                        <Typography variant="h4">0</Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            AI Conversations
                                        </Typography>
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>
                    </Stack>
                </Grid>

                {/* Coming Soon Features */}
                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Coming Soon
                            </Typography>
                            <Typography variant="body2" color="text.secondary" paragraph>
                                Once you complete your personality assessment, you'll unlock:
                            </Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Box textAlign="center" p={2}>
                                        <Groups sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                        <Typography variant="subtitle2">Match Discovery</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Find compatible partners
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Box textAlign="center" p={2}>
                                        <Psychology sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                        <Typography variant="subtitle2">AI Conversations</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Watch AI avatars interact
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Box textAlign="center" p={2}>
                                        <Assessment sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                        <Typography variant="subtitle2">Compatibility Reports</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Detailed relationship insights
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Box textAlign="center" p={2}>
                                        <TrendingUp sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                        <Typography variant="subtitle2">Relationship Simulations</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Test compatibility scenarios
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard;