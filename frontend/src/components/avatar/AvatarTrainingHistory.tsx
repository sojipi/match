/**
 * Avatar Training History Component
 */
import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Chip,
    Alert,
    CircularProgress,
    Paper,
    Stack,
    Divider
} from '@mui/material';
import {
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Schedule as ScheduleIcon,
    Psychology as PsychologyIcon,
    Refresh as RefreshIcon,
    TrendingUp as TrendingUpIcon,
    Build as BuildIcon
} from '@mui/icons-material';

import { AvatarTrainingSession } from '../../types/avatar';
import { avatarApi } from '../../services/avatarApi';

interface AvatarTrainingHistoryProps {
    avatarId: string;
}

const AvatarTrainingHistory: React.FC<AvatarTrainingHistoryProps> = ({ avatarId }) => {
    const [trainingSessions, setTrainingSessions] = useState<AvatarTrainingSession[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadTrainingHistory();
    }, [avatarId]);

    const loadTrainingHistory = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await avatarApi.getTrainingHistory(avatarId);
            setTrainingSessions(data);
        } catch (err: any) {
            setError('Failed to load training history');
            console.error('Error loading training history:', err);
        } finally {
            setLoading(false);
        }
    };

    const getTrainingTypeIcon = (trainingType: string) => {
        switch (trainingType) {
            case 'initial':
                return <PsychologyIcon />;
            case 'personality_update':
                return <RefreshIcon />;
            case 'performance_improvement':
                return <TrendingUpIcon />;
            case 'manual_retrain':
                return <BuildIcon />;
            default:
                return <ScheduleIcon />;
        }
    };

    const getTrainingTypeLabel = (trainingType: string) => {
        switch (trainingType) {
            case 'initial':
                return 'Initial Training';
            case 'personality_update':
                return 'Personality Update';
            case 'performance_improvement':
                return 'Performance Improvement';
            case 'manual_retrain':
                return 'Manual Retrain';
            default:
                return trainingType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
    };

    const getStatusColor = (success: boolean) => {
        return success ? 'success' : 'error';
    };

    const getStatusIcon = (success: boolean) => {
        return success ? <CheckCircleIcon /> : <ErrorIcon />;
    };

    const formatDuration = (seconds?: number) => {
        if (!seconds) return 'Unknown';
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds}s`;
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" onClose={() => setError(null)}>
                {error}
            </Alert>
        );
    }

    if (trainingSessions.length === 0) {
        return (
            <Card>
                <CardContent>
                    <Box textAlign="center" py={4}>
                        <ScheduleIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" gutterBottom>
                            No Training History
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Your avatar hasn't been trained yet. Training will begin automatically
                            when you complete your personality assessment or make customizations.
                        </Typography>
                    </Box>
                </CardContent>
            </Card>
        );
    }

    return (
        <Box>
            <Box mb={3}>
                <Typography variant="h6" component="h2" gutterBottom>
                    Training History
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Track your avatar's training sessions and improvements over time
                </Typography>
            </Box>

            {/* Training Statistics */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                        Training Statistics
                    </Typography>
                    <Box display="flex" gap={4} flexWrap="wrap">
                        <Box>
                            <Typography variant="h4" color="primary.main" fontWeight="bold">
                                {trainingSessions.length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Total Sessions
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="h4" color="success.main" fontWeight="bold">
                                {trainingSessions.filter(s => s.success).length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Successful
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="h4" color="error.main" fontWeight="bold">
                                {trainingSessions.filter(s => !s.success).length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Failed
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="h4" color="info.main" fontWeight="bold">
                                {Math.round(
                                    trainingSessions
                                        .filter(s => s.duration_seconds)
                                        .reduce((sum, s) => sum + (s.duration_seconds || 0), 0) /
                                    trainingSessions.filter(s => s.duration_seconds).length || 0
                                )}s
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Avg Duration
                            </Typography>
                        </Box>
                    </Box>
                </CardContent>
            </Card>

            {/* Training Sessions List */}
            <Stack spacing={2}>
                {trainingSessions.map((session, index) => (
                    <Paper key={session.id} elevation={1} sx={{ p: 2 }}>
                        <Box display="flex" alignItems="flex-start" gap={2}>
                            {/* Status Icon */}
                            <Box
                                sx={{
                                    width: 40,
                                    height: 40,
                                    borderRadius: '50%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    bgcolor: session.success ? 'success.light' : 'error.light',
                                    color: session.success ? 'success.contrastText' : 'error.contrastText',
                                    mt: 0.5
                                }}
                            >
                                {getTrainingTypeIcon(session.training_type)}
                            </Box>

                            {/* Session Details */}
                            <Box sx={{ flexGrow: 1 }}>
                                <Box display="flex" alignItems="center" gap={1} mb={1}>
                                    <Typography variant="subtitle1" fontWeight="medium">
                                        {getTrainingTypeLabel(session.training_type)}
                                    </Typography>
                                    <Chip
                                        label={session.success ? 'Success' : 'Failed'}
                                        size="small"
                                        color={getStatusColor(session.success) as any}
                                        icon={getStatusIcon(session.success)}
                                    />
                                </Box>

                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                    {session.trigger_reason}
                                </Typography>

                                <Box display="flex" gap={2} flexWrap="wrap" mt={1}>
                                    <Typography variant="caption" color="text.secondary">
                                        Started: {formatDate(session.started_at)}
                                    </Typography>
                                    {session.completed_at && (
                                        <Typography variant="caption" color="text.secondary">
                                            Completed: {formatDate(session.completed_at)}
                                        </Typography>
                                    )}
                                    {session.duration_seconds && (
                                        <Typography variant="caption" color="text.secondary">
                                            Duration: {formatDuration(session.duration_seconds)}
                                        </Typography>
                                    )}
                                </Box>

                                {session.error_message && (
                                    <Alert severity="error" sx={{ mt: 1 }}>
                                        <Typography variant="body2">
                                            {session.error_message}
                                        </Typography>
                                    </Alert>
                                )}
                            </Box>
                        </Box>

                        {/* Connector line (except for last item) */}
                        {index < trainingSessions.length - 1 && (
                            <Box
                                sx={{
                                    width: 2,
                                    height: 20,
                                    bgcolor: 'divider',
                                    ml: 2.5,
                                    mt: 1
                                }}
                            />
                        )}
                    </Paper>
                ))}
            </Stack>
        </Box>
    );
};

export default AvatarTrainingHistory;