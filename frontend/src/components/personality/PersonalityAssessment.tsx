/**
 * Interactive Personality Assessment Component
 */
import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    LinearProgress,
    Button,
    Chip,
    Stack,
    Alert
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { PersonalityQuestion, PersonalityAnswer, AssessmentProgress } from '../../types/personality';
import { personalityApi } from '../../services/personalityApi';
import QuestionCard from './QuestionCard';
import ProgressInsights from './ProgressInsights';

interface PersonalityAssessmentProps {
    userId: string;
    onComplete: (profile: any) => void;
    onProgress?: (progress: AssessmentProgress) => void;
}

const PersonalityAssessment: React.FC<PersonalityAssessmentProps> = ({
    userId,
    onComplete,
    onProgress
}) => {
    const [questions, setQuestions] = useState<PersonalityQuestion[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState<PersonalityAnswer[]>([]);
    const [progress, setProgress] = useState<AssessmentProgress | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showInsights, setShowInsights] = useState(false);

    // Load initial questions and progress
    useEffect(() => {
        loadAssessmentData();
    }, [userId]);

    // Update progress when answers change
    useEffect(() => {
        if (answers.length > 0) {
            updateProgress();
        }
    }, [answers]);

    const loadAssessmentData = async () => {
        try {
            setIsLoading(true);
            const [questionsData, progressData] = await Promise.all([
                personalityApi.getQuestions(),
                personalityApi.getProgress(userId)
            ]);

            setQuestions(questionsData);
            setProgress(progressData);

            // Start from where user left off
            setCurrentQuestionIndex(Math.min(progressData.current_step * 5, questionsData.length - 1));

            if (onProgress) {
                onProgress(progressData);
            }
        } catch (err) {
            setError('Failed to load assessment. Please try again.');
            console.error('Assessment loading error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const updateProgress = async () => {
        try {
            const progressData = await personalityApi.getProgress(userId);
            setProgress(progressData);

            if (onProgress) {
                onProgress(progressData);
            }
        } catch (err) {
            console.error('Progress update error:', err);
        }
    };

    const handleAnswer = (questionId: string, answer: any, confidence?: number) => {
        const newAnswer: PersonalityAnswer = {
            question_id: questionId,
            answer,
            confidence
        };

        setAnswers(prev => {
            const existing = prev.findIndex(a => a.question_id === questionId);
            if (existing >= 0) {
                const updated = [...prev];
                updated[existing] = newAnswer;
                return updated;
            }
            return [...prev, newAnswer];
        });
    };

    const handleNext = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
        } else {
            // Assessment complete
            handleSubmit();
        }
    };

    const handlePrevious = () => {
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(prev => prev - 1);
        }
    };

    const handleSubmit = async () => {
        try {
            setIsSubmitting(true);
            const profile = await personalityApi.submitAssessment(userId, {
                answers,
                assessment_version: '1.0'
            });

            onComplete(profile);
        } catch (err) {
            setError('Failed to submit assessment. Please try again.');
            console.error('Assessment submission error:', err);
        } finally {
            setIsSubmitting(false);
        }
    };

    const toggleInsights = () => {
        setShowInsights(!showInsights);
    };

    if (isLoading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <Box textAlign="center">
                    <LinearProgress sx={{ width: 200, mb: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                        Loading your personality assessment...
                    </Typography>
                </Box>
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" sx={{ mb: 2 }}>
                {error}
                <Button onClick={loadAssessmentData} sx={{ ml: 2 }}>
                    Retry
                </Button>
            </Alert>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];
    const isLastQuestion = currentQuestionIndex === questions.length - 1;
    const currentAnswer = answers.find(a => a.question_id === currentQuestion?.id);
    const canProceed = currentAnswer !== undefined;

    return (
        <Box maxWidth="800px" mx="auto" p={2}>
            {/* Header with Progress */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h5" component="h1">
                            Personality Assessment
                        </Typography>
                        <Chip
                            label={`${currentQuestionIndex + 1} of ${questions.length}`}
                            color="primary"
                            variant="outlined"
                        />
                    </Box>

                    <LinearProgress
                        variant="determinate"
                        value={((currentQuestionIndex + 1) / questions.length) * 100}
                        sx={{ mb: 2, height: 8, borderRadius: 4 }}
                    />

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" color="text.secondary">
                            {progress && `${Math.round(progress.completion_percentage)}% complete`}
                        </Typography>

                        {progress && progress.insights.length > 0 && (
                            <Button
                                size="small"
                                onClick={toggleInsights}
                                variant="outlined"
                            >
                                {showInsights ? 'Hide' : 'Show'} Insights ({progress.insights.length})
                            </Button>
                        )}
                    </Box>
                </CardContent>
            </Card>

            {/* Real-time Insights */}
            <AnimatePresence>
                {showInsights && progress && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <ProgressInsights insights={progress.insights} />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Question Card */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentQuestionIndex}
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -50 }}
                    transition={{ duration: 0.3 }}
                >
                    <QuestionCard
                        question={currentQuestion}
                        answer={currentAnswer?.answer}
                        onAnswer={(answer, confidence) => handleAnswer(currentQuestion.id, answer, confidence)}
                    />
                </motion.div>
            </AnimatePresence>

            {/* Navigation */}
            <Box display="flex" justifyContent="space-between" mt={3}>
                <Button
                    onClick={handlePrevious}
                    disabled={currentQuestionIndex === 0}
                    variant="outlined"
                >
                    Previous
                </Button>

                <Stack direction="row" spacing={2}>
                    {isLastQuestion ? (
                        <Button
                            onClick={handleSubmit}
                            disabled={!canProceed || isSubmitting}
                            variant="contained"
                            size="large"
                        >
                            {isSubmitting ? 'Completing Assessment...' : 'Complete Assessment'}
                        </Button>
                    ) : (
                        <Button
                            onClick={handleNext}
                            disabled={!canProceed}
                            variant="contained"
                            size="large"
                        >
                            Next Question
                        </Button>
                    )}
                </Stack>
            </Box>

            {/* Progress Summary */}
            {progress && (
                <Box mt={3} textAlign="center">
                    <Typography variant="body2" color="text.secondary">
                        Estimated time remaining: {progress.estimated_time_remaining} minutes
                    </Typography>
                </Box>
            )}
        </Box>
    );
};

export default PersonalityAssessment;