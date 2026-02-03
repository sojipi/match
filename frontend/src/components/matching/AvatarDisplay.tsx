/**
 * Avatar Display - Shows AI avatars with animations and status
 */
import React from 'react';
import {
    Box,
    Paper,
    Typography,
    Avatar,
    Chip,
    LinearProgress,
    Tooltip,
    Badge
} from '@mui/material';
import {
    Psychology,
    Favorite,
    TrendingUp,
    TrendingDown,
    TrendingFlat,
    Circle
} from '@mui/icons-material';
import { motion } from 'framer-motion';

import { MatchSession, CompatibilityMetrics } from '../../types/matching';

interface AvatarDisplayProps {
    session?: MatchSession;
    compatibility: CompatibilityMetrics;
}

const AvatarDisplay: React.FC<AvatarDisplayProps> = ({
    session,
    compatibility
}) => {
    const getCompatibilityColor = (score: number): string => {
        if (score >= 0.8) return '#4CAF50';
        if (score >= 0.6) return '#FF9800';
        return '#F44336';
    };

    const getTrendIcon = () => {
        if (compatibility.trend_data.length < 2) return <TrendingFlat />;

        const recent = compatibility.trend_data.slice(-2);
        const trend = recent[1].score - recent[0].score;

        if (trend > 0.02) return <TrendingUp sx={{ color: 'success.main' }} />;
        if (trend < -0.02) return <TrendingDown sx={{ color: 'error.main' }} />;
        return <TrendingFlat sx={{ color: 'text.secondary' }} />;
    };

    const AvatarCard: React.FC<{
        name: string;
        isLeft: boolean;
        isActive: boolean;
    }> = ({ name, isLeft, isActive }) => {
        const avatarColor = name.includes('Alex') ? '#1976d2' : '#d32f2f';

        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: isLeft ? 0 : 0.2 }}
            >
                <Paper
                    elevation={isActive ? 8 : 2}
                    sx={{
                        p: 3,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 2,
                        minWidth: 200,
                        border: isActive ? `2px solid ${avatarColor}` : 'none',
                        borderRadius: 3,
                        background: isActive
                            ? `linear-gradient(135deg, ${avatarColor}10, transparent)`
                            : 'background.paper'
                    }}
                >
                    {/* Avatar with Status */}
                    <Badge
                        overlap="circular"
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        badgeContent={
                            <Circle
                                sx={{
                                    color: isActive ? 'success.main' : 'text.disabled',
                                    fontSize: 16
                                }}
                            />
                        }
                    >
                        <motion.div
                            animate={isActive ? {
                                scale: [1, 1.05, 1],
                                rotate: [0, 2, -2, 0]
                            } : {}}
                            transition={{
                                duration: 2,
                                repeat: isActive ? Infinity : 0,
                                repeatType: "reverse"
                            }}
                        >
                            <Avatar
                                sx={{
                                    width: 80,
                                    height: 80,
                                    bgcolor: avatarColor,
                                    fontSize: '2rem',
                                    fontWeight: 'bold',
                                    border: `4px solid ${isActive ? avatarColor : 'transparent'}`,
                                    boxShadow: isActive ? `0 0 20px ${avatarColor}40` : 'none'
                                }}
                            >
                                {name.charAt(0)}
                            </Avatar>
                        </motion.div>
                    </Badge>

                    {/* Avatar Name */}
                    <Typography variant="h6" textAlign="center">
                        {name}
                    </Typography>

                    {/* Status Chip */}
                    <Chip
                        icon={<Psychology />}
                        label={isActive ? "Conversing" : "Waiting"}
                        color={isActive ? "primary" : "default"}
                        size="small"
                    />

                    {/* Personality Traits Preview */}
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', justifyContent: 'center' }}>
                        {/* Mock personality traits - in real app, get from avatar data */}
                        {name.includes('Alex') ? (
                            <>
                                <Chip label="Adventurous" size="small" variant="outlined" />
                                <Chip label="Outgoing" size="small" variant="outlined" />
                                <Chip label="Creative" size="small" variant="outlined" />
                            </>
                        ) : (
                            <>
                                <Chip label="Thoughtful" size="small" variant="outlined" />
                                <Chip label="Caring" size="small" variant="outlined" />
                                <Chip label="Artistic" size="small" variant="outlined" />
                            </>
                        )}
                    </Box>
                </Paper>
            </motion.div>
        );
    };

    return (
        <Box
            sx={{
                p: 3,
                bgcolor: 'background.default',
                borderBottom: 1,
                borderColor: 'divider'
            }}
        >
            {/* Theater Stage */}
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 4,
                    mb: 3
                }}
            >
                {/* Left Avatar */}
                <AvatarCard
                    name="Alex's Avatar"
                    isLeft={true}
                    isActive={session?.status === 'active'}
                />

                {/* Center - Compatibility Display */}
                <Box
                    sx={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 2
                    }}
                >
                    {/* Compatibility Score */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.4 }}
                    >
                        <Paper
                            elevation={4}
                            sx={{
                                p: 2,
                                borderRadius: 3,
                                background: `linear-gradient(135deg, ${getCompatibilityColor(compatibility.overall_score)}20, transparent)`,
                                border: `2px solid ${getCompatibilityColor(compatibility.overall_score)}40`
                            }}
                        >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Favorite sx={{ color: getCompatibilityColor(compatibility.overall_score) }} />
                                <Box>
                                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: getCompatibilityColor(compatibility.overall_score) }}>
                                        {Math.round(compatibility.overall_score * 100)}%
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        Compatibility
                                    </Typography>
                                </Box>
                                {getTrendIcon()}
                            </Box>
                        </Paper>
                    </motion.div>

                    {/* Connection Animation */}
                    {session?.status === 'active' && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ duration: 0.5, delay: 0.6 }}
                            style={{ width: '100%' }}
                        >
                            <Box
                                sx={{
                                    position: 'relative',
                                    height: 4,
                                    bgcolor: 'divider',
                                    borderRadius: 2,
                                    overflow: 'hidden'
                                }}
                            >
                                <motion.div
                                    animate={{
                                        x: ['-100%', '100%']
                                    }}
                                    transition={{
                                        duration: 2,
                                        repeat: Infinity,
                                        ease: "linear"
                                    }}
                                    style={{
                                        position: 'absolute',
                                        top: 0,
                                        left: 0,
                                        width: '30%',
                                        height: '100%',
                                        background: `linear-gradient(90deg, transparent, ${getCompatibilityColor(compatibility.overall_score)}, transparent)`,
                                        borderRadius: 2
                                    }}
                                />
                            </Box>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 1 }}>
                                AI Conversation in Progress
                            </Typography>
                        </motion.div>
                    )}

                    {/* Dimension Scores */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.8 }}
                    >
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
                            {Object.entries(compatibility.dimension_scores).map(([dimension, score]) => (
                                <Tooltip key={dimension} title={`${dimension}: ${Math.round(score * 100)}%`}>
                                    <Chip
                                        label={`${dimension.charAt(0).toUpperCase()}${dimension.slice(1)}: ${Math.round(score * 100)}%`}
                                        size="small"
                                        sx={{
                                            bgcolor: `${getCompatibilityColor(score)}20`,
                                            color: getCompatibilityColor(score),
                                            border: `1px solid ${getCompatibilityColor(score)}40`
                                        }}
                                    />
                                </Tooltip>
                            ))}
                        </Box>
                    </motion.div>
                </Box>

                {/* Right Avatar */}
                <AvatarCard
                    name="Sarah's Avatar"
                    isLeft={false}
                    isActive={session?.status === 'active'}
                />
            </Box>

            {/* Session Status Bar */}
            {session && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 1 }}
                >
                    <Paper
                        elevation={1}
                        sx={{
                            p: 2,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            bgcolor: 'background.paper',
                            borderRadius: 2
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Chip
                                label={session.status}
                                color={session.status === 'active' ? 'success' : 'default'}
                                size="small"
                            />
                            <Typography variant="body2" color="text.secondary">
                                Session Type: {session.session_type}
                            </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                                Viewers: {session.viewer_count}
                            </Typography>
                            {session.status === 'active' && (
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Circle sx={{ color: 'success.main', fontSize: 8 }} />
                                    <Typography variant="body2" color="success.main">
                                        Live
                                    </Typography>
                                </Box>
                            )}
                        </Box>
                    </Paper>
                </motion.div>
            )}
        </Box>
    );
};

export default AvatarDisplay;