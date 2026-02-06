import React, { useState, useEffect } from 'react';
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    LinearProgress,
    Chip,
    Alert,
    CircularProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Button
} from '@mui/material';
import {
    TrendingUp,
    TrendingDown,
    TrendingFlat,
    Psychology,
    Chat,
    Handshake,
    Favorite,
    EmojiObjects,
    Assessment,
    Timeline,
    Insights,
    Lightbulb
} from '@mui/icons-material';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    BarChart,
    Bar,
    Legend
} from 'recharts';

interface CompatibilityDashboardProps {
    matchUserId: string;
    matchId?: string;
    onViewFullReport?: () => void;
}

interface DashboardData {
    has_data: boolean;
    message?: string;
    overview?: {
        overall_score: number;
        trend: string;
        sessions_completed: number;
        last_session_date: string;
    };
    dimension_scores?: {
        [key: string]: number;
    };
    progress_over_time?: Array<{
        date: string;
        overall_score: number;
        collaboration_score: number;
        communication_score: number;
        scenario: string;
    }>;
    scenario_performance?: {
        [category: string]: {
            sessions: number;
            average_score: number;
            scores: number[];
        };
    };
    communication_patterns?: {
        participation_balance: {
            balance_score: number;
            description: string;
        };
        response_patterns: {
            average_response_length: number;
            total_exchanges: number;
        };
    };
    key_insights?: string[];
    next_steps?: Array<{
        type: string;
        title: string;
        description: string;
    }>;
}

const CompatibilityDashboard: React.FC<CompatibilityDashboardProps> = ({
    matchUserId,
    matchId,
    onViewFullReport
}) => {
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadDashboardData();
    }, [matchUserId, matchId]);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            params.append('user2_id', matchUserId);
            if (matchId) params.append('match_id', matchId);

            const response = await fetch(`/api/v1/compatibility/dashboard?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load compatibility dashboard');
            }

            const data = await response.json();
            setDashboardData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load dashboard');
        } finally {
            setLoading(false);
        }
    };

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'improving': return <TrendingUp color="success" />;
            case 'declining': return <TrendingDown color="error" />;
            default: return <TrendingFlat color="info" />;
        }
    };

    const getTrendColor = (trend: string) => {
        switch (trend) {
            case 'improving': return 'success.main';
            case 'declining': return 'error.main';
            default: return 'info.main';
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 0.8) return 'success.main';
        if (score >= 0.6) return 'warning.main';
        return 'error.main';
    };

    const formatDimensionScores = (scores: { [key: string]: number }) => {
        return Object.entries(scores).map(([dimension, score]) => ({
            dimension: dimension.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            score: Math.round(score * 100),
            fullMark: 100
        }));
    };

    const formatProgressData = (progressData: DashboardData['progress_over_time']) => {
        if (!progressData) return [];

        return progressData.map(item => ({
            date: new Date(item.date).toLocaleDateString(),
            overall: Math.round(item.overall_score * 100),
            collaboration: Math.round(item.collaboration_score * 100),
            communication: Math.round(item.communication_score * 100),
            scenario: item.scenario
        }));
    };

    const formatScenarioData = (scenarioData: DashboardData['scenario_performance']) => {
        if (!scenarioData) return [];

        return Object.entries(scenarioData).map(([category, data]) => ({
            category: category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            score: Math.round(data.average_score * 100),
            sessions: data.sessions
        }));
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

    if (!dashboardData?.has_data) {
        return (
            <Alert severity="info" sx={{ mb: 2 }}>
                {dashboardData?.message || 'No compatibility data available yet. Complete some scenario simulations to see your compatibility analysis.'}
            </Alert>
        );
    }

    const { overview, dimension_scores, progress_over_time, scenario_performance, communication_patterns, key_insights, next_steps } = dashboardData;

    return (
        <Box>
            {/* Overview Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h3" color="primary.main" gutterBottom>
                                {Math.round((overview?.overall_score || 0) * 100)}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Overall Compatibility
                            </Typography>
                            <Box display="flex" justifyContent="center" alignItems="center" mt={1}>
                                {overview?.trend && getTrendIcon(overview.trend)}
                                <Typography variant="caption" sx={{ ml: 0.5, color: getTrendColor(overview?.trend || 'stable') }}>
                                    {overview?.trend || 'stable'}
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="secondary.main" gutterBottom>
                                {overview?.sessions_completed || 0}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Sessions Completed
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Communication Balance
                            </Typography>
                            {communication_patterns?.participation_balance && (
                                <Box>
                                    <LinearProgress
                                        variant="determinate"
                                        value={communication_patterns.participation_balance.balance_score * 100}
                                        sx={{ mb: 1 }}
                                    />
                                    <Typography variant="body2" color="text.secondary">
                                        {communication_patterns.participation_balance.description}
                                    </Typography>
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Compatibility Dimensions Radar Chart */}
            {dimension_scores && (
                <Grid container spacing={3} sx={{ mb: 4 }}>
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Compatibility Dimensions
                                </Typography>
                                <ResponsiveContainer width="100%" height={300}>
                                    <RadarChart data={formatDimensionScores(dimension_scores)}>
                                        <PolarGrid />
                                        <PolarAngleAxis dataKey="dimension" />
                                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                                        <Radar
                                            name="Score"
                                            dataKey="score"
                                            stroke="#8884d8"
                                            fill="#8884d8"
                                            fillOpacity={0.3}
                                        />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Dimension Breakdown
                                </Typography>
                                <List dense>
                                    {Object.entries(dimension_scores).map(([dimension, score]) => (
                                        <ListItem key={dimension}>
                                            <ListItemIcon>
                                                {dimension === 'collaboration' && <Handshake />}
                                                {dimension === 'communication' && <Chat />}
                                                {dimension === 'empathy' && <Favorite />}
                                                {dimension === 'problem_solving' && <EmojiObjects />}
                                                {!['collaboration', 'communication', 'empathy', 'problem_solving'].includes(dimension) && <Psychology />}
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={dimension.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                                secondary={
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <LinearProgress
                                                            variant="determinate"
                                                            value={score * 100}
                                                            sx={{ flexGrow: 1, height: 6 }}
                                                        />
                                                        <Typography variant="caption" sx={{ color: getScoreColor(score) }}>
                                                            {Math.round(score * 100)}%
                                                        </Typography>
                                                    </Box>
                                                }
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {/* Progress Over Time */}
            {progress_over_time && progress_over_time.length > 1 && (
                <Card sx={{ mb: 4 }}>
                    <CardContent>
                        <Typography variant="h6" gutterBottom>
                            Progress Over Time
                        </Typography>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={formatProgressData(progress_over_time)}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="overall"
                                    stroke="#8884d8"
                                    name="Overall"
                                    strokeWidth={2}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="collaboration"
                                    stroke="#82ca9d"
                                    name="Collaboration"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="communication"
                                    stroke="#ffc658"
                                    name="Communication"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            )}

            {/* Scenario Performance */}
            {scenario_performance && (
                <Card sx={{ mb: 4 }}>
                    <CardContent>
                        <Typography variant="h6" gutterBottom>
                            Performance by Scenario Type
                        </Typography>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={formatScenarioData(scenario_performance)}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="category" />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Bar dataKey="score" fill="#8884d8" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            )}

            {/* Key Insights and Next Steps */}
            <Grid container spacing={3}>
                {key_insights && key_insights.length > 0 && (
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    <Insights sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    Key Insights
                                </Typography>
                                <List>
                                    {key_insights.map((insight, index) => (
                                        <ListItem key={index}>
                                            <ListItemIcon>
                                                <Lightbulb color="primary" />
                                            </ListItemIcon>
                                            <ListItemText primary={insight} />
                                        </ListItem>
                                    ))}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>
                )}

                {next_steps && next_steps.length > 0 && (
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    Recommended Next Steps
                                </Typography>
                                <List>
                                    {next_steps.map((step, index) => (
                                        <ListItem key={index}>
                                            <ListItemIcon>
                                                <Chip
                                                    label={step.type}
                                                    size="small"
                                                    color={step.type === 'improvement' ? 'warning' : 'primary'}
                                                />
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={step.title}
                                                secondary={step.description}
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>
                )}
            </Grid>

            {/* Action Buttons */}
            {onViewFullReport && (
                <Box display="flex" justifyContent="center" mt={4}>
                    <Button
                        variant="contained"
                        size="large"
                        startIcon={<Assessment />}
                        onClick={onViewFullReport}
                    >
                        View Full Compatibility Report
                    </Button>
                </Box>
            )}
        </Box>
    );
};

export default CompatibilityDashboard;