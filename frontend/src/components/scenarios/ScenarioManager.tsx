import React, { useState } from 'react';
import {
    Box,
    Stepper,
    Step,
    StepLabel,
    Button,
    Typography,
    Paper,
    Alert,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress
} from '@mui/material';
import {
    LibraryBooks,
    PlayArrow,
    Assessment,
    CheckCircle
} from '@mui/icons-material';

import ScenarioLibrary from './ScenarioLibrary';
import SimulationTheater from './SimulationTheater';

interface Scenario {
    id: string;
    name: string;
    title: string;
    description: string;
    category: string;
    difficulty_level: number;
    estimated_duration_minutes: number;
    personality_dimensions: string[];
    value_dimensions: string[];
    tags: string[];
    user_rating: number;
    usage_count: number;
    success_rate: number;
    content_warnings: string[];
}

interface ScenarioManagerProps {
    matchUserId: string;
    matchId?: string;
    onComplete?: (results: any) => void;
    onClose?: () => void;
}

const ScenarioManager: React.FC<ScenarioManagerProps> = ({
    matchUserId,
    matchId,
    onComplete,
    onClose
}) => {
    const [activeStep, setActiveStep] = useState(0);
    const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [simulationResults, setSimulationResults] = useState<any>(null);
    const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

    const steps = [
        {
            label: 'Select Scenario',
            description: 'Choose a scenario to explore with your match',
            icon: <LibraryBooks />
        },
        {
            label: 'Simulation Theater',
            description: 'Watch your AI avatars interact in real-time',
            icon: <PlayArrow />
        },
        {
            label: 'Results & Analysis',
            description: 'Review compatibility insights and recommendations',
            icon: <Assessment />
        }
    ];

    const handleScenarioSelect = (scenario: Scenario) => {
        setSelectedScenario(scenario);
        setConfirmDialogOpen(true);
    };

    const handleConfirmScenario = async () => {
        if (!selectedScenario) return;

        setLoading(true);
        setError(null);
        setConfirmDialogOpen(false);

        try {
            const response = await fetch('/api/v1/scenarios/simulations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    user2_id: matchUserId,
                    scenario_id: selectedScenario.id,
                    match_id: matchId,
                    cultural_context: null, // Could be determined from user preferences
                    language: 'en'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to create simulation session');
            }

            const data = await response.json();
            setSessionId(data.session_id);
            setActiveStep(1);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create simulation');
        } finally {
            setLoading(false);
        }
    };

    const handleSimulationComplete = (results: any) => {
        setSimulationResults(results);
        setActiveStep(2);
    };

    const handleSimulationExit = () => {
        if (activeStep === 1) {
            // If simulation is in progress, ask for confirmation
            setConfirmDialogOpen(true);
        } else {
            handleClose();
        }
    };

    const handleClose = () => {
        if (onClose) {
            onClose();
        }
    };

    const handleFinish = () => {
        if (onComplete && simulationResults) {
            onComplete(simulationResults);
        } else {
            handleClose();
        }
    };

    const renderStepContent = () => {
        switch (activeStep) {
            case 0:
                return (
                    <ScenarioLibrary
                        matchUserId={matchUserId}
                        matchId={matchId}
                        onScenarioSelect={handleScenarioSelect}
                        showRecommendations={true}
                    />
                );
            case 1:
                return sessionId ? (
                    <SimulationTheater
                        sessionId={sessionId}
                        onComplete={handleSimulationComplete}
                        onExit={handleSimulationExit}
                    />
                ) : (
                    <Alert severity="error">
                        No simulation session available
                    </Alert>
                );
            case 2:
                return (
                    <Box>
                        <Typography variant="h5" gutterBottom>
                            Simulation Complete!
                        </Typography>
                        <Typography variant="body1" paragraph>
                            Your AI avatars have completed the scenario simulation.
                            Review the detailed compatibility analysis and insights below.
                        </Typography>

                        {simulationResults && (
                            <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    Overall Results
                                </Typography>
                                <Box display="flex" gap={4} mb={3}>
                                    <Box textAlign="center">
                                        <Typography variant="h4" color="primary.main">
                                            {Math.round(simulationResults.results?.overall_success_score * 100 || 0)}%
                                        </Typography>
                                        <Typography variant="caption">
                                            Overall Success
                                        </Typography>
                                    </Box>
                                    <Box textAlign="center">
                                        <Typography variant="h4" color="secondary.main">
                                            {Math.round(simulationResults.results?.collaboration_score * 100 || 0)}%
                                        </Typography>
                                        <Typography variant="caption">
                                            Collaboration
                                        </Typography>
                                    </Box>
                                    <Box textAlign="center">
                                        <Typography variant="h4" color="success.main">
                                            {Math.round(simulationResults.results?.communication_score * 100 || 0)}%
                                        </Typography>
                                        <Typography variant="caption">
                                            Communication
                                        </Typography>
                                    </Box>
                                </Box>

                                {simulationResults.results?.strengths_identified && (
                                    <Box mb={2}>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Relationship Strengths
                                        </Typography>
                                        <ul>
                                            {simulationResults.results.strengths_identified.map((strength: string, index: number) => (
                                                <li key={index}>
                                                    <Typography variant="body2">{strength}</Typography>
                                                </li>
                                            ))}
                                        </ul>
                                    </Box>
                                )}

                                {simulationResults.results?.relationship_recommendations && (
                                    <Box mb={2}>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Recommendations
                                        </Typography>
                                        <ul>
                                            {simulationResults.results.relationship_recommendations.map((rec: string, index: number) => (
                                                <li key={index}>
                                                    <Typography variant="body2">{rec}</Typography>
                                                </li>
                                            ))}
                                        </ul>
                                    </Box>
                                )}
                            </Paper>
                        )}

                        <Box display="flex" justifyContent="space-between">
                            <Button
                                variant="outlined"
                                onClick={() => setActiveStep(0)}
                            >
                                Try Another Scenario
                            </Button>
                            <Button
                                variant="contained"
                                startIcon={<CheckCircle />}
                                onClick={handleFinish}
                            >
                                View Full Report
                            </Button>
                        </Box>
                    </Box>
                );
            default:
                return null;
        }
    };

    if (loading) {
        return (
            <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
                <CircularProgress sx={{ mb: 2 }} />
                <Typography>Setting up simulation...</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ width: '100%', height: '100%' }}>
            {/* Stepper - only show if not in theater mode */}
            {activeStep !== 1 && (
                <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
                    <Stepper activeStep={activeStep} alternativeLabel>
                        {steps.map((step, index) => (
                            <Step key={step.label}>
                                <StepLabel
                                    icon={step.icon}
                                    optional={
                                        <Typography variant="caption">
                                            {step.description}
                                        </Typography>
                                    }
                                >
                                    {step.label}
                                </StepLabel>
                            </Step>
                        ))}
                    </Stepper>
                </Paper>
            )}

            {/* Error Display */}
            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Step Content */}
            <Box sx={{ flexGrow: 1 }}>
                {renderStepContent()}
            </Box>

            {/* Confirmation Dialog */}
            <Dialog
                open={confirmDialogOpen}
                onClose={() => setConfirmDialogOpen(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>
                    {selectedScenario ? 'Confirm Scenario Selection' : 'Exit Simulation?'}
                </DialogTitle>
                <DialogContent>
                    {selectedScenario ? (
                        <Box>
                            <Typography variant="body1" paragraph>
                                You've selected: <strong>{selectedScenario.title}</strong>
                            </Typography>
                            <Typography variant="body2" color="text.secondary" paragraph>
                                {selectedScenario.description}
                            </Typography>
                            <Typography variant="body2" paragraph>
                                This simulation will take approximately {selectedScenario.estimated_duration_minutes} minutes
                                and will explore {selectedScenario.personality_dimensions.join(', ')} personality dimensions.
                            </Typography>
                            <Typography variant="body2">
                                Are you ready to start the simulation with your match?
                            </Typography>
                        </Box>
                    ) : (
                        <Typography variant="body1">
                            Are you sure you want to exit the simulation? Any progress will be lost.
                        </Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setConfirmDialogOpen(false)}>
                        Cancel
                    </Button>
                    <Button
                        variant="contained"
                        onClick={selectedScenario ? handleConfirmScenario : handleClose}
                        color={selectedScenario ? 'primary' : 'error'}
                    >
                        {selectedScenario ? 'Start Simulation' : 'Exit'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ScenarioManager;