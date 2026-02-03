/**
 * Live Matching Theater Page - Full page wrapper for the theater interface
 */
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Container, Button } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';

import LiveMatchingTheater from '../components/matching/LiveMatchingTheater';
import { useAppSelector } from '../hooks/redux';

const LiveMatchingTheaterPage: React.FC = () => {
    const { sessionId } = useParams<{ sessionId: string }>();
    const navigate = useNavigate();
    const { user } = useAppSelector(state => state.auth);
    const isAuthenticated = !!user;

    useEffect(() => {
        // Redirect if not authenticated
        if (!isAuthenticated) {
            navigate('/auth');
            return;
        }

        // Validate session ID
        if (!sessionId) {
            navigate('/matches');
            return;
        }
    }, [isAuthenticated, sessionId, navigate]);

    const handleSessionEnd = () => {
        navigate('/matches');
    };

    const handleBackToMatches = () => {
        navigate('/matches');
    };

    if (!isAuthenticated || !sessionId) {
        return null; // Will redirect
    }

    return (
        <Box
            sx={{
                minHeight: '100vh',
                bgcolor: 'background.default',
                display: 'flex',
                flexDirection: 'column'
            }}
        >
            {/* Header with back button */}
            <Box
                sx={{
                    p: 2,
                    borderBottom: 1,
                    borderColor: 'divider',
                    bgcolor: 'background.paper'
                }}
            >
                <Container maxWidth="xl">
                    <Button
                        startIcon={<ArrowBack />}
                        onClick={handleBackToMatches}
                        variant="outlined"
                        size="small"
                    >
                        Back to Matches
                    </Button>
                </Container>
            </Box>

            {/* Theater Content */}
            <Box sx={{ flex: 1 }}>
                <Container maxWidth="xl" sx={{ height: '100%', py: 2 }}>
                    <LiveMatchingTheater
                        sessionId={sessionId}
                        onSessionEnd={handleSessionEnd}
                    />
                </Container>
            </Box>
        </Box>
    );
};

export default LiveMatchingTheaterPage;