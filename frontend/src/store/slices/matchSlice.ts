import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../../utils/api';

export interface PotentialMatch {
    user_id: string;
    display_name: string;
    age?: number;
    location: string;
    primary_photo_url?: string;
    bio_preview: string;
    compatibility_preview: number;
    shared_interests: string[];
    personality_highlights: string[];
    is_online: boolean;
    mutual_connections: number;
}

export interface MatchHistoryItem {
    id: string;
    user: {
        id: string;
        name: string;
        photo_url?: string;
    };
    compatibility_score: number;
    status: string;
    conversation_count: number;
    last_interaction?: string;
    created_at: string;
}

export interface MatchFilters {
    age_min?: number;
    age_max?: number;
    max_distance?: number;
    interests?: string[];
}

interface MatchState {
    // Discovery state
    potentialMatches: PotentialMatch[];
    currentMatchIndex: number;
    totalMatches: number;
    hasMoreMatches: boolean;
    discoveryLoading: boolean;
    discoveryError: string | null;
    filters: MatchFilters;
    recommendations: string[];

    // Match history state
    matchHistory: MatchHistoryItem[];
    historyLoading: boolean;
    historyError: string | null;

    // Action states
    likeLoading: boolean;
    passLoading: boolean;
    actionError: string | null;
}

const initialState: MatchState = {
    potentialMatches: [],
    currentMatchIndex: 0,
    totalMatches: 0,
    hasMoreMatches: true,
    discoveryLoading: false,
    discoveryError: null,
    filters: {
        age_min: 18,
        age_max: 50,
        max_distance: 50
    },
    recommendations: [],

    matchHistory: [],
    historyLoading: false,
    historyError: null,

    likeLoading: false,
    passLoading: false,
    actionError: null,
};

// Async thunks
export const discoverMatches = createAsyncThunk(
    'match/discoverMatches',
    async (params: { filters?: MatchFilters; limit?: number; offset?: number }) => {
        const { filters, limit = 20, offset = 0 } = params;

        const searchParams = new URLSearchParams();
        searchParams.append('limit', limit.toString());
        searchParams.append('offset', offset.toString());

        if (filters?.age_min) searchParams.append('age_min', filters.age_min.toString());
        if (filters?.age_max) searchParams.append('age_max', filters.age_max.toString());
        if (filters?.max_distance) searchParams.append('max_distance', filters.max_distance.toString());

        const response = await api.get(`/api/v1/matches/discover?${searchParams}`);
        return response;
    }
);

export const likeUser = createAsyncThunk(
    'match/likeUser',
    async (userId: string) => {
        const response = await api.post(`/api/v1/matches/like/${userId}`);
        return { userId, ...response };
    }
);

export const passUser = createAsyncThunk(
    'match/passUser',
    async (userId: string) => {
        const response = await api.post(`/api/v1/matches/pass/${userId}`);
        return { userId, ...response };
    }
);

export const fetchMatchHistory = createAsyncThunk(
    'match/fetchMatchHistory',
    async () => {
        const response = await api.get('/api/v1/matches/history');
        return response;
    }
);

const matchSlice = createSlice({
    name: 'match',
    initialState,
    reducers: {
        setFilters: (state, action: PayloadAction<MatchFilters>) => {
            state.filters = { ...state.filters, ...action.payload };
        },

        nextMatch: (state) => {
            if (state.currentMatchIndex < state.potentialMatches.length - 1) {
                state.currentMatchIndex += 1;
            }
        },

        resetCurrentMatch: (state) => {
            state.currentMatchIndex = 0;
        },

        clearDiscoveryError: (state) => {
            state.discoveryError = null;
        },

        clearActionError: (state) => {
            state.actionError = null;
        },

        clearHistoryError: (state) => {
            state.historyError = null;
        },
    },
    extraReducers: (builder) => {
        // Discover matches
        builder
            .addCase(discoverMatches.pending, (state) => {
                state.discoveryLoading = true;
                state.discoveryError = null;
            })
            .addCase(discoverMatches.fulfilled, (state, action) => {
                state.discoveryLoading = false;
                state.potentialMatches = action.payload.matches;
                state.totalMatches = action.payload.total_count;
                state.hasMoreMatches = action.payload.has_more;
                state.recommendations = action.payload.recommendations || [];
                state.currentMatchIndex = 0;
            })
            .addCase(discoverMatches.rejected, (state, action) => {
                state.discoveryLoading = false;
                state.discoveryError = action.error.message || 'Failed to discover matches';
            });

        // Like user
        builder
            .addCase(likeUser.pending, (state) => {
                state.likeLoading = true;
                state.actionError = null;
            })
            .addCase(likeUser.fulfilled, (state, action) => {
                state.likeLoading = false;
                // Move to next match if not mutual
                if (!action.payload.is_mutual && state.currentMatchIndex < state.potentialMatches.length - 1) {
                    state.currentMatchIndex += 1;
                }
            })
            .addCase(likeUser.rejected, (state, action) => {
                state.likeLoading = false;
                state.actionError = action.error.message || 'Failed to like user';
            });

        // Pass user
        builder
            .addCase(passUser.pending, (state) => {
                state.passLoading = true;
                state.actionError = null;
            })
            .addCase(passUser.fulfilled, (state) => {
                state.passLoading = false;
                // Move to next match
                if (state.currentMatchIndex < state.potentialMatches.length - 1) {
                    state.currentMatchIndex += 1;
                }
            })
            .addCase(passUser.rejected, (state, action) => {
                state.passLoading = false;
                state.actionError = action.error.message || 'Failed to pass on user';
            });

        // Fetch match history
        builder
            .addCase(fetchMatchHistory.pending, (state) => {
                state.historyLoading = true;
                state.historyError = null;
            })
            .addCase(fetchMatchHistory.fulfilled, (state, action) => {
                state.historyLoading = false;
                state.matchHistory = action.payload.matches;
            })
            .addCase(fetchMatchHistory.rejected, (state, action) => {
                state.historyLoading = false;
                state.historyError = action.error.message || 'Failed to fetch match history';
            });
    },
});

export const {
    setFilters,
    nextMatch,
    resetCurrentMatch,
    clearDiscoveryError,
    clearActionError,
    clearHistoryError,
} = matchSlice.actions;

export default matchSlice.reducer;