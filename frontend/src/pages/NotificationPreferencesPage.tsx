import React from 'react';
import { Container, Box } from '@mui/material';
import NotificationPreferences from '../components/notifications/NotificationPreferences';

const NotificationPreferencesPage: React.FC = () => {
    return (
        <Container maxWidth="md">
            <Box py={4}>
                <NotificationPreferences />
            </Box>
        </Container>
    );
};

export default NotificationPreferencesPage;
