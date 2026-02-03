/**
 * Interactive Question Card Component
 * Displays different types of personality assessment questions with engaging UI
 */
import React, { useState } from 'react';
import {
    Card,
    CardContent,
    Typography,
    Slider,
    FormControl,
    FormControlLabel,
    Radio,
    RadioGroup,
    Box,
    Chip,
    Stack,
    Paper
} from '@mui/material';
import { motion } from 'framer-motion';
import {
    DragIndicator,
    Psychology,
    Favorite,
    Star,
    TrendingUp,
    Groups,
    Work
} from '@mui/icons-material';
import { PersonalityQuestion } from '../../types/personality';

interface QuestionCardProps {
    question: PersonalityQuestion;
    answer?: any;
    onAnswer: (answer: any, confidence?: number) => void;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
    question,
    answer,
    onAnswer
}) => {
    const [confidence, setConfidence] = useState<number>(4);
    const [draggedItems, setDraggedItems] = useState<string[]>(
        question.question_type === 'ranking' && question.options
            ? [...question.options]
            : []
    );

    const handleScaleChange = (value: number) => {
        onAnswer(value, confidence);
    };

    const handleMultipleChoiceChange = (selectedValue: string) => {
        onAnswer(selectedValue, confidence);
    };

    const handleRankingChange = (newOrder: string[]) => {
        setDraggedItems(newOrder);
        onAnswer(newOrder, confidence);
    };

    const handleConfidenceChange = (newConfidence: number) => {
        setConfidence(newConfidence);
        if (answer !== undefined) {
            onAnswer(answer, newConfidence);
        }
    };

    const getQuestionIcon = () => {
        const category = question.category.toLowerCase();
        switch (category) {
            case 'openness': return <Psychology color="primary" />;
            case 'conscientiousness': return <Work color="primary" />;
            case 'extraversion': return <Groups color="primary" />;
            case 'agreeableness': return <Favorite color="primary" />;
            case 'neuroticism': return <TrendingUp color="primary" />;
            case 'values': return <Star color="primary" />;
            case 'communication': return <Groups color="primary" />;
            default: return <Psychology color="primary" />;
        }
    };

    const renderScaleQuestion = () => {
        const min = question.scale_min || 1;
        const max = question.scale_max || 7;
        const labels = question.scale_labels || {};

        return (
            <Box>
                <Box sx={{ px: 2, mb: 3 }}>
                    <Slider
                        value={answer || Math.floor((min + max) / 2)}
                        min={min}
                        max={max}
                        step={1}
                        marks={Object.entries(labels).map(([value, label]) => ({
                            value: parseInt(value),
                            label: label
                        }))}
                        onChange={(_, value) => handleScaleChange(value as number)}
                        sx={{
                            '& .MuiSlider-thumb': {
                                width: 24,
                                height: 24,
                                '&:hover': {
                                    boxShadow: '0 0 0 8px rgba(25, 118, 210, 0.16)'
                                }
                            },
                            '& .MuiSlider-track': {
                                height: 6
                            },
                            '& .MuiSlider-rail': {
                                height: 6
                            }
                        }}
                    />
                </Box>

                <Box display="flex" justifyContent="space-between" sx={{ px: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                        {labels[min.toString()] || `${min}`}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        {labels[max.toString()] || `${max}`}
                    </Typography>
                </Box>

                {answer && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <Box textAlign="center" mt={2}>
                            <Chip
                                label={`Your answer: ${answer}`}
                                color="primary"
                                variant="outlined"
                            />
                        </Box>
                    </motion.div>
                )}
            </Box>
        );
    };

    const renderMultipleChoiceQuestion = () => {
        return (
            <FormControl component="fieldset" fullWidth>
                <RadioGroup
                    value={answer || ''}
                    onChange={(e) => handleMultipleChoiceChange(e.target.value)}
                >
                    <Stack spacing={1}>
                        {question.options?.map((option, index) => (
                            <motion.div
                                key={option}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.3, delay: index * 0.1 }}
                            >
                                <Paper
                                    elevation={answer === option ? 2 : 0}
                                    sx={{
                                        p: 1,
                                        border: answer === option ? 2 : 1,
                                        borderColor: answer === option ? 'primary.main' : 'divider',
                                        transition: 'all 0.2s ease-in-out',
                                        '&:hover': {
                                            elevation: 1,
                                            borderColor: 'primary.light'
                                        }
                                    }}
                                >
                                    <FormControlLabel
                                        value={option}
                                        control={<Radio />}
                                        label={option}
                                        sx={{ width: '100%', m: 0 }}
                                    />
                                </Paper>
                            </motion.div>
                        ))}
                    </Stack>
                </RadioGroup>
            </FormControl>
        );
    };

    const renderRankingQuestion = () => {
        const handleDragStart = (e: React.DragEvent, item: string) => {
            e.dataTransfer.setData('text/plain', item);
        };

        const handleDragOver = (e: React.DragEvent) => {
            e.preventDefault();
        };

        const handleDrop = (e: React.DragEvent, targetIndex: number) => {
            e.preventDefault();
            const draggedItem = e.dataTransfer.getData('text/plain');
            const currentIndex = draggedItems.indexOf(draggedItem);

            if (currentIndex !== -1) {
                const newItems = [...draggedItems];
                newItems.splice(currentIndex, 1);
                newItems.splice(targetIndex, 0, draggedItem);
                handleRankingChange(newItems);
            }
        };

        return (
            <Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Drag and drop to rank these items in order of importance to you:
                </Typography>
                <Stack spacing={1}>
                    {draggedItems.map((item, index) => (
                        <motion.div
                            key={item}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                        >
                            <Paper
                                draggable
                                onDragStart={(e) => handleDragStart(e, item)}
                                onDragOver={handleDragOver}
                                onDrop={(e) => handleDrop(e, index)}
                                sx={{
                                    p: 2,
                                    cursor: 'grab',
                                    border: 1,
                                    borderColor: 'divider',
                                    '&:hover': {
                                        borderColor: 'primary.light',
                                        elevation: 1
                                    },
                                    '&:active': {
                                        cursor: 'grabbing'
                                    }
                                }}
                            >
                                <Box display="flex" alignItems="center">
                                    <DragIndicator sx={{ mr: 1, color: 'text.secondary' }} />
                                    <Typography variant="body1">{item}</Typography>
                                    <Box flexGrow={1} />
                                    <Chip
                                        label={`#${index + 1}`}
                                        size="small"
                                        color="primary"
                                        variant="outlined"
                                    />
                                </Box>
                            </Paper>
                        </motion.div>
                    ))}
                </Stack>
            </Box>
        );
    };

    const renderConfidenceSlider = () => {
        if (answer === undefined) return null;

        return (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
            >
                <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                        How confident are you in this answer?
                    </Typography>
                    <Box sx={{ px: 1 }}>
                        <Slider
                            value={confidence}
                            min={1}
                            max={5}
                            step={1}
                            marks={[
                                { value: 1, label: 'Not sure' },
                                { value: 3, label: 'Somewhat' },
                                { value: 5, label: 'Very sure' }
                            ]}
                            onChange={(_, value) => handleConfidenceChange(value as number)}
                            sx={{ mt: 1 }}
                        />
                    </Box>
                </Box>
            </motion.div>
        );
    };

    return (
        <Card sx={{ maxWidth: 600, mx: 'auto' }}>
            <CardContent sx={{ p: 3 }}>
                {/* Question Header */}
                <Box display="flex" alignItems="flex-start" mb={3}>
                    <Box sx={{ mr: 2, mt: 0.5 }}>
                        {getQuestionIcon()}
                    </Box>
                    <Box flexGrow={1}>
                        <Typography variant="overline" color="text.secondary">
                            {question.category.toUpperCase()}
                        </Typography>
                        <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
                            {question.question}
                        </Typography>
                    </Box>
                </Box>

                {/* Question Content */}
                <Box>
                    {question.question_type === 'scale' && renderScaleQuestion()}
                    {question.question_type === 'multiple_choice' && renderMultipleChoiceQuestion()}
                    {question.question_type === 'ranking' && renderRankingQuestion()}
                </Box>

                {/* Confidence Slider */}
                {renderConfidenceSlider()}
            </CardContent>
        </Card>
    );
};

export default QuestionCard;
