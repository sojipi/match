import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Grid,
    Card,
    CardContent,
    Chip,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Alert,
    CircularProgress,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import {
    ExpandMore,
    Psychology,
    TrendingUp,
    Lightbulb,
    Favorite,
    Warning,
    CheckCircle,
    Assessment,
    Download,
    Share,
    Print
} from '@mui/icons-material';

interface CompatibilityReportProps {
    matchUserId: string;
    matchId?: string;
    onClose?: () => void;
}

interface CompatibilityReport {
    report_id: string;
    generated_at: string;
    users: {
        user1: {
            id: string;
            name: string;
            personality_summary: any;
        };
        user2: {
            id: string;
            name: string;
            personality_summary: any;
        };
    };
    compatibility_scores: {
        [key: string]: number;
    };
    insights: {
        strengths: Array<{
            area: string;
            score: number;
            description: string;
        }>;
        challenges: Array<{
            area: string;
            score: number;
            description: string;
        }>;
        opportunities: Array<{
            area: string;
            current_score: number;
            potential: string;
            description: string;
        }>;
        personality_dynamics: {
            complementary_traits: Array<{
                trait: string;
                description: string;
            }>;
            similar_traits: Array<{
                trait: string;
                description: string;
            }>;
            potential_friction: Array<{
                trait: string;
                description: string;
            }>;
        };
    };
    trends?: {
        has_trends: boolean;
        overall_trend: string;
        trend_summary: string;
        timeline_data: Array<{
            date: string;
            overall_score: number;
            scenario_category: string;
        }>;
    };
    recommendations: {
        immediate_actions: string[];
        long_term_goals: string[];
        scenario_suggestions: Array<{
            category: string;
            title: string;
            reason: string;
        }>;
        relationship_advice: string[];
    };
    simulation_summary: {
        total_sessions: number;
        total_duration_minutes: number;
        scenarios_explored: string[];
        average_engagement: number;
    };
}

const CompatibilityReport: React.FC<CompatibilityReportProps> = ({
    matchUserId,
    matchId,
    onClose
}) => {
    const [report, setReport] = useState<CompatibilityReport | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [shareDialogOpen, setShareDialogOpen] = useState(false);

    useEffect(() => {
        loadReport();
    }, [matchUserId, matchId]);

    const loadReport = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            params.append('user2_id', matchUserId);
            if (matchId) params.append('match_id', matchId);
            params.append('include_trends', 'true');

            const response = await fetch(`/api/v1/compatibility/report?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load compatibility report');
            }

            const data = await response.json();
            setReport(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load report');
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 0.8) return 'success';
        if (score >= 0.6) return 'warning';
        return 'error';
    };

    const getScoreLabel = (score: number) => {
        if (score >= 0.8) return 'Excellent';
        if (score >= 0.6) return 'Good';
        if (score >= 0.4) return 'Fair';
        return 'Needs Work';
    };

    const handlePrint = () => {
        window.print();
    };

    const handleDownload = () => {
        if (!report) return;

        const reportData = JSON.stringify(report, null, 2);
        const blob = new Blob([reportData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `compatibility-report-${report.report_id}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleShare = () => {
        setShareDialogOpen(true);
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

    if (!report) {
        return (
            <Alert severity="warning" sx={{ mb: 2 }}>
                No compatibility report available
            </Alert>
        );
    }

    return (
        <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 3 }}>
            {/* Header */}
            <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h4" gutterBottom>
                        Compatibility Report
                    </Typography>
                    <Box display="flex" gap={1}>
                        <Button startIcon={<Print />} onClick={handlePrint}>
                            Print
                        </Button>
                        <Button startIcon={<Download />} onClick={handleDownload}>
                            Download
                        </Button>
                        <Button startIcon={<Share />} onClick={handleShare}>
                            Share
                        </Button>
                        {onClose && (
                            <Button variant="outlined" onClick={onClose}>
                                Close
                            </Button>
                        )}
                    </Box>
                </Box>

                <Typography variant="body1" color="text.secondary" paragraph>
                    Comprehensive compatibility analysis between {report.users.user1.name} and {report.users.user2.name}
                </Typography>

                <Typography variant="caption" color="text.secondary">
                    Generated on {new Date(report.generated_at).toLocaleString()}
                </Typography>
            </Paper>

            {/* Overall Compatibility Score */}
            <Card sx={{ mb: 3 }}>
                <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h2" color="primary.main" gutterBottom>
                        {Math.round(report.compatibility_scores.overall_compatibility * 100)}%
                    </Typography>
                    <Typography variant="h5" gutterBottom>
                        Overall Compatibility
                    </Typography>
                    <Chip
                        label={getScoreLabel(report.compatibility_scores.overall_compatibility)}
                        color={getScoreColor(report.compatibility_scores.overall_compatibility) as any}
                        size="medium"
                    />

                    {report.trends?.has_trends && (
                        <Box mt={2}>
                            <Typography variant="body2" color="text.secondary">
                                {report.trends.trend_summary}
                            </Typography>
                        </Box>
                    )}
                </CardContent>
            </Card>

            {/* Compatibility Dimensions */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Compatibility Dimensions
                    </Typography>
                    <Grid container spacing={2}>
                        {Object.entries(report.compatibility_scores)
                            .filter(([key]) => key !== 'overall_compatibility')
                            .map(([dimension, score]) => (
                                <Grid item xs={12} sm={6} md={4} key={dimension}>
                                    <Box textAlign="center" p={2}>
                                        <Typography variant="h4" color={getScoreColor(score) + '.main'}>
                                            {Math.round(score * 100)}%
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            {dimension.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                        </Typography>
                                        <Chip
                                            label={getScoreLabel(score)}
                                            color={getScoreColor(score) as any}
                                            size="small"
                                            sx={{ mt: 1 }}
                                        />
                                    </Box>
                                </Grid>
                            ))}
                    </Grid>
                </CardContent>
            </Card>

            {/* Insights Sections */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                {/* Strengths */}
                {report.insights.strengths.length > 0 && (
                    <Grid item xs={12} md={4}>
                        <Card sx={{ height: '100%' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom color="success.main">
                                    <CheckCircle sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    Strengths
                                </Typography>
                                <List dense>
                                    {report.insights.strengths.map((strength, index) => (
                                        <ListItem key={index}>
                                            <ListItemText
                                                primary={strength.area}
                                                secondary={strength.description}
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>
                )}

                {/* Challenges */}
                {report.insights.challenges.length > 0 && (
                    <Grid item xs={12} md={4}>
                        <Card sx={{ height: '100%' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom color="warning.main">
                                    <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    Challenges
                                </Typography>
                                <List dense>
                                    {report.insights.challenges.map((challenge, index) => (
                                        <ListItem key={index}>
                                            <ListItemText
                                                primary={challenge.area}
                                                secondary={challenge.description}
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>
                )}

                {/* Opportunities */}
                {report.insights.opportunities.length > 0 && (
                    <Grid item xs={12} md={4}>
                        <Card sx={{ height: '100%' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom color="info.main">
                                    <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    Growth Opportunities
                                </Typography>
                                <List dense>
                                    {report.insights.opportunities.map((opportunity, index) => (
                                        <ListItem key={index}>
                                            <ListItemText
                                                primary={opportunity.area}
                                                secondary={
                                                    <Box>
                                                        <Typography variant="body2" component="span">
                                                            {opportunity.description}
                                                        </Typography>
                                                        <Chip
                                                            label={`${opportunity.potential} Potential`}
                                                            size="small"
                                                            color="info"
                                                            sx={{ ml: 1 }}
                                                        />
                                                    </Box>
                                                }
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>
                )}
            </Grid>

            {/* Detailed Analysis Accordions */}
            <Box sx={{ mb: 3 }}>
                {/* Personality Dynamics */}
                <Accordion>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="h6">
                            <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Personality Dynamics
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Grid container spacing={3}>
                            {report.insights.personality_dynamics.complementary_traits.length > 0 && (
                                <Grid item xs={12} md={4}>
                                    <Typography variant="subtitle1" gutterBottom color="success.main">
                                        Complementary Traits
                                    </Typography>
                                    <List dense>
                                        {report.insights.personality_dynamics.complementary_traits.map((trait, index) => (
                                            <ListItem key={index}>
                                                <ListItemText
                                                    primary={trait.trait}
                                                    secondary={trait.description}
                                                />
                                            </ListItem>
                                        ))}
                                    </List>
                                </Grid>
                            )}

                            {report.insights.personality_dynamics.similar_traits.length > 0 && (
                                <Grid item xs={12} md={4}>
                                    <Typography variant="subtitle1" gutterBottom color="info.main">
                                        Similar Traits
                                    </Typography>
                                    <List dense>
                                        {report.insights.personality_dynamics.similar_traits.map((trait, index) => (
                                            <ListItem key={index}>
                                                <ListItemText
                                                    primary={trait.trait}
                                                    secondary={trait.description}
                                                />
                                            </ListItem>
                                        ))}
                                    </List>
                                </Grid>
                            )}

                            {report.insights.personality_dynamics.potential_friction.length > 0 && (
                                <Grid item xs={12} md={4}>
                                    <Typography variant="subtitle1" gutterBottom color="warning.main">
                                        Potential Friction Areas
                                    </Typography>
                                    <List dense>
                                        {report.insights.personality_dynamics.potential_friction.map((trait, index) => (
                                            <ListItem key={index}>
                                                <ListItemText
                                                    primary={trait.trait}
                                                    secondary={trait.description}
                                                />
                                            </ListItem>
                                        ))}
                                    </List>
                                </Grid>
                            )}
                        </Grid>
                    </AccordionDetails>
                </Accordion>

                {/* Recommendations */}
                <Accordion>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="h6">
                            <Lightbulb sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Recommendations
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Grid container spacing={3}>
                            {report.recommendations.immediate_actions.length > 0 && (
                                <Grid item xs={12} md={6}>
                                    <Typography variant="subtitle1" gutterBottom color="primary.main">
                                        Immediate Actions
                                    </Typography>
                                    <List dense>
                                        {report.recommendations.immediate_actions.map((action, index) => (
                                            <ListItem key={index}>
                                                <ListItemIcon>
                                                    <CheckCircle color="primary" />
                                                </ListItemIcon>
                                                <ListItemText primary={action} />
                                            </ListItem>
                                        ))}
                                    </List>
                                </Grid>
                            )}

                            {report.recommendations.long_term_goals.length > 0 && (
                                <Grid item xs={12} md={6}>
                                    <Typography variant="subtitle1" gutterBottom color="secondary.main">
                                        Long-term Goals
                                    </Typography>
                                    <List dense>
                                        {report.recommendations.long_term_goals.map((goal, index) => (
                                            <ListItem key={index}>
                                                <ListItemIcon>
                                                    <TrendingUp color="secondary" />
                                                </ListItemIcon>
                                                <ListItemText primary={goal} />
                                            </ListItem>
                                        ))}
                                    </List>
                                </Grid>
                            )}

                            {report.recommendations.scenario_suggestions.length > 0 && (
                                <Grid item xs={12}>
                                    <Typography variant="subtitle1" gutterBottom color="info.main">
                                        Suggested Scenarios
                                    </Typography>
                                    <Grid container spacing={2}>
                                        {report.recommendations.scenario_suggestions.map((scenario, index) => (
                                            <Grid item xs={12} md={4} key={index}>
                                                <Card variant="outlined">
                                                    <CardContent>
                                                        <Typography variant="subtitle2" gutterBottom>
                                                            {scenario.title}
                                                        </Typography>
                                                        <Chip
                                                            label={scenario.category.replace('_', ' ')}
                                                            size="small"
                                                            color="info"
                                                            sx={{ mb: 1 }}
                                                        />
                                                        <Typography variant="body2" color="text.secondary">
                                                            {scenario.reason}
                                                        </Typography>
                                                    </CardContent>
                                                </Card>
                                            </Grid>
                                        ))}
                                    </Grid>
                                </Grid>
                            )}

                            {report.recommendations.relationship_advice.length > 0 && (
                                <Grid item xs={12}>
                                    <Typography variant="subtitle1" gutterBottom color="success.main">
                                        Relationship Advice
                                    </Typography>
                                    <List dense>
                                        {report.recommendations.relationship_advice.map((advice, index) => (
                                            <ListItem key={index}>
                                                <ListItemIcon>
                                                    <Favorite color="success" />
                                                </ListItemIcon>
                                                <ListItemText primary={advice} />
                                            </ListItem>
                                        ))}
                                    </List>
                                </Grid>
                            )}
                        </Grid>
                    </AccordionDetails>
                </Accordion>

                {/* Simulation Summary */}
                <Accordion>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="h6">
                            <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Simulation Summary
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={3}>
                                <Box textAlign="center">
                                    <Typography variant="h4" color="primary.main">
                                        {report.simulation_summary.total_sessions}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Total Sessions
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={12} md={3}>
                                <Box textAlign="center">
                                    <Typography variant="h4" color="secondary.main">
                                        {Math.round(report.simulation_summary.total_duration_minutes)}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Minutes Together
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={12} md={3}>
                                <Box textAlign="center">
                                    <Typography variant="h4" color="success.main">
                                        {report.simulation_summary.scenarios_explored.length}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Scenario Types
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={12} md={3}>
                                <Box textAlign="center">
                                    <Typography variant="h4" color="info.main">
                                        {Math.round(report.simulation_summary.average_engagement * 100)}%
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Avg Engagement
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={12}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Scenarios Explored:
                                </Typography>
                                <Box display="flex" flexWrap="wrap" gap={1}>
                                    {report.simulation_summary.scenarios_explored.map((scenario, index) => (
                                        <Chip
                                            key={index}
                                            label={scenario.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                            variant="outlined"
                                            size="small"
                                        />
                                    ))}
                                </Box>
                            </Grid>
                        </Grid>
                    </AccordionDetails>
                </Accordion>
            </Box>

            {/* Share Dialog */}
            <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)}>
                <DialogTitle>Share Compatibility Report</DialogTitle>
                <DialogContent>
                    <Alert severity="info" sx={{ mb: 2 }}>
                        Sharing functionality will be implemented in a future update.
                        For now, you can download the report or print it.
                    </Alert>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShareDialogOpen(false)}>Close</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default CompatibilityReport;