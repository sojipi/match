import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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
    Stack,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Divider,
    Paper,
    IconButton,
    Tooltip
} from '@mui/material';
import {
    Psychology,
    TrendingUp,
    Groups,
    Assessment,
    Chat,
    Notifications,
    ArrowForward,
    CheckCircle,
    Info,
    PhotoCamera,
    Edit,
    Explore,
    Timeline
} from '@mui/icons-material';
import { useAppSelector } from '../hooks/redux';
import { personalityApi } from '../services/personalityApi';
import { PersonalityProfile, AssessmentProgress } from '../types/personality';
import api from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

interface DashboardStats {
    total_matches: number;
    active_conversations: number;
    compatibility_reports: number;
    ai_sessions: number;
    unread_notifications: number;
}

interface ActivityItem {
    type: string;
    message: string;
    timestamp: string;
    match_id?: string;
    session_id?: string;
}

interface CompatibilityTrend {
    week: string;
    avg_score: number;
}

interface Recommendation {
    type: string;
    priority: string;
    message: string;
    action_url: string;
}

interface DashboardData {
    stats: DashboardStats;
    activity_feed: ActivityItem[];
    compatibility_trends: CompatibilityTrend[];
    recommendations: Recommendation[];
    profile_completeness: number;
}

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const { user } = useAppSelector(state => state.auth);
    const [personalityProfile, setPersonalityProfile] = useState<PersonalityProfile | null>(null);
    const [assessmentProgress, setAssessmentProgress] = useState<AssessmentProgress | null>(null);
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
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

            // Load dashboard data
            try {
                const response = await api.get('/api/v1/users/dashboard');
                setDashboardData(response);
            } catch (error) {
                console.error('Failed to load dashboard data:', error);
            }

            // Try to load existing personality profile
            try {
                const profile = await personalityApi.getProfile(user.id);
                setPersonalityProfile(profile);
            } catch (error) {
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

    const handleRecommendationClick = (actionUrl: string) => {
        navigate(actionUrl);
    };

    const getPersonalityStatus = () => {
        const completeness = dashboardData?.profile_completeness || 0;

        if (completeness === 0) {
            return {
                status: 'not_started',
                message: t('dashboard.status.notStarted'),
                color: 'warning' as const,
                action: t('dashboard.actions.startAssessment')
            };
        }

        if (completeness < 0.8) {
            return {
                status: 'incomplete',
                message: t('dashboard.status.incomplete', { percent: Math.round(completeness * 100) }),
                color: 'info' as const,
                action: t('dashboard.actions.completeAssessment')
            };
        }

        return {
            status: 'complete',
            message: t('dashboard.status.complete'),
            color: 'success' as const,
            action: t('dashboard.actions.viewProfile')
        };
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high':
                return 'error';
            case 'medium':
                return 'warning';
            case 'low':
                return 'info';
            default:
                return 'default';
        }
    };

    const getActivityIcon = (type: string) => {
        switch (type) {
            case 'match':
                return <Groups color="primary" />;
            case 'session_completed':
                return <Psychology color="success" />;
            case 'message':
                return <Chat color="info" />;
            default:
                return <Info />;
        }
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return t('dashboard.time.justNow');
        if (diffMins < 60) return t('dashboard.time.minutesAgo', { minutes: diffMins });
        if (diffHours < 24) return t('dashboard.time.hoursAgo', { hours: diffHours });
        if (diffDays < 7) return t('dashboard.time.daysAgo', { days: diffDays });
        return date.toLocaleDateString();
    };

    if (isLoading) {
        return (
            <Box p={3}>
                <Typography variant="h4" component="h1" gutterBottom>
                    {t('navigation.dashboard')}
                </Typography>
                <LinearProgress sx={{ mt: 2 }} />
            </Box>
        );
    }

    const personalityStatus = getPersonalityStatus();
    const stats = dashboardData?.stats || {
        total_matches: 0,
        active_conversations: 0,
        compatibility_reports: 0,
        ai_sessions: 0,
        unread_notifications: 0
    };

    return (
        <Box p={3}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                    <Typography variant="h4" component="h1" gutterBottom>
                        {t('dashboard.welcome', { name: user?.first_name || '' })}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        {t('dashboard.subtitle')}
                    </Typography>
                </Box>
                {stats.unread_notifications > 0 && (
                    <Tooltip title={t('notifications.title')}>
                        <IconButton onClick={() => navigate('/notifications')} color="primary">
                            <Notifications />
                            <Chip
                                label={stats.unread_notifications}
                                size="small"
                                color="error"
                                sx={{ ml: 1 }}
                            />
                        </IconButton>
                    </Tooltip>
                )}
            </Box>

            <Grid container spacing={3}>
                {/* Quick Stats */}
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography variant="h4">{stats.total_matches}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {t('dashboard.stats.totalMatches')}
                                    </Typography>
                                </Box>
                                <Groups color="primary" sx={{ fontSize: 40 }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography variant="h4">{stats.active_conversations}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {t('dashboard.stats.activeChats')}
                                    </Typography>
                                </Box>
                                <Chat color="primary" sx={{ fontSize: 40 }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography variant="h4">{stats.ai_sessions}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {t('dashboard.stats.aiSessions')}
                                    </Typography>
                                </Box>
                                <Psychology color="primary" sx={{ fontSize: 40 }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography variant="h4">{stats.compatibility_reports}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {t('dashboard.stats.reports')}
                                    </Typography>
                                </Box>
                                <Assessment color="primary" sx={{ fontSize: 40 }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Personality Assessment Card */}
                <Grid item xs={12} md={8}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <Psychology color="primary" sx={{ mr: 2 }} />
                                <Typography variant="h6">
                                    {t('dashboard.personalityAssessment')}
                                </Typography>
                            </Box>

                            <Alert severity={personalityStatus.color} sx={{ mb: 2 }}>
                                {personalityStatus.message}
                            </Alert>

                            {dashboardData && dashboardData.profile_completeness > 0 && (
                                <Box mb={2}>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        {t('dashboard.profileCompleteness')}
                                    </Typography>
                                    <LinearProgress
                                        variant="determinate"
                                        value={dashboardData.profile_completeness * 100}
                                        sx={{ height: 8, borderRadius: 4, mb: 1 }}
                                    />
                                    <Typography variant="caption" color="text.secondary">
                                        {Math.round(dashboardData.profile_completeness * 100)}% {t('dashboard.complete')}
                                    </Typography>
                                </Box>
                            )}

                            {assessmentProgress && assessmentProgress.insights.length > 0 && (
                                <Box mb={2}>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        {t('dashboard.insights')}
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

                {/* Recommendations */}
                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <TrendingUp color="primary" sx={{ mr: 2 }} />
                                <Typography variant="h6">
                                    {t('dashboard.recommendations')}
                                </Typography>
                            </Box>

                            {dashboardData && dashboardData.recommendations.length > 0 ? (
                                <List dense>
                                    {dashboardData.recommendations.slice(0, 4).map((rec, index) => (
                                        <React.Fragment key={index}>
                                            <ListItem
                                                button
                                                onClick={() => handleRecommendationClick(rec.action_url)}
                                                sx={{ px: 0 }}
                                            >
                                                <ListItemIcon>
                                                    <Chip
                                                        label={rec.priority}
                                                        size="small"
                                                        color={getPriorityColor(rec.priority)}
                                                    />
                                                </ListItemIcon>
                                                <ListItemText
                                                    primary={rec.message}
                                                    primaryTypographyProps={{ variant: 'body2' }}
                                                />
                                                <ArrowForward fontSize="small" color="action" />
                                            </ListItem>
                                            {index < dashboardData.recommendations.length - 1 && <Divider />}
                                        </React.Fragment>
                                    ))}
                                </List>
                            ) : (
                                <Box textAlign="center" py={3}>
                                    <CheckCircle color="success" sx={{ fontSize: 48, mb: 1 }} />
                                    <Typography variant="body2" color="text.secondary">
                                        {t('dashboard.empty.allSet')}
                                    </Typography>
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                {/* Compatibility Trends */}
                {dashboardData && dashboardData.compatibility_trends.length > 0 && (
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Box display="flex" alignItems="center" mb={2}>
                                    <Timeline color="primary" sx={{ mr: 2 }} />
                                    <Typography variant="h6">
                                        {t('dashboard.compatibilityTrends')}
                                    </Typography>
                                </Box>

                                <ResponsiveContainer width="100%" height={200}>
                                    <LineChart data={dashboardData.compatibility_trends}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis
                                            dataKey="week"
                                            tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                        />
                                        <YAxis domain={[0, 1]} />
                                        <RechartsTooltip
                                            formatter={(value: number) => `${(value * 100).toFixed(0)}%`}
                                            labelFormatter={(label) => new Date(label).toLocaleDateString()}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="avg_score"
                                            stroke="#8884d8"
                                            strokeWidth={2}
                                            dot={{ r: 4 }}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>

                                <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                                    {t('dashboard.trendsDescription')}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                )}

                {/* Activity Feed */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <Notifications color="primary" sx={{ mr: 2 }} />
                                <Typography variant="h6">
                                    {t('dashboard.recentActivity')}
                                </Typography>
                            </Box>

                            {dashboardData && dashboardData.activity_feed.length > 0 ? (
                                <List dense>
                                    {dashboardData.activity_feed.slice(0, 8).map((activity, index) => (
                                        <React.Fragment key={index}>
                                            <ListItem sx={{ px: 0 }}>
                                                <ListItemIcon>
                                                    {getActivityIcon(activity.type)}
                                                </ListItemIcon>
                                                <ListItemText
                                                    primary={activity.message}
                                                    secondary={formatTimestamp(activity.timestamp)}
                                                    primaryTypographyProps={{ variant: 'body2' }}
                                                    secondaryTypographyProps={{ variant: 'caption' }}
                                                />
                                            </ListItem>
                                            {index < Math.min(dashboardData.activity_feed.length, 8) - 1 && <Divider />}
                                        </React.Fragment>
                                    ))}
                                </List>
                            ) : (
                                <Box textAlign="center" py={3}>
                                    <Info color="action" sx={{ fontSize: 48, mb: 1 }} />
                                    <Typography variant="body2" color="text.secondary">
                                        {t('dashboard.empty.noActivity')}
                                    </Typography>
                                    <Button
                                        variant="outlined"
                                        startIcon={<Explore />}
                                        onClick={() => navigate('/discover')}
                                        sx={{ mt: 2 }}
                                    >
                                        {t('dashboard.actions.discoverMatches')}
                                    </Button>
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                {/* Quick Actions */}
                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                {t('dashboard.quickActions')}
                            </Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper
                                        elevation={0}
                                        sx={{
                                            p: 2,
                                            textAlign: 'center',
                                            cursor: 'pointer',
                                            '&:hover': { bgcolor: 'action.hover' },
                                            border: 1,
                                            borderColor: 'divider'
                                        }}
                                        onClick={() => navigate('/discover')}
                                    >
                                        <Explore sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                        <Typography variant="subtitle2">{t('dashboard.actions.discoverMatches')}</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {t('dashboard.descriptions.discoverMatches')}
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper
                                        elevation={0}
                                        sx={{
                                            p: 2,
                                            textAlign: 'center',
                                            cursor: 'pointer',
                                            '&:hover': { bgcolor: 'action.hover' },
                                            border: 1,
                                            borderColor: 'divider'
                                        }}
                                        onClick={() => navigate('/matches')}
                                    >
                                        <Groups sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                        <Typography variant="subtitle2">{t('dashboard.actions.myMatches')}</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {t('dashboard.descriptions.myMatches')}
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper
                                        elevation={0}
                                        sx={{
                                            p: 2,
                                            textAlign: 'center',
                                            cursor: 'pointer',
                                            '&:hover': { bgcolor: 'action.hover' },
                                            border: 1,
                                            borderColor: 'divider'
                                        }}
                                        onClick={() => navigate('/avatar')}
                                    >
                                        <Psychology sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                        <Typography variant="subtitle2">{t('dashboard.actions.aiAvatar')}</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {t('dashboard.descriptions.aiAvatar')}
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper
                                        elevation={0}
                                        sx={{
                                            p: 2,
                                            textAlign: 'center',
                                            cursor: 'pointer',
                                            '&:hover': { bgcolor: 'action.hover' },
                                            border: 1,
                                            borderColor: 'divider'
                                        }}
                                        onClick={() => navigate('/profile')}
                                    >
                                        <Edit sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                        <Typography variant="subtitle2">{t('dashboard.actions.editProfile')}</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {t('dashboard.descriptions.editProfile')}
                                        </Typography>
                                    </Paper>
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
