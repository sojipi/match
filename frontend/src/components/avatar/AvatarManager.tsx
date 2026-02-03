/**
 * AI Avatar Management Component
 */
import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    Grid,
    Chip,
    LinearProgress,
    Alert,
    CircularProgress,
    Tabs,
    Tab,
    Paper
} from '@mui/material';
import {
    Person as PersonIcon,
    Psychology as PsychologyIcon,
    Chat as ChatIcon,
    TrendingUp as TrendingUpIcon,
    Refresh as RefreshIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';

import { AIAvatar, AvatarCompletenessAnalysis } from '../../types/avatar';
import { avatarApi } from '../../services/avatarApi';
import AvatarVisualization from './AvatarVisualization';
import AvatarCustomization from './AvatarCustomization';
import AvatarCompleteness from './AvatarCompleteness';
import AvatarTrainingHistory from './AvatarTrainingHistory';

interface AvatarManagerProps {
    userId: string;
    onAvatarUpdate?: (avatar: AIAvatar) => void;
}

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
            id={`avatar-tabpanel-${index}`}
            aria-labelledby={`avatar-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
}

const AvatarManager: React.FC<AvatarManagerProps> = ({ userId, onAvatarUpdate }) => {
    const [avatar, setAvatar] = useState<AIAvatar | null>(null);
    const [completenessAnalysis, setCompletenessAnalysis] = useState<AvatarCompletenessAnalysis | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState(0);
    const [isCreating, setIsCreating] = useState(false);
    const [isRetraining, setIsRetraining] = useState(false);

    useEffect(() => {
        loadAvatar();
    }, [userId]);

    const loadAvatar = async () => {
        try {
            setLoading(true);
            setError(null);

            const avatarData = await avatarApi.getAvatar(userId);
            setAvatar(avatarData);

            // Load completeness analysis
            const analysis = await avatarApi.getCompletenessAnalysis(avatarData.id);
            setCompletenessAnalysis(analysis);

            if (onAvatarUpdate) {
                onAvatarUpdate(avatarData);
            }
        } catch (err: any) {
            // Check if it's a 404 error (avatar not found)
            if (err.status === 404) {
                // Avatar doesn't exist yet - this is expected
                setAvatar(null);
                setError(null);
            } else {
                setError('Failed to load avatar');
                console.error('Error loading avatar:', err);
            }
        } finally {
            setLoading(false);
        }
    };

    const createAvatar = async () => {
        try {
            setIsCreating(true);
            setError(null);

            const newAvatar = await avatarApi.createAvatar(userId);
            setAvatar(newAvatar);

            // Load completeness analysis
            const analysis = await avatarApi.getCompletenessAnalysis(newAvatar.id);
            setCompletenessAnalysis(analysis);

            if (onAvatarUpdate) {
                onAvatarUpdate(newAvatar);
            }
        } catch (err: any) {
            setError(err.message || 'Failed to create avatar');
            console.error('Error creating avatar:', err);
        } finally {
            setIsCreating(false);
        }
    };

    const retrainAvatar = async () => {
        if (!avatar) return;

        try {
            setIsRetraining(true);
            setError(null);

            const updatedAvatar = await avatarApi.retrainAvatar(avatar.id);
            setAvatar(updatedAvatar);

            // Reload completeness analysis
            const analysis = await avatarApi.getCompletenessAnalysis(updatedAvatar.id);
            setCompletenessAnalysis(analysis);

            if (onAvatarUpdate) {
                onAvatarUpdate(updatedAvatar);
            }
        } catch (err: any) {
            setError(err.message || 'Failed to retrain avatar');
            console.error('Error retraining avatar:', err);
        } finally {
            setIsRetraining(false);
        }
    };

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'success';
            case 'training': return 'warning';
            case 'creating': return 'info';
            case 'error': return 'error';
            default: return 'default';
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'active': return 'Active';
            case 'training': return 'Training';
            case 'creating': return 'Creating';
            case 'error': return 'Error';
            default: return status;
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    if (!avatar) {
        return (
            <Card>
                <CardContent>
                    <Box textAlign="center" py={4}>
                        <PsychologyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h5" gutterBottom>
                            Create Your AI Avatar
                        </Typography>
                        <Typography variant="body1" color="text.secondary" paragraph>
                            Your AI avatar represents your personality in conversations and matchmaking.
                            Complete your personality assessment first, then create your avatar.
                        </Typography>

                        {error && (
                            <Alert severity="error" sx={{ mb: 2 }}>
                                {error}
                            </Alert>
                        )}

                        <Button
                            variant="contained"
                            size="large"
                            onClick={createAvatar}
                            disabled={isCreating}
                            startIcon={isCreating ? <CircularProgress size={20} /> : <PersonIcon />}
                        >
                            {isCreating ? 'Creating Avatar...' : 'Create Avatar'}
                        </Button>
                    </Box>
                </CardContent>
            </Card>
        );
    }

    return (
        <Box>
            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Avatar Overview */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Grid container spacing={3} alignItems="center">
                        <Grid item xs={12} md={8}>
                            <Box display="flex" alignItems="center" gap={2} mb={2}>
                                <PsychologyIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                                <Box>
                                    <Typography variant="h5" component="h2">
                                        {avatar.name}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {avatar.description}
                                    </Typography>
                                </Box>
                                <Chip
                                    label={getStatusLabel(avatar.status)}
                                    color={getStatusColor(avatar.status) as any}
                                    size="small"
                                />
                            </Box>

                            <Grid container spacing={2}>
                                <Grid item xs={6} sm={3}>
                                    <Typography variant="body2" color="text.secondary">
                                        Completeness
                                    </Typography>
                                    <Box display="flex" alignItems="center" gap={1}>
                                        <LinearProgress
                                            variant="determinate"
                                            value={avatar.completeness_score * 100}
                                            sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                                        />
                                        <Typography variant="body2" fontWeight="bold">
                                            {Math.round(avatar.completeness_score * 100)}%
                                        </Typography>
                                    </Box>
                                </Grid>

                                <Grid item xs={6} sm={3}>
                                    <Typography variant="body2" color="text.secondary">
                                        Authenticity
                                    </Typography>
                                    <Box display="flex" alignItems="center" gap={1}>
                                        <LinearProgress
                                            variant="determinate"
                                            value={avatar.authenticity_score * 100}
                                            sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                                            color="secondary"
                                        />
                                        <Typography variant="body2" fontWeight="bold">
                                            {Math.round(avatar.authenticity_score * 100)}%
                                        </Typography>
                                    </Box>
                                </Grid>

                                <Grid item xs={6} sm={3}>
                                    <Typography variant="body2" color="text.secondary">
                                        Consistency
                                    </Typography>
                                    <Box display="flex" alignItems="center" gap={1}>
                                        <LinearProgress
                                            variant="determinate"
                                            value={avatar.consistency_score * 100}
                                            sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                                            color="info"
                                        />
                                        <Typography variant="body2" fontWeight="bold">
                                            {Math.round(avatar.consistency_score * 100)}%
                                        </Typography>
                                    </Box>
                                </Grid>

                                <Grid item xs={6} sm={3}>
                                    <Typography variant="body2" color="text.secondary">
                                        Training Sessions
                                    </Typography>
                                    <Typography variant="h6" fontWeight="bold">
                                        {avatar.training_iterations}
                                    </Typography>
                                </Grid>
                            </Grid>
                        </Grid>

                        <Grid item xs={12} md={4}>
                            <Box display="flex" gap={1} flexWrap="wrap" justifyContent="flex-end">
                                <Button
                                    variant="outlined"
                                    size="small"
                                    onClick={retrainAvatar}
                                    disabled={isRetraining || avatar.status === 'training'}
                                    startIcon={isRetraining ? <CircularProgress size={16} /> : <RefreshIcon />}
                                >
                                    {isRetraining ? 'Retraining...' : 'Retrain'}
                                </Button>
                                <Button
                                    variant="outlined"
                                    size="small"
                                    onClick={loadAvatar}
                                    startIcon={<RefreshIcon />}
                                >
                                    Refresh
                                </Button>
                            </Box>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {/* Avatar Management Tabs */}
            <Paper sx={{ width: '100%' }}>
                <Tabs
                    value={activeTab}
                    onChange={handleTabChange}
                    aria-label="avatar management tabs"
                    variant="scrollable"
                    scrollButtons="auto"
                >
                    <Tab
                        label="Overview"
                        icon={<PersonIcon />}
                        iconPosition="start"
                        id="avatar-tab-0"
                        aria-controls="avatar-tabpanel-0"
                    />
                    <Tab
                        label="Completeness"
                        icon={<TrendingUpIcon />}
                        iconPosition="start"
                        id="avatar-tab-1"
                        aria-controls="avatar-tabpanel-1"
                    />
                    <Tab
                        label="Customization"
                        icon={<SettingsIcon />}
                        iconPosition="start"
                        id="avatar-tab-2"
                        aria-controls="avatar-tabpanel-2"
                    />
                    <Tab
                        label="Training History"
                        icon={<ChatIcon />}
                        iconPosition="start"
                        id="avatar-tab-3"
                        aria-controls="avatar-tabpanel-3"
                    />
                </Tabs>

                <TabPanel value={activeTab} index={0}>
                    <AvatarVisualization avatar={avatar} />
                </TabPanel>

                <TabPanel value={activeTab} index={1}>
                    {completenessAnalysis && (
                        <AvatarCompleteness
                            analysis={completenessAnalysis}
                            onImprove={() => setActiveTab(2)}
                        />
                    )}
                </TabPanel>

                <TabPanel value={activeTab} index={2}>
                    <AvatarCustomization
                        avatar={avatar}
                        onCustomizationApplied={loadAvatar}
                    />
                </TabPanel>

                <TabPanel value={activeTab} index={3}>
                    <AvatarTrainingHistory avatarId={avatar.id} />
                </TabPanel>
            </Paper>
        </Box>
    );
};

export default AvatarManager;