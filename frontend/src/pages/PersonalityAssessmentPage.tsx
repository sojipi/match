/**
 * Personality Assessment Page
 * Handles the complete personality assessment flow
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Container, Typography, Alert, Button } from '@mui/material';
import { useAppSelector } from '../hooks/redux';
import PersonalityAssessment from '../components/personality/PersonalityAssessment';
import PersonalityVisualization from '../components/personality/PersonalityVisualization';
import { PersonalityProfile, AssessmentProgress } from '../types/personality';

const PersonalityAssessmentPage: React.FC = () => {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const { user } = useAppSelector(state => state.auth);
    const [isCompleted, setIsCompleted] = useState(false);
    const [completedProfile, setCompletedProfile] = useState<PersonalityProfile | null>(null);
    const [currentProgress, setCurrentProgress] = useState<AssessmentProgress | null>(null);

    const handleAssessmentComplete = (profile: PersonalityProfile) => {
        setCompletedProfile(profile);
        setIsCompleted(true);
    };

    const handleProgressUpdate = (progress: AssessmentProgress) => {
        setCurrentProgress(progress);
    };

    const handleContinueToDashboard = () => {
        navigate('/dashboard');
    };

    const handleRetakeAssessment = () => {
        setIsCompleted(false);
        setCompletedProfile(null);
    };

    if (!user) {
        return (
            <Container maxWidth="md" sx={{ py: 4 }}>
                <Alert severity="error">
                    {t('personality.page.loginRequired')}
                    <Button onClick={() => navigate('/auth')} sx={{ ml: 2 }}>
                        {t('personality.page.login')}
                    </Button>
                </Alert>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            {/* Header */}
            <Box textAlign="center" mb={4}>
                <Typography variant="h3" component="h1" gutterBottom>
                    {t('personality.page.title')}
                </Typography>
                <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
                    {isCompleted
                        ? t('personality.page.subtitleComplete')
                        : t('personality.page.subtitle')
                    }
                </Typography>
            </Box>

            {isCompleted && completedProfile ? (
                /* Assessment Complete - Show Results */
                <Box>
                    <Alert severity="success" sx={{ mb: 3 }}>
                        {t('personality.page.congratulations')}
                    </Alert>

                    <PersonalityVisualization
                        profile={completedProfile}
                        showDetails={true}
                    />

                    <Box display="flex" justifyContent="center" gap={2} mt={4}>
                        <Button
                            variant="contained"
                            size="large"
                            onClick={handleContinueToDashboard}
                        >
                            {t('personality.page.continueToDashboard')}
                        </Button>
                        <Button
                            variant="outlined"
                            size="large"
                            onClick={handleRetakeAssessment}
                        >
                            {t('personality.retakeAssessment')}
                        </Button>
                    </Box>

                    {/* Next Steps */}
                    <Box sx={{ mt: 4, p: 3, bgcolor: 'primary.50', borderRadius: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            {t('personality.page.whatsNext.title')}
                        </Typography>
                        <Typography variant="body1" paragraph>
                            {t('personality.page.whatsNext.intro')}
                        </Typography>
                        <ul>
                            <li>
                                <Typography variant="body2">
                                    {t('personality.page.whatsNext.discoverMatches')}
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    {t('personality.page.whatsNext.watchConversations')}
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    {t('personality.page.whatsNext.getReports')}
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    {t('personality.page.whatsNext.refineProfile')}
                                </Typography>
                            </li>
                        </ul>
                    </Box>
                </Box>
            ) : (
                /* Assessment In Progress */
                <Box>
                    {currentProgress && currentProgress.completion_percentage > 0 && (
                        <Alert severity="info" sx={{ mb: 3 }}>
                            {t('personality.page.progressMessage', { percent: Math.round(currentProgress.completion_percentage) })}
                            {currentProgress.insights.length > 0 &&
                                ` ${t('personality.page.insightsDiscovered', { count: currentProgress.insights.length })}`
                            }
                        </Alert>
                    )}

                    <PersonalityAssessment
                        userId={user.id}
                        onComplete={handleAssessmentComplete}
                        onProgress={handleProgressUpdate}
                    />

                    {/* Help Section */}
                    <Box sx={{ mt: 4, p: 3, bgcolor: 'grey.50', borderRadius: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            {t('personality.page.tips.title')}
                        </Typography>
                        <ul>
                            <li>
                                <Typography variant="body2">
                                    {t('personality.page.tips.honest')}
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    {t('personality.page.tips.takeTime')}
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    {t('personality.page.tips.confidence')}
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    {t('personality.page.tips.insights')}
                                </Typography>
                            </li>
                        </ul>
                    </Box>
                </Box>
            )}
        </Container>
    );
};

export default PersonalityAssessmentPage;