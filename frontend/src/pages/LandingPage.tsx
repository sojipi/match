import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
    const navigate = useNavigate();

    return (
        <Container maxWidth="lg">
            <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                minHeight="100vh"
                textAlign="center"
            >
                <Typography variant="h1" component="h1" gutterBottom>
                    AI Matchmaker
                </Typography>
                <Typography variant="h5" component="h2" color="text.secondary" paragraph>
                    Discover meaningful connections through AI-powered personality matching
                </Typography>
                <Box mt={4}>
                    <Button
                        variant="contained"
                        size="large"
                        onClick={() => navigate('/auth/register')}
                        sx={{ mr: 2 }}
                    >
                        Get Started
                    </Button>
                    <Button
                        variant="outlined"
                        size="large"
                        onClick={() => navigate('/auth/login')}
                    >
                        Sign In
                    </Button>
                </Box>
            </Box>
        </Container>
    );
};

export default LandingPage;