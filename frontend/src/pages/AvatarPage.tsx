/**
 * Avatar Management Page
 */
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Container,
    Box,
    Typography,
    Breadcrumbs,
    Link,
    Alert
} from '@mui/material';
import {
    Home as HomeIcon,
    Psychology as PsychologyIcon
} from '@mui/icons-material';
import { useSelector } from 'react-redux';

import { RootState } from '../store/store';
import AvatarManager from '../components/avatar/AvatarManager';
import { AIAvatar } from '../types/avatar';

const AvatarPage: React.FC = () => {
    const user = useSelector((state: RootState) => state.auth.user);
    const { t } = useTranslation();
    const [currentAvatar, setCurrentAvatar] = useState<AIAvatar | null>(null);

    const handleAvatarUpdate = (avatar: AIAvatar) => {
        setCurrentAvatar(avatar);
    };

    if (!user) {
        return (
            <Container maxWidth="lg">
                <Alert severity="error">
                    Please log in to manage your AI avatar.
                </Alert>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg">
            <Box py={3}>
                {/* Breadcrumbs */}
                <Breadcrumbs sx={{ mb: 2 }}>
                    <Link
                        color="inherit"
                        href="/dashboard"
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                    >
                        <HomeIcon fontSize="small" />
                        Dashboard
                    </Link>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <PsychologyIcon fontSize="small" />
                        AI Avatar
                    </Box>
                </Breadcrumbs>

                {/* Page Header */}
                <Box mb={4}>
                    <Typography variant="h4" component="h1" gutterBottom>
                        AI Avatar Management
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Create and customize your AI avatar that represents your personality in conversations and matchmaking.
                        Your avatar learns from your personality assessment and can be fine-tuned to better reflect who you are.
                    </Typography>
                </Box>

                {/* Avatar Manager */}
                <AvatarManager
                    userId={user.id}
                    onAvatarUpdate={handleAvatarUpdate}
                />
            </Box>
        </Container>
    );
};

export default AvatarPage;