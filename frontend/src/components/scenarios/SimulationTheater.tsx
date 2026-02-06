import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Paper,
    Avatar,
    Chip,
    Button,
    LinearProgress,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Tooltip,
    Fab,
    Zoom,
    Alert
} from '@mui/material';
import {
    PlayArrow,
    Pause,
    Stop,
    Feedback,
    Psychology,
    TrendingUp,
    Schedule,
    People,
    Chat,
    Lightbulb,
    Warning,
    CheckCircle,
    Error as ErrorIcon
} from '@mui/icons-material';

interface SimulationMessage {
    message_id: string;
    sender_name: string;
    sender_type: string;
    content: string;
    message_type: string;
    scenario_phase: string;
    timestamp: string;
    is_highlighted: boolean;
}

interface SimulationSession {
    session_id: string;
    match_id?: string;
    scenario: {
        id: string;
        name: string;
        title: string;
        description: string;
        category: string;
        difficulty_level: number;
    };
    participants: Array<{
        user_id: string;
        name: string;
    }>;
    status: string;
    current_phase: string;
    started_at?: string;
    ended_at?: string;
    duration_seconds?: number;
    message_count: number;
    engagement_score: number;
    scenario_completion_score?: number;
    collaboration_score?: number;
    messages: SimulationMessage[];
}

interface SimulationTheaterProps {
    sessionId: string;
    onComplete: (results: any) => void;
    onExit: () => void;
}

const SimulationTheater: React.FC<SimulationTheaterProps> = ({
    sessionId,
    onComplete,
    onExit
}) => {
    const [session, setSession] = useState<SimulationSession | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [showFeedbackDialog, setShowFeedbackDialog] = useState(false);
    const [currentPhase, setCurrentPhase] = useState('');
    const [phaseProgress, setPhaseProgress] = useState(0);
    const [liveScores, setLiveScores] = useState({
        collaboration: 0,
        communication: 0,
        engagement: 0
    });

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        loadSession();
        setupWebSocket();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [sessionId]);

    useEffect(() => {
        scrollToBottom();
    }, [session?.messages]);

    const loadSession = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/v1/scenarios/simulations/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load simulation session');
            }

            const data = await response.json();
            setSession(data);
            setCurrentPhase(data.current_phase);
            setIsPlaying(data.status === 'active');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load session');
        } finally {
            setLoading(false);
        }
    };

    const setupWebSocket = () => {
        const token = localStorage.getItem('token');
        const wsUrl = `ws://localhost:8000/ws/simulation/${sessionId}?token=${token}`;

        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
            console.log('WebSocket connected to simulation');
        };

        wsRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        wsRef.current.onclose = () => {
            console.log('WebSocket disconnected from simulation');
        };

        wsRef.current.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    };

    const handleWebSocketMessage = (data: any) => {
        switch (data.type) {
            case 'message':
                if (session) {
                    setSession(prev => prev ? {
                        ...prev,
                        messages: [...prev.messages, data.message],
                        message_count: prev.message_count + 1
                    } : null);
                }
                break;
            case 'phase_change':
                setCurrentPhase(data.phase);
                setPhaseProgress(0);
                break;
            case 'score_update':
                setLiveScores(data.scores);
                break;
            case 'session_complete':
                setIsPlaying(false);
                onComplete(data.results);
                break;
            case 'progress_update':
                setPhaseProgress(data.progress);
                break;
        }
    };

    const startSimulation = async () => {
        try {
            const response = await fetch(`/api/v1/scenarios/simulations/${sessionId}/start`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to start simulation');
            }

            setIsPlaying(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start simulation');
        }
    };

    const completeSimulation = async () => {
        try {
            const response = await fetch(`/api/v1/scenarios/simulations/${sessionId}/complete`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to complete simulation');
            }

            const results = await response.json();
            setIsPlaying(false);
            onComplete(results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to complete simulation');
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const getPhaseIcon = (phase: string) => {
        switch (phase) {
            case 'setup': return <Psychology />;
            case 'scenario_presentation': return <Chat />;
            case 'interaction': return <People />;
            case 'resolution': return <CheckCircle />;
            case 'analysis': return <TrendingUp />;
            case 'completed': return <CheckCircle />;
            default: return <Schedule />;
        }
    };

    const getPhaseLabel = (phase: string) => {
        switch (phase) {
            case 'setup': return 'Setting Up';
            case 'scenario_presentation': return 'Scenario Presentation';
            case 'interaction': return 'Active Discussion';
            case 'resolution': return 'Finding Resolution';
            case 'analysis': return 'Analyzing Results';
            case 'completed': return 'Completed';
            default: return phase;
        }
    };

    const getMessageTypeIcon = (type: string) => {
        switch (type) {
            case 'system': return <Psychology color="primary" />;
            case 'guidance': return <Lightbulb color="warning" />;
            case 'action': return <PlayArrow color="action" />;
            default: return <Chat color="action" />;
        }
    };

    const getSenderAvatar = (message: SimulationMessage) => {
        if (message.sender_type === 'scenario_agent') {
            return <Avatar sx={{ bgcolor: 'primary.main' }}><Psychology /></Avatar>;
        } else if (message.sender_type === 'user_avatar') {
            return <Avatar>{message.sender_name.charAt(0)}</Avatar>;
        } else {
            return <Avatar sx={{ bgcolor: 'grey.500' }}><Chat /></Avatar>;
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <Typography>Loading simulation...</Typography>
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

    if (!session) {
        return (
            <Alert severity="warning" sx={{ mb: 2 }}>
                Simulation session not found
            </Alert>
        );
    }

    return (
        <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h5">
                        {session.scenario.title}
                    </Typography>
                    <Box display="flex" gap={1}>
                        <Chip
                            icon={getPhaseIcon(currentPhase)}
                            label={getPhaseLabel(currentPhase)}
                            color="primary"
                        />
                        <Chip
                            label={session.scenario.category}
                            variant="outlined"
                        />
                    </Box>
                </Box>

                {/* Phase Progress */}
                <Box mb={2}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="body2" color="text.secondary">
                            Simulation Progress
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            {Math.round(phaseProgress)}%
                        </Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={phaseProgress} />
                </Box>

                {/* Live Scores */}
                <Box display="flex" gap={2}>
                    <Box textAlign="center">
                        <Typography variant="caption" color="text.secondary">
                            Collaboration
                        </Typography>
                        <Typography variant="h6" color="primary.main">
                            {Math.round(liveScores.collaboration * 100)}%
                        </Typography>
                    </Box>
                    <Box textAlign="center">
                        <Typography variant="caption" color="text.secondary">
                            Communication
                        </Typography>
                        <Typography variant="h6" color="secondary.main">
                            {Math.round(liveScores.communication * 100)}%
                        </Typography>
                    </Box>
                    <Box textAlign="center">
                        <Typography variant="caption" color="text.secondary">
                            Engagement
                        </Typography>
                        <Typography variant="h6" color="success.main">
                            {Math.round(liveScores.engagement * 100)}%
                        </Typography>
                    </Box>
                </Box>
            </Paper>

            {/* Messages Area */}
            <Box sx={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <Paper
                    elevation={1}
                    sx={{
                        flexGrow: 1,
                        overflow: 'auto',
                        p: 2,
                        backgroundColor: 'grey.50'
                    }}
                >
                    {session.messages.map((message) => (
                        <Box
                            key={message.message_id}
                            sx={{
                                mb: 2,
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: 2,
                                p: 2,
                                backgroundColor: message.is_highlighted ? 'warning.light' : 'white',
                                borderRadius: 2,
                                border: message.is_highlighted ? '2px solid' : '1px solid',
                                borderColor: message.is_highlighted ? 'warning.main' : 'grey.300'
                            }}
                        >
                            {getSenderAvatar(message)}
                            <Box sx={{ flexGrow: 1 }}>
                                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                                    <Box display="flex" alignItems="center" gap={1}>
                                        <Typography variant="subtitle2">
                                            {message.sender_name}
                                        </Typography>
                                        {getMessageTypeIcon(message.message_type)}
                                        {message.is_highlighted && (
                                            <Chip label="Key Moment" size="small" color="warning" />
                                        )}
                                    </Box>
                                    <Typography variant="caption" color="text.secondary">
                                        {new Date(message.timestamp).toLocaleTimeString()}
                                    </Typography>
                                </Box>
                                <Typography variant="body1">
                                    {message.content}
                                </Typography>
                                {message.scenario_phase && (
                                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                                        Phase: {getPhaseLabel(message.scenario_phase)}
                                    </Typography>
                                )}
                            </Box>
                        </Box>
                    ))}
                    <div ref={messagesEndRef} />
                </Paper>
            </Box>

            {/* Control Panel */}
            <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box display="flex" gap={1}>
                        {!isPlaying && session.status === 'scheduled' && (
                            <Button
                                variant="contained"
                                startIcon={<PlayArrow />}
                                onClick={startSimulation}
                            >
                                Start Simulation
                            </Button>
                        )}
                        {isPlaying && (
                            <Button
                                variant="contained"
                                color="error"
                                startIcon={<Stop />}
                                onClick={completeSimulation}
                            >
                                Complete Simulation
                            </Button>
                        )}
                    </Box>

                    <Box display="flex" gap={1}>
                        <Tooltip title="Provide Feedback">
                            <IconButton
                                color="primary"
                                onClick={() => setShowFeedbackDialog(true)}
                            >
                                <Feedback />
                            </IconButton>
                        </Tooltip>
                        <Button variant="outlined" onClick={onExit}>
                            Exit Theater
                        </Button>
                    </Box>
                </Box>

                {/* Session Info */}
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                    <Typography variant="body2" color="text.secondary">
                        Participants: {session.participants.map(p => p.name).join(', ')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Messages: {session.message_count} | Duration: {
                            session.duration_seconds
                                ? `${Math.floor(session.duration_seconds / 60)}:${(session.duration_seconds % 60).toString().padStart(2, '0')}`
                                : 'In progress'
                        }
                    </Typography>
                </Box>
            </Paper>

            {/* Floating Action Buttons */}
            <Box sx={{ position: 'fixed', bottom: 16, right: 16 }}>
                <Zoom in={isPlaying}>
                    <Fab
                        color="primary"
                        size="small"
                        onClick={() => setShowFeedbackDialog(true)}
                        sx={{ mb: 1 }}
                    >
                        <Feedback />
                    </Fab>
                </Zoom>
            </Box>

            {/* Feedback Dialog */}
            <Dialog
                open={showFeedbackDialog}
                onClose={() => setShowFeedbackDialog(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>
                    Provide Guidance to Your Avatar
                </DialogTitle>
                <DialogContent>
                    <Typography variant="body2" color="text.secondary" paragraph>
                        You can provide guidance to help your AI avatar better represent you in this scenario.
                        Your feedback will influence how your avatar responds in future interactions.
                    </Typography>
                    {/* Add feedback form here */}
                    <Alert severity="info">
                        Feedback functionality will be implemented in the next iteration.
                    </Alert>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowFeedbackDialog(false)}>
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default SimulationTheater;