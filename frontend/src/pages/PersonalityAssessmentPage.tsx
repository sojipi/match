/**
 * Personality Assessment Page
 * Handles the complete personality assessment flow
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Container, Typography, Alert, Button } from '@mui/material';
import { useAppSelector } from '../hooks/redux';
import PersonalityAssessment from '../components/personality/PersonalityAssessment';
import PersonalityVisualization from '../components/personality/PersonalityVisualization';
import { PersonalityProfile, AssessmentProgress } from '../types/personality';

const PersonalityAssessmentPage: React.FC = () => {
    const navigate = useNavigate();
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
                    You must be logged in to take the personality assessment.
                    <Button onClick={() => navigate('/auth')} sx={{ ml: 2 }}>
                        Login
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
                    Personality Assessment
                </Typography>
                <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
                    {isCompleted
                        ? "Your personality profile is complete! Review your results below."
                        : "Help us understand your unique personality to find your perfect matches. This assessment takes about 10-15 minutes."
                    }
                </Typography>
            </Box>

            {isCompleted && completedProfile ? (
                /* Assessment Complete - Show Results */
                <Box>
                    <Alert severity="success" sx={{ mb: 3 }}>
                        🎉 Congratulations! Your personality assessment is complete.
                        Your AI avatar is now ready to represent you in matchmaking sessions.
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
                            Continue to Dashboard
                        </Button>
                        <Button
                            variant="outlined"
                            size="large"
                            onClick={handleRetakeAssessment}
                        >
                            Retake Assessment
                        </Button>
                    </Box>

                    {/* Next Steps */}
                    <Box sx={{ mt: 4, p: 3, bgcolor: 'primary.50', borderRadius: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            What's Next?
                        </Typography>
                        <Typography variant="body1" paragraph>
                            Now that your personality profile is complete, you can:
                        </Typography>
                        <ul>
                            <li>
                                <Typography variant="body2">
                                    <strong>Discover Matches:</strong> Browse potential partners based on personality compatibility
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    <strong>Watch AI Conversations:</strong> See your AI avatar interact with potential matches
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    <strong>Get Compatibility Reports:</strong> Receive detailed analysis of your relationship potential
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    <strong>Refine Your Profile:</strong> Update your assessment anytime to improve matches
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
                            You're {Math.round(currentProgress.completion_percentage)}% complete!
                            {currentProgress.insights.length > 0 &&
                                ` We've already discovered ${currentProgress.insights.length} personality insights about you.`
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
                            Assessment Tips
                        </Typography>
                        <ul>
                            <li>
                                <Typography variant="body2">
                                    Answer honestly - there are no right or wrong answers
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    Take your time - you can pause and resume anytime
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    Use the confidence slider to indicate how sure you are
                                </Typography>
                            </li>
                            <li>
                                <Typography variant="body2">
                                    Watch for real-time insights as you progress
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