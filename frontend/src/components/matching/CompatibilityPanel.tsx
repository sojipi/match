/**
 * Compatibility Panel - Real-time compatibility metrics display
 */
import React from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    LinearProgress,
    Chip,
    Card,
    CardContent,
    Divider,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Tooltip
} from '@mui/material';
import {
    Close,
    TrendingUp,
    TrendingDown,
    TrendingFlat,
    Psychology,
    Chat,
    Favorite,
    Home,
    Lightbulb,
    CheckCircle,
    Warning
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { motion } from 'framer-motion';

import { CompatibilityMetrics, MatchSession } from '../../types/matching';

interface CompatibilityPanelProps {
    compatibility: CompatibilityMetrics;
    session?: MatchSession;
    onClose: () => void;
}

const CompatibilityPanel: React.FC<CompatibilityPanelProps> = ({
    compatibility,
    session,
    onClose
}) => {
    const getScoreColor = (score: number): string => {
        if (score >= 0.8) return '#4CAF50'; // Green
        if (score >= 0.6) return '#FF9800'; // Orange
        return '#F44336'; // Red
    };

    const getTrendIcon = (trendData: Array<{ timestamp: string; score: number }>) => {
        if (trendData.length < 2) return <TrendingFlat />;

        const recent = trendData.slice(-2);
        const trend = recent[1].score - recent[0].score;

        if (trend > 0.02) return <TrendingUp sx={{ color: 'success.main' }} />;
        if (trend < -0.02) return <TrendingDown sx={{ color: 'error.main' }} />;
        return <TrendingFlat sx={{ color: 'text.secondary' }} />;
    };

    const getDimensionIcon = (dimension: string) => {
        const icons: Record<string, React.ReactElement> = {
            personality: <Psychology />,
            communication: <Chat />,
            values: <Favorite />,
            lifestyle: <Home />
        };
        return icons[dimension] || <Psychology />;
    };

    const formatScore = (score: number): string => {
        return `${Math.round(score * 100)}%`;
    };

    // Prepare radar chart data
    const radarData = Object.entries(compatibility.dimension_scores).map(([key, value]) => ({
        dimension: key.charAt(0).toUpperCase() + key.slice(1),
        score: Math.round(value * 100),
        fullMark: 100
    }));

    return (
        <Box
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.paper'
            }}
        >
            {/* Header */}
            <Box
                sx={{
                    p: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    borderBottom: 1,
                    borderColor: 'divider'
                }}
            >
                <Typography variant="h6" component="h2">
                    Compatibility Metrics
                </Typography>
                <IconButton onClick={onClose} size="small">
                    <Close />
                </IconButton>
            </Box>

            {/* Content */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
                {/* Overall Score */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                <Typography variant="h6">Overall Compatibility</Typography>
                                {getTrendIcon(compatibility.trend_data)}
                            </Box>

                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                <Typography
                                    variant="h3"
                                    sx={{
                                        color: getScoreColor(compatibility.overall_score),
                                        fontWeight: 'bold'
                                    }}
                                >
                                    {formatScore(compatibility.overall_score)}
                                </Typography>
                                <Box sx={{ flex: 1 }}>
                                    <LinearProgress
                                        variant="determinate"
                                        value={compatibility.overall_score * 100}
                                        sx={{
                                            height: 12,
                                            borderRadius: 6,
                                            bgcolor: 'grey.200',
                                            '& .MuiLinearProgress-bar': {
                                                bgcolor: getScoreColor(compatibility.overall_score),
                                                borderRadius: 6
                                            }
                                        }}
                                    />
                                </Box>
                            </Box>

                            {compatibility.overall_score >= 0.8 && (
                                <Chip
                                    icon={<CheckCircle />}
                                    label="Excellent Match!"
                                    color="success"
                                    size="small"
                                />
                            )}
                            {compatibility.overall_score >= 0.6 && compatibility.overall_score < 0.8 && (
                                <Chip
                                    icon={<Lightbulb />}
                                    label="Good Potential"
                                    color="warning"
                                    size="small"
                                />
                            )}
                            {compatibility.overall_score < 0.6 && (
                                <Chip
                                    icon={<Warning />}
                                    label="Needs Work"
                                    color="error"
                                    size="small"
                                />
                            )}
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Dimension Scores */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                >
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            <Typography variant="h6" sx={{ mb: 2 }}>
                                Compatibility Dimensions
                            </Typography>

                            {Object.entries(compatibility.dimension_scores).map(([dimension, score], index) => (
                                <motion.div
                                    key={dimension}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.3, delay: index * 0.1 }}
                                >
                                    <Box sx={{ mb: 2 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                            {getDimensionIcon(dimension)}
                                            <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                                                {dimension}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
                                                {formatScore(score)}
                                            </Typography>
                                        </Box>
                                        <LinearProgress
                                            variant="determinate"
                                            value={score * 100}
                                            sx={{
                                                height: 8,
                                                borderRadius: 4,
                                                bgcolor: 'grey.200',
                                                '& .MuiLinearProgress-bar': {
                                                    bgcolor: getScoreColor(score),
                                                    borderRadius: 4
                                                }
                                            }}
                                        />
                                    </Box>
                                </motion.div>
                            ))}
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Radar Chart */}
                {radarData.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                    >
                        <Card sx={{ mb: 3 }}>
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2 }}>
                                    Compatibility Profile
                                </Typography>
                                <Box sx={{ height: 250 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <RadarChart data={radarData}>
                                            <PolarGrid />
                                            <PolarAngleAxis dataKey="dimension" />
                                            <PolarRadiusAxis
                                                angle={90}
                                                domain={[0, 100]}
                                                tick={false}
                                            />
                                            <Radar
                                                name="Compatibility"
                                                dataKey="score"
                                                stroke="#1976d2"
                                                fill="#1976d2"
                                                fillOpacity={0.3}
                                                strokeWidth={2}
                                            />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                </Box>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}

                {/* Trend Chart */}
                {compatibility.trend_data.length > 1 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                    >
                        <Card sx={{ mb: 3 }}>
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2 }}>
                                    Compatibility Trend
                                </Typography>
                                <Box sx={{ height: 200 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={compatibility.trend_data}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis
                                                dataKey="timestamp"
                                                tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                                            />
                                            <YAxis
                                                domain={[0, 1]}
                                                tickFormatter={(value) => `${Math.round(value * 100)}%`}
                                            />
                                            <RechartsTooltip
                                                labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                                                formatter={(value: number) => [`${Math.round(value * 100)}%`, 'Compatibility']}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="score"
                                                stroke="#1976d2"
                                                strokeWidth={3}
                                                dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
                                                activeDot={{ r: 6, stroke: '#1976d2', strokeWidth: 2 }}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </Box>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}

                {/* Key Insights */}
                {compatibility.insights.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.4 }}
                    >
                        <Card sx={{ mb: 3 }}>
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2 }}>
                                    Key Insights
                                </Typography>
                                <List dense>
                                    {compatibility.insights.map((insight, index) => (
                                        <ListItem key={index} sx={{ px: 0 }}>
                                            <ListItemIcon>
                                                <Lightbulb color="primary" />
                                            </ListItemIcon>
                                            <ListItemText primary={insight} />
                                        </ListItem>
                                    ))}
                                </List>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}

                {/* Strengths and Challenges */}
                <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                    {/* Strengths */}
                    {compatibility.strengths.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.5 }}
                            style={{ flex: 1 }}
                        >
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" color="success.main" sx={{ mb: 2 }}>
                                        Strengths
                                    </Typography>
                                    <List dense>
                                        {compatibility.strengths.map((strength, index) => (
                                            <ListItem key={index} sx={{ px: 0 }}>
                                                <ListItemIcon>
                                                    <CheckCircle color="success" />
                                                </ListItemIcon>
                                                <ListItemText
                                                    primary={strength}
                                                    primaryTypographyProps={{ variant: 'body2' }}
                                                />
                                            </ListItem>
                                        ))}
                                    </List>
                                </CardContent>
                            </Card>
                        </motion.div>
                    )}

                    {/* Challenges */}
                    {compatibility.challenges.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.6 }}
                            style={{ flex: 1 }}
                        >
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" color="warning.main" sx={{ mb: 2 }}>
                                        Areas to Explore
                                    </Typography>
                                    <List dense>
                                        {compatibility.challenges.map((challenge, index) => (
                                            <ListItem key={index} sx={{ px: 0 }}>
                                                <ListItemIcon>
                                                    <Warning color="warning" />
                                                </ListItemIcon>
                                                <ListItemText
                                                    primary={challenge}
                                                    primaryTypographyProps={{ variant: 'body2' }}
                                                />
                                            </ListItem>
                                        ))}
                                    </List>
                                </CardContent>
                            </Card>
                        </motion.div>
                    )}
                </Box>

                {/* Session Info */}
                {session && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.7 }}
                    >
                        <Card>
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2 }}>
                                    Session Details
                                </Typography>
                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Session Type:
                                        </Typography>
                                        <Chip
                                            label={session.session_type}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </Box>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Status:
                                        </Typography>
                                        <Chip
                                            label={session.status}
                                            size="small"
                                            color={session.status === 'active' ? 'success' : 'default'}
                                        />
                                    </Box>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Viewers:
                                        </Typography>
                                        <Typography variant="body2">
                                            {session.viewer_count}
                                        </Typography>
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}
            </Box>
        </Box>
    );
};

export default CompatibilityPanel;