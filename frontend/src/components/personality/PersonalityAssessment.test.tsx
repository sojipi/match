/**
 * Tests for PersonalityAssessment component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { configureStore } from '@reduxjs/toolkit';
import PersonalityAssessment from './PersonalityAssessment';
import { personalityApi } from '../../services/personalityApi';

// Mock the personality API
vi.mock('../../services/personalityApi', () => ({
    personalityApi: {
        getQuestions: vi.fn(),
        getProgress: vi.fn(),
        submitAssessment: vi.fn(),
    }
}));

const mockQuestions = [
    {
        id: 'test_1',
        category: 'openness',
        question: 'I enjoy exploring new ideas',
        question_type: 'scale',
        scale_min: 1,
        scale_max: 7,
        scale_labels: { '1': 'Strongly Disagree', '7': 'Strongly Agree' }
    }
];

const mockProgress = {
    current_step: 1,
    total_steps: 5,
    completion_percentage: 20,
    estimated_time_remaining: 8,
    insights: []
};

const theme = createTheme();

const mockStore = configureStore({
    reducer: {
        auth: () => ({ user: { id: 'test-user' }, isLoading: false }),
        theme: () => ({ mode: 'light' }),
        user: () => ({})
    }
});

const renderWithProviders = (component: React.ReactElement) => {
    return render(
        <Provider store={mockStore}>
            <BrowserRouter>
                <ThemeProvider theme={theme}>
                    {component}
                </ThemeProvider>
            </BrowserRouter>
        </Provider>
    );
};

describe('PersonalityAssessment', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        (personalityApi.getQuestions as any).mockResolvedValue(mockQuestions);
        (personalityApi.getProgress as any).mockResolvedValue(mockProgress);
    });

    it('renders loading state initially', () => {
        renderWithProviders(
            <PersonalityAssessment
                userId="test-user"
                onComplete={vi.fn()}
            />
        );

        expect(screen.getByText('Loading your personality assessment...')).toBeInTheDocument();
    });

    it('loads questions and displays first question', async () => {
        renderWithProviders(
            <PersonalityAssessment
                userId="test-user"
                onComplete={vi.fn()}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('Personality Assessment')).toBeInTheDocument();
        });

        await waitFor(() => {
            expect(screen.getByText('I enjoy exploring new ideas')).toBeInTheDocument();
        });

        expect(personalityApi.getQuestions).toHaveBeenCalled();
        expect(personalityApi.getProgress).toHaveBeenCalledWith('test-user');
    });

    it('displays progress information', async () => {
        renderWithProviders(
            <PersonalityAssessment
                userId="test-user"
                onComplete={vi.fn()}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('1 of 1')).toBeInTheDocument();
        });

        await waitFor(() => {
            expect(screen.getByText('20% complete')).toBeInTheDocument();
        });
    });

    it('calls onProgress callback when provided', async () => {
        const onProgress = vi.fn();

        renderWithProviders(
            <PersonalityAssessment
                userId="test-user"
                onComplete={vi.fn()}
                onProgress={onProgress}
            />
        );

        await waitFor(() => {
            expect(onProgress).toHaveBeenCalledWith(mockProgress);
        });
    });

    it('handles API errors gracefully', async () => {
        (personalityApi.getQuestions as any).mockRejectedValue(new Error('API Error'));

        renderWithProviders(
            <PersonalityAssessment
                userId="test-user"
                onComplete={vi.fn()}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('Failed to load assessment. Please try again.')).toBeInTheDocument();
        });
    });
});