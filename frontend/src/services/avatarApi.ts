/**
 * AI Avatar API service
 */
import { apiClient } from '../utils/api';
import {
    AIAvatar,
    AvatarCustomization,
    AvatarCustomizationRequest,
    AvatarCompletenessAnalysis,
    AvatarTrainingSession
} from '../types/avatar';

export const avatarApi = {
    /**
     * Create AI avatar from user's personality profile
     */
    createAvatar: async (userId: string): Promise<AIAvatar> => {
        const response = await apiClient.post(`/api/v1/avatar/create/${userId}`);
        return response;
    },

    /**
     * Get user's AI avatar
     */
    getAvatar: async (userId: string): Promise<AIAvatar> => {
        const response = await apiClient.get(`/api/v1/avatar/${userId}`);
        return response;
    },

    /**
     * Update avatar from personality profile changes
     */
    updateAvatarFromPersonality: async (userId: string): Promise<AIAvatar> => {
        const response = await apiClient.put(`/api/v1/avatar/update/${userId}`);
        return response;
    },

    /**
     * Customize avatar
     */
    customizeAvatar: async (
        avatarId: string,
        customization: AvatarCustomizationRequest
    ): Promise<AvatarCustomization> => {
        const response = await apiClient.post(
            `/api/v1/avatar/${avatarId}/customize`,
            customization
        );
        return response;
    },

    /**
     * Get avatar customizations
     */
    getAvatarCustomizations: async (avatarId: string): Promise<AvatarCustomization[]> => {
        const response = await apiClient.get(`/api/v1/avatar/${avatarId}/customizations`);
        return response;
    },

    /**
     * Get avatar completeness analysis
     */
    getCompletenessAnalysis: async (avatarId: string): Promise<AvatarCompletenessAnalysis> => {
        const response = await apiClient.get(`/api/v1/avatar/${avatarId}/completeness`);
        return response;
    },

    /**
     * Get avatar training history
     */
    getTrainingHistory: async (avatarId: string): Promise<AvatarTrainingSession[]> => {
        const response = await apiClient.get(`/api/v1/avatar/${avatarId}/training-history`);
        return response;
    },

    /**
     * Manually retrain avatar
     */
    retrainAvatar: async (avatarId: string): Promise<AIAvatar> => {
        const response = await apiClient.post(`/api/v1/avatar/${avatarId}/retrain`);
        return response;
    }
};