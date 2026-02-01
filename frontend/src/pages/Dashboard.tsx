import React from 'react';
import { Box, Typography } from '@mui/material';

const Dashboard: React.FC = () => {
    return (
        <Box p={3}>
            <Typography variant="h4" component="h1" gutterBottom>
                Dashboard
            </Typography>
            <Typography variant="body1">
                Welcome to your AI Matchmaker dashboard! This is where you'll manage your profile,
                view matches, and access AI-powered compatibility insights.
            </Typography>
        </Box>
    );
};

export default Dashboard;