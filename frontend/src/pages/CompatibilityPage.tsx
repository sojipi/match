import React, { useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import {
    Box,
    Container,
    Typography,
    Paper,
    Tabs,
    Tab,
    Button,
    Breadcrumbs,
    Link
} from '@mui/material';
import {
    ArrowBack,
    Home,
    People,
    Assessment,
    Dashboard as DashboardIcon
} from '@mui/icons-material';

import CompatibilityDashboard from '../components/compatibility/CompatibilityDashboard';
import CompatibilityReport from '../components/compatibility/CompatibilityReport';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`compatibility-tabpanel-${index}`}
            aria-labelledby={`compatibility-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ py: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
}

function a11yProps(index: number) {
    return {
        id: `compatibility-tab-${index}`,
        'aria-controls': `compatibility-tabpanel-${index}`,
    };
}

const CompatibilityPage: React.FC = () => {
    const { matchId } = useParams<{ matchId: string }>();
    const location = useLocation();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState(0);

    // Get data from navigation state (from scenario simulation)
    const simulationResults = location.state?.simulationResults;
    const matchUserId = location.state?.matchUserId;
    const matchUserName = location.state?.matchUserName;

    // If no match user ID in state, try to extract from URL params
    const urlParams = new URLSearchParams(location.search);
    const finalMatchUserId = matchUserId || urlParams.get('userId') || '';
    const finalMatchUserName = matchUserName || urlParams.get('userName') || 'Your Match';

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue);
    };

    const handleBack = () => {
        if (matchId) {
            navigate(`/matches/${matchId}`);
        } else {
            navigate('/matches');
        }
    };

    const handleViewFullReport = () => {
        setActiveTab(1); // Switch to report tab
    };

    if (!finalMatchUserId) {
        return (
            <Container maxWidth="lg" sx={{ py: 4 }}>
                <Typography variant="h5" color="error" gutterBottom>
                    Missing Match Information
                </Typography>
                <Typography variant="body1" paragraph>
                    Unable to load compatibility analysis. Match user information is required.
                </Typography>
                <Button
                    startIcon={<ArrowBack />}
                    onClick={() => navigate('/matches')}
                >
                    Back to Matches
                </Button>
            </Container>
        );
    }

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: 'grey.50' }}>
            <Container maxWidth="xl" sx={{ py: 2 }}>
                {/* Breadcrumbs */}
                <Breadcrumbs sx={{ mb: 2 }}>
                    <Link
                        color="inherit"
                        href="/dashboard"
                        sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}
                    >
                        <Home sx={{ mr: 0.5 }} fontSize="inherit" />
                        Dashboard
                    </Link>
                    <Link
                        color="inherit"
                        href="/matches"
                        sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}
                    >
                        <People sx={{ mr: 0.5 }} fontSize="inherit" />
                        Matches
                    </Link>
                    <Typography
                        color="text.primary"
                        sx={{ display: 'flex', alignItems: 'center' }}
                    >
                        <Assessment sx={{ mr: 0.5 }} fontSize="inherit" />
                        Compatibility Analysis
                    </Typography>
                </Breadcrumbs>

                {/* Page Header */}
                <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                            <Typography variant="h4" gutterBottom>
                                Compatibility Analysis
                            </Typography>
                            <Typography variant="body1" color="text.secondary">
                                Detailed compatibility insights with {finalMatchUserName}
                            </Typography>
                            {simulationResults && (
                                <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
                                    ✓ Based on recent scenario simulation results
                                </Typography>
                            )}
                        </Box>
                        <Button
                            variant="outlined"
                            startIcon={<ArrowBack />}
                            onClick={handleBack}
                        >
                            Back to Matches
                        </Button>
                    </Box>
                </Paper>

                {/* Tabs */}
                <Paper elevation={1} sx={{ mb: 3 }}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                        <Tabs
                            value={activeTab}
                            onChange={handleTabChange}
                            aria-label="compatibility analysis tabs"
                        >
                            <Tab
                                label="Dashboard"
                                icon={<DashboardIcon />}
                                iconPosition="start"
                                {...a11yProps(0)}
                            />
                            <Tab
                                label="Full Report"
                                icon={<Assessment />}
                                iconPosition="start"
                                {...a11yProps(1)}
                            />
                        </Tabs>
                    </Box>

                    <TabPanel value={activeTab} index={0}>
                        <CompatibilityDashboard
                            matchUserId={finalMatchUserId}
                            matchId={matchId}
                            onViewFullReport={handleViewFullReport}
                        />
                    </TabPanel>

                    <TabPanel value={activeTab} index={1}>
                        <CompatibilityReport
                            matchUserId={finalMatchUserId}
                            matchId={matchId}
                        />
                    </TabPanel>
                </Paper>

                {/* Simulation Results Summary (if available) */}
                {simulationResults && (
                    <Paper elevation={1} sx={{ p: 3, mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Latest Simulation Results
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            These results have been incorporated into your compatibility analysis above.
                        </Typography>

                        <Box display="flex" gap={4}>
                            <Box textAlign="center">
                                <Typography variant="h4" color="primary.main">
                                    {Math.round((simulationResults.results?.overall_success_score || 0) * 100)}%
                                </Typography>
                                <Typography variant="caption">
                                    Session Success
                                </Typography>
                            </Box>
                            <Box textAlign="center">
                                <Typography variant="h4" color="secondary.main">
                                    {Math.round((simulationResults.results?.collaboration_score || 0) * 100)}%
                                </Typography>
                                <Typography variant="caption">
                                    Collaboration
                                </Typography>
                            </Box>
                            <Box textAlign="center">
                                <Typography variant="h4" color="success.main">
                                    {Math.round((simulationResults.results?.communication_score || 0) * 100)}%
                                </Typography>
                                <Typography variant="caption">
                                    Communication
                                </Typography>
                            </Box>
                            <Box textAlign="center">
                                <Typography variant="h4" color="info.main">
                                    {simulationResults.duration_seconds ? `${Math.floor(simulationResults.duration_seconds / 60)}:${(simulationResults.duration_seconds % 60).toString().padStart(2, '0')}` : 'N/A'}
                                </Typography>
                                <Typography variant="caption">
                                    Duration
                                </Typography>
                            </Box>
                        </Box>
                    </Paper>
                )}
            </Container>
        </Box>
    );
};

export default CompatibilityPage;