/**
 * User Controls - Interactive controls for the live matching theater
 */
import React, { useState } from 'react';
import {
    Box,
    Paper,
    Button,
    IconButton,
    Tooltip,
    Chip,
    Typography,
    Fab,
    SpeedDial,
    SpeedDialAction,
    SpeedDialIcon,
    Alert
} from '@mui/material';
import {
    PlayArrow,
    Stop,
    Refresh,
    Psychology,
    Send,
    Assessment,
    Feedback,
    Help,
    Settings
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

import { MatchSession } from '../../types/matching';

interface UserControlsProps {
    session?: MatchSession;
    onStartConversation: () => void;
    onSendGuidance: () => void;
    onRequestUpdate: () => void;
    isConnected: boolean;
}

const UserControls: React.FC<UserControlsProps> = ({
    session,
    onStartConversation,
    onSendGuidance,
    onRequestUpdate,
    isConnected
}) => {
    const [speedDialOpen, setSpeedDialOpen] = useState(false);
    const [showHelp, setShowHelp] = useState(false);

    const canStartConversation = session?.status === 'waiting' && isConnected;
    const canSendGuidance = session?.status === 'active' && isConnected;
    const canRequestUpdate = isConnected;

    const speedDialActions = [
        {
            icon: <Psychology />,
            name: 'Send Guidance',
            onClick: onSendGuidance,
            disabled: !canSendGuidance,
            tooltip: 'Guide your AI avatar during the conversation'
        },
        {
            icon: <Assessment />,
            name: 'Request Update',
            onClick: onRequestUpdate,
            disabled: !canRequestUpdate,
            tooltip: 'Get latest compatibility metrics'
        },
        {
            icon: <Feedback />,
            name: 'Feedback',
            onClick: () => console.log('Feedback clicked'),
            disabled: false,
            tooltip: 'Provide feedback about the session'
        },
        {
            icon: <Help />,
            name: 'Help',
            onClick: () => setShowHelp(!showHelp),
            disabled: false,
            tooltip: 'Show help and tips'
        }
    ];

    return (
        <Box
            sx={{
                p: 2,
                bgcolor: 'background.paper',
                borderTop: 1,
                borderColor: 'divider'
            }}
        >
            {/* Connection Status */}
            <AnimatePresence>
                {!isConnected && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        style={{ marginBottom: 16 }}
                    >
                        <Alert severity="warning" variant="outlined">
                            Connection lost. Some controls may not work properly.
                        </Alert>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Help Panel */}
            <AnimatePresence>
                {showHelp && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        style={{ marginBottom: 16 }}
                    >
                        <Paper
                            elevation={1}
                            sx={{
                                p: 2,
                                bgcolor: 'info.light',
                                color: 'info.contrastText'
                            }}
                        >
                            <Typography variant="subtitle2" sx={{ mb: 1 }}>
                                How to Use the AI Theater
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                • <strong>Start Conversation:</strong> Begin the AI avatar interaction
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                • <strong>Send Guidance:</strong> Provide real-time guidance to your avatar
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                • <strong>React to Messages:</strong> Click the emoji button on messages to react
                            </Typography>
                            <Typography variant="body2">
                                • <strong>View Metrics:</strong> Check compatibility panel for detailed analysis
                            </Typography>
                        </Paper>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Main Controls */}
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 2
                }}
            >
                {/* Primary Action */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {session?.status === 'waiting' && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.3 }}
                        >
                            <Button
                                variant="contained"
                                size="large"
                                startIcon={<PlayArrow />}
                                onClick={onStartConversation}
                                disabled={!canStartConversation}
                                sx={{
                                    minWidth: 200,
                                    py: 1.5,
                                    fontSize: '1.1rem',
                                    background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
                                    '&:hover': {
                                        background: 'linear-gradient(45deg, #1565c0, #1976d2)'
                                    }
                                }}
                            >
                                Start AI Conversation
                            </Button>
                        </motion.div>
                    )}

                    {session?.status === 'active' && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.3 }}
                        >
                            <Chip
                                icon={<Psychology />}
                                label="AI Conversation Active"
                                color="success"
                                variant="outlined"
                                sx={{ py: 2, px: 1, fontSize: '1rem' }}
                            />
                        </motion.div>
                    )}

                    {session?.status === 'completed' && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.3 }}
                        >
                            <Chip
                                label="Session Completed"
                                color="default"
                                sx={{ py: 2, px: 1, fontSize: '1rem' }}
                            />
                        </motion.div>
                    )}
                </Box>

                {/* Session Info */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {session && (
                        <>
                            <Chip
                                label={`Type: ${session.session_type}`}
                                size="small"
                                variant="outlined"
                            />
                            <Chip
                                label={`Viewers: ${session.viewer_count}`}
                                size="small"
                                variant="outlined"
                            />
                        </>
                    )}
                </Box>

                {/* Quick Actions */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Tooltip title="Refresh compatibility metrics">
                        <IconButton
                            onClick={onRequestUpdate}
                            disabled={!canRequestUpdate}
                            color="primary"
                        >
                            <Refresh />
                        </IconButton>
                    </Tooltip>

                    {canSendGuidance && (
                        <Tooltip title="Send guidance to your avatar">
                            <IconButton
                                onClick={onSendGuidance}
                                color="secondary"
                                sx={{
                                    animation: 'pulse 2s infinite',
                                    '@keyframes pulse': {
                                        '0%': { boxShadow: '0 0 0 0 rgba(156, 39, 176, 0.7)' },
                                        '70%': { boxShadow: '0 0 0 10px rgba(156, 39, 176, 0)' },
                                        '100%': { boxShadow: '0 0 0 0 rgba(156, 39, 176, 0)' }
                                    }
                                }}
                            >
                                <Send />
                            </IconButton>
                        </Tooltip>
                    )}
                </Box>
            </Box>

            {/* Speed Dial for Additional Actions */}
            <SpeedDial
                ariaLabel="Theater controls"
                sx={{
                    position: 'fixed',
                    bottom: 24,
                    right: 24,
                    zIndex: 1000
                }}
                icon={<SpeedDialIcon />}
                open={speedDialOpen}
                onOpen={() => setSpeedDialOpen(true)}
                onClose={() => setSpeedDialOpen(false)}
            >
                {speedDialActions.map((action) => (
                    <SpeedDialAction
                        key={action.name}
                        icon={action.icon}
                        tooltipTitle={action.tooltip}
                        onClick={() => {
                            action.onClick();
                            setSpeedDialOpen(false);
                        }}
                        sx={{
                            opacity: action.disabled ? 0.5 : 1,
                            pointerEvents: action.disabled ? 'none' : 'auto'
                        }}
                    />
                ))}
            </SpeedDial>

            {/* Status Indicators */}
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    gap: 2,
                    mt: 2,
                    pt: 2,
                    borderTop: 1,
                    borderColor: 'divider'
                }}
            >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Box
                        sx={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            bgcolor: isConnected ? 'success.main' : 'error.main'
                        }}
                    />
                    <Typography variant="caption" color="text.secondary">
                        {isConnected ? 'Connected' : 'Disconnected'}
                    </Typography>
                </Box>

                {session && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box
                            sx={{
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                bgcolor: session.status === 'active' ? 'success.main' : 'warning.main'
                            }}
                        />
                        <Typography variant="caption" color="text.secondary">
                            Session {session.status}
                        </Typography>
                    </Box>
                )}
            </Box>
        </Box>
    );
};

export default UserControls;