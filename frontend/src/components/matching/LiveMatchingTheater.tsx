/**
 * Live Matching Theater - Real-time AI conversation viewing interface
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    Chip,
    Badge,
    Alert,
    LinearProgress,
    Tooltip,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import {
    Assessment,
    People,
    Warning,
    Send,
    Close,
    Fullscreen,
    FullscreenExit,
    VolumeUp,
    VolumeOff
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { Drawer } from '@mui/material';

import { websocketService } from '../../services/websocketService';
import { useAppSelector } from '../../hooks/redux';
import {
    ConversationMessage,
    CompatibilityUpdate,
    UserReaction,
    SessionViewer,
    TheaterState
} from '../../types/matching';
import ConversationDisplay from './ConversationDisplay';
import CompatibilityPanel from './CompatibilityPanel';
import ViewersPanel from './ViewersPanel';
import AvatarDisplay from './AvatarDisplay';
import UserControls from './UserControls';

interface LiveMatchingTheaterProps {
    sessionId?: string;
    onSessionEnd?: () => void;
}

const LiveMatchingTheater: React.FC<LiveMatchingTheaterProps> = ({
    sessionId: propSessionId,
    onSessionEnd
}) => {
    const { sessionId: paramSessionId } = useParams<{ sessionId: string }>();
    const navigate = useNavigate();
    const sessionId = propSessionId || paramSessionId;

    // Get auth token from Redux store
    const { token } = useAppSelector(state => state.auth);

    // State management
    const [state, setState] = useState<TheaterState>({
        isConnected: false,
        messages: [],
        compatibility: {
            overall_score: 0,
            dimension_scores: {
                personality: 0,
                communication: 0,
                values: 0,
                lifestyle: 0
            },
            trend_data: [],
            insights: [],
            strengths: [],
            challenges: []
        },
        viewers: [],
        userReactions: [],
        isLoading: true,
        showCompatibilityPanel: false,
        showViewersPanel: false,
        showCompletionDialog: false,
        showQuotaExceededDialog: false,
        quotaErrorDetails: null
    });

    // UI state
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [soundEnabled, setSoundEnabled] = useState(true);
    const [showGuidanceDialog, setShowGuidanceDialog] = useState(false);
    const [guidanceText, setGuidanceText] = useState('');
    const [selectedAvatar, setSelectedAvatar] = useState<string>('');

    // Refs
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const theaterRef = useRef<HTMLDivElement>(null);

    // WebSocket event handlers
    const handleConnectionEstablished = useCallback((data: any) => {
        setState(prev => ({
            ...prev,
            isConnected: true,
            isLoading: false,
            connectionError: undefined, // Clear any previous connection errors
            session: data.session
        }));
    }, []);

    const handleAIMessage = useCallback((data: any) => {
        const message: ConversationMessage = {
            message_id: data.message_id,
            session_id: sessionId!,
            sender_type: data.sender_type,
            sender_name: data.sender_name,
            content: data.content,
            message_type: data.message_type || 'text',
            emotion_indicators: data.emotion_indicators || [],
            compatibility_impact: data.compatibility_impact,
            is_highlighted: data.is_highlighted || false,
            timestamp: data.timestamp
        };

        setState(prev => ({
            ...prev,
            messages: [...prev.messages, message]
        }));

        // Play sound notification if enabled
        if (soundEnabled && data.is_highlighted) {
            playNotificationSound();
        }

        // Auto-scroll to bottom
        setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }, [sessionId, soundEnabled]);

    const handleCompatibilityUpdate = useCallback((data: CompatibilityUpdate) => {
        setState(prev => ({
            ...prev,
            compatibility: {
                ...prev.compatibility,
                overall_score: data.overall_score,
                dimension_scores: data.dimension_scores,
                insights: data.key_insights,
                trend_data: [
                    ...prev.compatibility.trend_data,
                    {
                        timestamp: data.timestamp,
                        score: data.overall_score
                    }
                ].slice(-20) // Keep last 20 data points
            }
        }));
    }, []);

    const handleUserJoined = useCallback((data: any) => {
        const viewer: SessionViewer = {
            user_id: data.user_id,
            user_name: data.user_name,
            connected_at: data.timestamp
        };

        setState(prev => ({
            ...prev,
            viewers: [...prev.viewers.filter(v => v.user_id !== data.user_id), viewer]
        }));
    }, []);

    const handleUserLeft = useCallback((data: any) => {
        setState(prev => ({
            ...prev,
            viewers: prev.viewers.filter(v => v.user_id !== data.user_id)
        }));
    }, []);

    const handleUserReaction = useCallback((data: any) => {
        const reaction: UserReaction = {
            reaction_id: `${data.user_id}_${data.message_id}_${Date.now()}`,
            user_id: data.user_id,
            user_name: data.user_name,
            message_id: data.message_id,
            reaction_type: data.reaction_type,
            timestamp: data.timestamp
        };

        setState(prev => ({
            ...prev,
            userReactions: [...prev.userReactions, reaction]
        }));
    }, []);

    const handleSessionStatusChange = useCallback((data: any) => {
        setState(prev => ({
            ...prev,
            session: prev.session ? { ...prev.session, status: data.status } : undefined
        }));

        if (data.status === 'completed') {
            // Session ended, show completion message and give user more time
            setState(prev => ({
                ...prev,
                showCompletionDialog: true
            }));

            // Auto-redirect after longer delay (10 seconds instead of 3)
            setTimeout(() => {
                if (onSessionEnd) {
                    onSessionEnd();
                } else {
                    navigate('/matches');
                }
            }, 10000);
        }
    }, [navigate, onSessionEnd]);

    const handleError = useCallback((data: any) => {
        // Check if it's a Gemini quota error
        if (data.type === 'gemini_quota_exceeded') {
            setState(prev => ({
                ...prev,
                showQuotaExceededDialog: true,
                quotaErrorDetails: data
            }));
        } else {
            setState(prev => ({
                ...prev,
                connectionError: data.message
            }));
        }
    }, []);

    // Initialize WebSocket connection
    useEffect(() => {
        if (!sessionId) {
            navigate('/matches');
            return;
        }

        const initializeConnection = async () => {
            // Reset error state before attempting connection
            setState(prev => ({
                ...prev,
                connectionError: undefined,
                isLoading: true
            }));

            try {
                // Get auth token from Redux store
                if (!token) {
                    setState(prev => ({
                        ...prev,
                        connectionError: 'Authentication required. Please log in.',
                        isLoading: false
                    }));
                    navigate('/auth');
                    return;
                }

                // Set up event listeners
                websocketService.on('connection_established', handleConnectionEstablished);
                websocketService.on('ai_message', handleAIMessage);
                websocketService.on('compatibility_update', handleCompatibilityUpdate);
                websocketService.on('user_joined', handleUserJoined);
                websocketService.on('user_left', handleUserLeft);
                websocketService.on('user_reaction', handleUserReaction);
                websocketService.on('session_status_change', handleSessionStatusChange);
                websocketService.on('gemini_quota_exceeded', handleError);
                websocketService.on('error', handleError);

                // Connect to session
                const connected = await websocketService.connectToSession(sessionId, token);

                if (!connected) {
                    setState(prev => ({
                        ...prev,
                        connectionError: 'Failed to connect to session',
                        isLoading: false
                    }));
                }

                // Start heartbeat
                websocketService.startHeartbeat();

            } catch (error) {
                console.error('Failed to initialize WebSocket connection:', error);
                setState(prev => ({
                    ...prev,
                    connectionError: 'Connection failed',
                    isLoading: false
                }));
            }
        };

        initializeConnection();

        // Cleanup on unmount
        return () => {
            websocketService.off('connection_established', handleConnectionEstablished);
            websocketService.off('ai_message', handleAIMessage);
            websocketService.off('compatibility_update', handleCompatibilityUpdate);
            websocketService.off('user_joined', handleUserJoined);
            websocketService.off('user_left', handleUserLeft);
            websocketService.off('user_reaction', handleUserReaction);
            websocketService.off('session_status_change', handleSessionStatusChange);
            websocketService.off('gemini_quota_exceeded', handleError);
            websocketService.off('error', handleError);
            websocketService.disconnect();
        };
    }, [sessionId, navigate, handleConnectionEstablished, handleAIMessage, handleCompatibilityUpdate, handleUserJoined, handleUserLeft, handleUserReaction, handleSessionStatusChange, handleError]);

    // Theater actions
    const startConversation = useCallback(() => {
        websocketService.startConversation();
    }, []);

    const sendReaction = useCallback((messageId: string, reactionType: string) => {
        websocketService.sendReaction(messageId, reactionType);
    }, []);

    const sendGuidance = useCallback(() => {
        if (guidanceText.trim() && selectedAvatar) {
            websocketService.sendGuidance(selectedAvatar, guidanceText);
            setGuidanceText('');
            setShowGuidanceDialog(false);
        }
    }, [guidanceText, selectedAvatar]);

    const toggleCompatibilityPanel = useCallback(() => {
        setState(prev => ({
            ...prev,
            showCompatibilityPanel: !prev.showCompatibilityPanel
        }));
    }, []);

    const toggleViewersPanel = useCallback(() => {
        setState(prev => ({
            ...prev,
            showViewersPanel: !prev.showViewersPanel
        }));
    }, []);

    const toggleFullscreen = useCallback(() => {
        if (!isFullscreen) {
            theaterRef.current?.requestFullscreen?.();
        } else {
            document.exitFullscreen?.();
        }
        setIsFullscreen(!isFullscreen);
    }, [isFullscreen]);

    const playNotificationSound = useCallback(() => {
        if (soundEnabled) {
            // Create a simple notification sound
            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 800;
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        }
    }, [soundEnabled]);

    // Loading state
    if (state.isLoading) {
        return (
            <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                minHeight="400px"
                gap={2}
            >
                <LinearProgress sx={{ width: '200px' }} />
                <Typography variant="h6">Connecting to AI Theater...</Typography>
                <Typography variant="body2" color="text.secondary">
                    Preparing your live matching session
                </Typography>
            </Box>
        );
    }

    // Error state
    if (state.connectionError) {
        return (
            <Alert severity="error" sx={{ m: 2 }}>
                <Typography variant="h6">Connection Error</Typography>
                <Typography>{state.connectionError}</Typography>
                <Button onClick={() => window.location.reload()} sx={{ mt: 1 }}>
                    Retry Connection
                </Button>
            </Alert>
        );
    }

    // Handle Gemini quota exceeded dialog
    const handleCloseQuotaDialog = () => {
        setState(prev => ({ ...prev, showQuotaExceededDialog: false }));
        // Redirect to matches page when closing without going to settings
        navigate('/matches');
    };

    const handleGoToSettings = () => {
        navigate('/settings');
    };

    return (
        <Box
            ref={theaterRef}
            sx={{
                height: isFullscreen ? '100vh' : '80vh',
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.default',
                position: 'relative',
                overflow: 'hidden'
            }}
        >
            {/* Gemini Quota Exceeded Dialog */}
            <Dialog
                open={state.showQuotaExceededDialog}
                onClose={handleCloseQuotaDialog}
                maxWidth="sm"
                fullWidth
                disableEscapeKeyDown
            >
                <DialogTitle>
                    <Box display="flex" alignItems="center" gap={1}>
                        <Warning color="warning" />
                        <Typography variant="h6">API Quota Limit Reached</Typography>
                    </Box>
                </DialogTitle>
                <DialogContent>
                    <Typography variant="body1" paragraph>
                        The system's Gemini API Key has reached its daily usage limit.
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                        To continue using AI conversation features, we recommend configuring your own Gemini API Key.
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Click "Go to Settings" to configure your API Key, or "Close" to return to the matches page.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseQuotaDialog} variant="outlined">
                        Close
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handleGoToSettings}
                        startIcon={<Send />}
                        autoFocus
                    >
                        Go to Settings
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Main Theater Content */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                {/* Theater Header */}
                <Paper
                    elevation={2}
                    sx={{
                        p: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        borderRadius: isFullscreen ? 0 : 1
                    }}
                >
                    <Box display="flex" alignItems="center" gap={2}>
                        <Typography variant="h5" component="h1">
                            Live AI Theater
                        </Typography>
                        <Chip
                            label={state.session?.status || 'Unknown'}
                            color={state.session?.status === 'active' ? 'success' : 'default'}
                            size="small"
                        />
                        <Badge badgeContent={state.viewers.length} color="primary">
                            <People />
                        </Badge>
                    </Box>

                    <Box display="flex" alignItems="center" gap={1}>
                        <Tooltip title="Compatibility Metrics">
                            <IconButton onClick={toggleCompatibilityPanel}>
                                <Assessment />
                            </IconButton>
                        </Tooltip>

                        <Tooltip title="Viewers">
                            <IconButton onClick={toggleViewersPanel}>
                                <Badge badgeContent={state.viewers.length} color="primary">
                                    <People />
                                </Badge>
                            </IconButton>
                        </Tooltip>

                        <Tooltip title={soundEnabled ? "Mute Sounds" : "Enable Sounds"}>
                            <IconButton onClick={() => setSoundEnabled(!soundEnabled)}>
                                {soundEnabled ? <VolumeUp /> : <VolumeOff />}
                            </IconButton>
                        </Tooltip>

                        <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
                            <IconButton onClick={toggleFullscreen}>
                                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
                            </IconButton>
                        </Tooltip>

                        <Tooltip title="Close Theater">
                            <IconButton onClick={() => navigate('/matches')}>
                                <Close />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Paper>

                {/* Main Theater Content */}
                <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                    {/* Conversation Area */}
                    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                        {/* Avatar Display */}
                        <AvatarDisplay
                            session={state.session}
                            compatibility={state.compatibility}
                        />

                        {/* Conversation Display */}
                        <Box sx={{ flex: 1, overflow: 'hidden' }}>
                            <ConversationDisplay
                                messages={state.messages}
                                userReactions={state.userReactions}
                                onReaction={sendReaction}
                                selectedMessage={state.selectedMessage}
                            />
                            <div ref={messagesEndRef} />
                        </Box>

                        {/* User Controls */}
                        <UserControls
                            session={state.session}
                            onStartConversation={startConversation}
                            onSendGuidance={() => setShowGuidanceDialog(true)}
                            onRequestUpdate={() => websocketService.requestCompatibilityUpdate()}
                            isConnected={state.isConnected}
                        />
                    </Box>

                    {/* Side Panels */}
                    <Drawer
                        anchor="right"
                        open={state.showCompatibilityPanel}
                        onClose={toggleCompatibilityPanel}
                        variant="temporary"
                        sx={{
                            '& .MuiDrawer-paper': {
                                width: 400,
                                position: 'relative',
                                height: '100%'
                            }
                        }}
                    >
                        <CompatibilityPanel
                            compatibility={state.compatibility}
                            session={state.session}
                            onClose={toggleCompatibilityPanel}
                        />
                    </Drawer>

                    <Drawer
                        anchor="right"
                        open={state.showViewersPanel}
                        onClose={toggleViewersPanel}
                        variant="temporary"
                        sx={{
                            '& .MuiDrawer-paper': {
                                width: 300,
                                position: 'relative',
                                height: '100%'
                            }
                        }}
                    >
                        <ViewersPanel
                            viewers={state.viewers}
                            onClose={toggleViewersPanel}
                        />
                    </Drawer>
                </Box>

                {/* Guidance Dialog */}
                <Dialog
                    open={showGuidanceDialog}
                    onClose={() => setShowGuidanceDialog(false)}
                    maxWidth="sm"
                    fullWidth
                >
                    <DialogTitle>Send Guidance to Your Avatar</DialogTitle>
                    <DialogContent>
                        <FormControl fullWidth sx={{ mb: 2, mt: 1 }}>
                            <InputLabel>Select Avatar</InputLabel>
                            <Select
                                value={selectedAvatar}
                                onChange={(e) => setSelectedAvatar(e.target.value)}
                                label="Select Avatar"
                            >
                                <MenuItem value="user_avatar_1">Your Avatar</MenuItem>
                                <MenuItem value="user_avatar_2">Match's Avatar</MenuItem>
                            </Select>
                        </FormControl>

                        <TextField
                            fullWidth
                            multiline
                            rows={3}
                            label="Guidance Message"
                            value={guidanceText}
                            onChange={(e) => setGuidanceText(e.target.value)}
                            placeholder="Provide guidance to your avatar about how to respond..."
                            helperText="Your avatar will receive this guidance for the next response"
                        />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setShowGuidanceDialog(false)}>
                            Cancel
                        </Button>
                        <Button
                            onClick={sendGuidance}
                            variant="contained"
                            disabled={!guidanceText.trim() || !selectedAvatar}
                            startIcon={<Send />}
                        >
                            Send Guidance
                        </Button>
                    </DialogActions>
                </Dialog>

                {/* Connection Status Indicator */}
                <AnimatePresence>
                    {!state.isConnected && (
                        <motion.div
                            initial={{ opacity: 0, y: 50 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 50 }}
                            style={{
                                position: 'absolute',
                                bottom: 16,
                                left: 16,
                                zIndex: 1000
                            }}
                        >
                            <Alert severity="warning" variant="filled">
                                Connection lost. Attempting to reconnect...
                            </Alert>
                        </motion.div>
                    )}
                </AnimatePresence>
            </Box>
        </Box>
    );
};

export default LiveMatchingTheater;