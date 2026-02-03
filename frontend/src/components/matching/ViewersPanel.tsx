/**
 * Viewers Panel - Shows current session viewers
 */
import React from 'react';
import {
    Box,
    Typography,
    IconButton,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Avatar,
    Chip,
    Divider,
    Paper
} from '@mui/material';
import {
    Close,
    Person,
    Circle
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';

import { SessionViewer } from '../../types/matching';

interface ViewersPanelProps {
    viewers: SessionViewer[];
    onClose: () => void;
}

const ViewersPanel: React.FC<ViewersPanelProps> = ({
    viewers,
    onClose
}) => {
    const getAvatarColor = (userId: string): string => {
        // Generate consistent color based on user ID
        const colors = ['#1976d2', '#d32f2f', '#388e3c', '#f57c00', '#7b1fa2', '#0288d1'];
        const index = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
        return colors[index];
    };

    const getInitials = (name: string): string => {
        return name
            .split(' ')
            .map(word => word.charAt(0))
            .join('')
            .toUpperCase()
            .slice(0, 2);
    };

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
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h6" component="h2">
                        Viewers
                    </Typography>
                    <Chip
                        label={viewers.length}
                        size="small"
                        color="primary"
                    />
                </Box>
                <IconButton onClick={onClose} size="small">
                    <Close />
                </IconButton>
            </Box>

            {/* Content */}
            <Box sx={{ flex: 1, overflow: 'auto' }}>
                {viewers.length === 0 ? (
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '200px',
                            gap: 2,
                            color: 'text.secondary'
                        }}
                    >
                        <Person sx={{ fontSize: 48, opacity: 0.5 }} />
                        <Typography variant="body2" textAlign="center">
                            No viewers currently watching
                        </Typography>
                    </Box>
                ) : (
                    <List sx={{ p: 0 }}>
                        <AnimatePresence>
                            {viewers.map((viewer, index) => (
                                <motion.div
                                    key={viewer.user_id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    transition={{ duration: 0.3, delay: index * 0.1 }}
                                >
                                    <ListItem
                                        sx={{
                                            py: 2,
                                            '&:hover': {
                                                bgcolor: 'action.hover'
                                            }
                                        }}
                                    >
                                        <ListItemAvatar>
                                            <Avatar
                                                sx={{
                                                    bgcolor: getAvatarColor(viewer.user_id),
                                                    width: 40,
                                                    height: 40
                                                }}
                                            >
                                                {getInitials(viewer.user_name)}
                                            </Avatar>
                                        </ListItemAvatar>

                                        <ListItemText
                                            primary={
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Typography variant="body1">
                                                        {viewer.user_name}
                                                    </Typography>
                                                    <Circle sx={{ color: 'success.main', fontSize: 8 }} />
                                                </Box>
                                            }
                                            secondary={
                                                <Typography variant="caption" color="text.secondary">
                                                    Joined {formatDistanceToNow(new Date(viewer.connected_at), { addSuffix: true })}
                                                </Typography>
                                            }
                                        />
                                    </ListItem>

                                    {index < viewers.length - 1 && <Divider />}
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </List>
                )}

                {/* Viewer Stats */}
                {viewers.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                    >
                        <Paper
                            elevation={1}
                            sx={{
                                m: 2,
                                p: 2,
                                bgcolor: 'background.default'
                            }}
                        >
                            <Typography variant="subtitle2" sx={{ mb: 1 }}>
                                Session Stats
                            </Typography>

                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <Typography variant="body2" color="text.secondary">
                                        Total Viewers:
                                    </Typography>
                                    <Typography variant="body2">
                                        {viewers.length}
                                    </Typography>
                                </Box>

                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <Typography variant="body2" color="text.secondary">
                                        Most Recent:
                                    </Typography>
                                    <Typography variant="body2">
                                        {viewers.length > 0
                                            ? viewers.reduce((latest, viewer) =>
                                                new Date(viewer.connected_at) > new Date(latest.connected_at)
                                                    ? viewer
                                                    : latest
                                            ).user_name
                                            : 'None'
                                        }
                                    </Typography>
                                </Box>
                            </Box>
                        </Paper>
                    </motion.div>
                )}
            </Box>

            {/* Footer Info */}
            <Box
                sx={{
                    p: 2,
                    borderTop: 1,
                    borderColor: 'divider',
                    bgcolor: 'background.default'
                }}
            >
                <Typography variant="caption" color="text.secondary" textAlign="center" display="block">
                    Viewers can watch the AI conversation and see compatibility updates in real-time
                </Typography>
            </Box>
        </Box>
    );
};

export default ViewersPanel;