/**
 * Personality assessment API service
 */
import { apiClient } from '../utils/api';
import {
    PersonalityQuestion,
    PersonalityAssessmentRequest,
    PersonalityProfile,
    AssessmentProgress
} from '../types/personality';

export const personalityApi = {
    /**
     * Get personality assessment questions
     */
    getQuestions: async (step?: number, previousAnswers?: string): Promise<PersonalityQuestion[]> => {
        const params = new URLSearchParams();
        if (step) params.append('step', step.toString());
        if (previousAnswers) params.append('previous_answers', previousAnswers);

        const response = await apiClient.get(`/api/v1/personality/questions?${params.toString()}`);
        return response;
    },

    /**
     * Get assessment progress for a user
     */
    getProgress: async (userId: string): Promise<AssessmentProgress> => {
        const response = await apiClient.get(`/api/v1/personality/progress/${userId}`);
        return response;
    },

    /**
     * Submit personality assessment
     */
    submitAssessment: async (userId: string, assessmentData: PersonalityAssessmentRequest): Promise<PersonalityProfile> => {
        const response = await apiClient.post(`/api/v1/personality/submit?user_id=${userId}`, assessmentData);
        return response;
    },

    /**
     * Get personality profile
     */
    getProfile: async (userId: string): Promise<PersonalityProfile> => {
        const response = await apiClient.get(`/api/v1/personality/profile/${userId}`);
        return response;
    }
};