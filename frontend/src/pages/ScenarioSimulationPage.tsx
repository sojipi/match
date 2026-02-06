import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
    Box,
    Container,
    Typography,
    Paper,
    Alert,
    Button,
    Breadcrumbs,
    Link
} from '@mui/material';
import {
    ArrowBack,
    Home,
    People,
    Psychology
} from '@mui/icons-material';

import ScenarioManager from '../components/scenarios/ScenarioManager';
import { useAppSelector } from '../hooks/redux';

const ScenarioSimulationPage: React.FC = () => {
    const { matchId } = useParams<{ matchId: string }>();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const currentUser = useAppSelector(state => state.auth.user);

    const [matchUserId, setMatchUserId] = useState<string>('');
    const [matchUserName, setMatchUserName] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Get match user ID from URL params or search params
    useEffect(() => {
        const userIdFromParams = searchParams.get('userId');
        const userNameFromParams = searchParams.get('userName');

        if (userIdFromParams) {
            setMatchUserId(userIdFromParams);
            setMatchUserName(userNameFromParams || 'Your Match');
            setLoading(false);
        } else if (matchId) {
            loadMatchDetails();
        } else {
            setError('No match information provided');
            setLoading(false);
        }
    }, [matchId, searchParams]);

    const loadMatchDetails = async () => {
        if (!matchId) return;

        try {
            setLoading(true);
            const response = await fetch(`/api/v1/matches/${matchId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load match details');
            }

            const matchData = await response.json();

            // Determine which user is the match (not the current user)
            const otherUser = matchData.user1.id === currentUser?.id
                ? matchData.user2
                : matchData.user1;

            setMatchUserId(otherUser.id);
            setMatchUserName(`${otherUser.first_name} ${otherUser.last_name}`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load match details');
        } finally {
            setLoading(false);
        }
    };

    const handleSimulationComplete = (results: any) => {
        // Navigate to compatibility report page with results
        navigate(`/compatibility/${matchId || 'direct'}`, {
            state: {
                simulationResults: results,
                matchUserId,
                matchUserName
            }
        });
    };

    const handleClose = () => {
        // Navigate back to matches or dashboard
        if (matchId) {
            navigate(`/matches/${matchId}`);
        } else {
            navigate('/matches');
        }
    };

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ py: 4 }}>
                <Typography>Loading match details...</Typography>
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxWidth="lg" sx={{ py: 4 }}>
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
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
                        <Psychology sx={{ mr: 0.5 }} fontSize="inherit" />
                        Scenario Simulation
                    </Typography>
                </Breadcrumbs>

                {/* Page Header */}
                <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                            <Typography variant="h4" gutterBottom>
                                Scenario Simulation
                            </Typography>
                            <Typography variant="body1" color="text.secondary">
                                Explore compatibility with {matchUserName} through AI-powered relationship scenarios
                            </Typography>
                        </Box>
                        <Button
                            variant="outlined"
                            startIcon={<ArrowBack />}
                            onClick={handleClose}
                        >
                            Back to Matches
                        </Button>
                    </Box>
                </Paper>

                {/* Scenario Manager */}
                <Box sx={{ height: 'calc(100vh - 200px)' }}>
                    <ScenarioManager
                        matchUserId={matchUserId}
                        matchId={matchId}
                        onComplete={handleSimulationComplete}
                        onClose={handleClose}
                    />
                </Box>
            </Container>
        </Box>
    );
};

export default ScenarioSimulationPage;