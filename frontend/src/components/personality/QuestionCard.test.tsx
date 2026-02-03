/**
 * Tests for QuestionCard component
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import QuestionCard from './QuestionCard';
import { PersonalityQuestion } from '../../types/personality';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
    return render(
        <ThemeProvider theme={theme}>
            {component}
        </ThemeProvider>
    );
};

describe('QuestionCard', () => {
    const mockScaleQuestion: PersonalityQuestion = {
        id: 'test_scale',
        category: 'openness',
        question: 'I enjoy exploring new ideas',
        question_type: 'scale',
        scale_min: 1,
        scale_max: 7,
        scale_labels: { '1': 'Strongly Disagree', '7': 'Strongly Agree' }
    };

    const mockMultipleChoiceQuestion: PersonalityQuestion = {
        id: 'test_mc',
        category: 'values',
        question: 'What matters most to you?',
        question_type: 'multiple_choice',
        options: ['Family', 'Career', 'Adventure', 'Security']
    };

    const mockRankingQuestion: PersonalityQuestion = {
        id: 'test_ranking',
        category: 'values',
        question: 'Rank these values by importance',
        question_type: 'ranking',
        options: ['Family', 'Career', 'Adventure']
    };

    it('renders scale question correctly', () => {
        const onAnswer = vi.fn();

        renderWithTheme(
            <QuestionCard
                question={mockScaleQuestion}
                onAnswer={onAnswer}
            />
        );

        expect(screen.getByText('I enjoy exploring new ideas')).toBeInTheDocument();
        expect(screen.getByText('OPENNESS')).toBeInTheDocument();
        expect(screen.getAllByText('Strongly Disagree')[0]).toBeInTheDocument();
        expect(screen.getByText('Strongly Agree')).toBeInTheDocument();
    });

    it('renders multiple choice question correctly', () => {
        const onAnswer = vi.fn();

        renderWithTheme(
            <QuestionCard
                question={mockMultipleChoiceQuestion}
                onAnswer={onAnswer}
            />
        );

        expect(screen.getByText('What matters most to you?')).toBeInTheDocument();
        expect(screen.getByText('VALUES')).toBeInTheDocument();
        expect(screen.getByText('Family')).toBeInTheDocument();
        expect(screen.getByText('Career')).toBeInTheDocument();
        expect(screen.getByText('Adventure')).toBeInTheDocument();
        expect(screen.getByText('Security')).toBeInTheDocument();
    });

    it('renders ranking question correctly', () => {
        const onAnswer = vi.fn();

        renderWithTheme(
            <QuestionCard
                question={mockRankingQuestion}
                onAnswer={onAnswer}
            />
        );

        expect(screen.getByText('Rank these values by importance')).toBeInTheDocument();
        expect(screen.getByText('VALUES')).toBeInTheDocument();
        expect(screen.getByText(/Drag and drop to rank these items/)).toBeInTheDocument();
    });

    it('calls onAnswer when multiple choice option is selected', () => {
        const onAnswer = vi.fn();

        renderWithTheme(
            <QuestionCard
                question={mockMultipleChoiceQuestion}
                onAnswer={onAnswer}
            />
        );

        const familyOption = screen.getByLabelText('Family');
        fireEvent.click(familyOption);

        expect(onAnswer).toHaveBeenCalledWith('Family', 4);
    });

    it('shows confidence slider when answer is provided', () => {
        const onAnswer = vi.fn();

        renderWithTheme(
            <QuestionCard
                question={mockScaleQuestion}
                answer={5}
                onAnswer={onAnswer}
            />
        );

        expect(screen.getByText('How confident are you in this answer?')).toBeInTheDocument();
        expect(screen.getByText('Your answer: 5')).toBeInTheDocument();
    });

    it('displays correct category icon', () => {
        const onAnswer = vi.fn();

        renderWithTheme(
            <QuestionCard
                question={mockScaleQuestion}
                onAnswer={onAnswer}
            />
        );

        // Check that the Psychology icon is rendered for openness category
        const icons = document.querySelectorAll('[data-testid="PsychologyIcon"]');
        expect(icons.length).toBeGreaterThan(0);
    });
});