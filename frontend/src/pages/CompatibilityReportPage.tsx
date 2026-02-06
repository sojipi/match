/**
 * Compatibility Report Page - Display detailed compatibility analysis
 */
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Box, IconButton, Tooltip } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import CompatibilityReport from '../components/compatibility/CompatibilityReport';

const CompatibilityReportPage: React.FC = () => {
    const { reportId } = useParams<{ reportId: string }>();
    const navigate = useNavigate();

    if (!reportId) {
        return (
            <Container maxWidth="lg" sx={{ py: 4 }}>
                <Box textAlign="center">
                    <p>Invalid report ID</p>
                </Box>
            </Container>
        );
    }

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 3 }}>
            <Container maxWidth="lg">
                <Box sx={{ mb: 2 }}>
                    <Tooltip title="Back to Matches">
                        <IconButton onClick={() => navigate('/matches')}>
                            <ArrowBack />
                        </IconButton>
                    </Tooltip>
                </Box>

                <CompatibilityReport
                    matchUserId={reportId}
                    onClose={() => navigate('/matches')}
                />
            </Container>
        </Box>
    );
};

export default CompatibilityReportPage;
