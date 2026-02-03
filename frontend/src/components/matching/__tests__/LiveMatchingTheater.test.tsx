/**
 * Tests for LiveMatchingTheater component
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ThemeProvider, createTheme } from '@mui/material/styles';

import { vi } from 'vitest';

import LiveMatchingTheater from '../LiveMatchingTheater';
import authSlice from '../../../store/slices/authSlice';

// Mock WebSocket
global.WebSocket = vi.fn(() => ({
    close: vi.fn(),
    send: vi.fn(),
    readyState: 1,
    OPEN: 1
})) as any;

const mockStore = configureStore({
    reducer: {
        auth: authSlice
    },
    preloadedState: {
        auth: {
            user: {
                id: 'test-user',
                email: 'test@example.com',
                username: 'testuser',
                first_name: 'Test',
                last_name: 'User'
            },
            token: 'test-token',
            isLoading: false
        }
    }
});

const theme = createTheme();

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

describe('LiveMatchingTheater', () => {
    beforeEach(() => {
        // Mock localStorage
        Object.defineProperty(window, 'localStorage', {
            value: {
                getItem: jest.fn(() => 'test-token'),
                setItem: jest.fn(),
                removeItem: jest.fn(),
            },
            writable: true,
        });
    });

    it('renders loading state initially', () => {
        renderWithProviders(<LiveMatchingTheater sessionId="test-session" />);

        expect(screen.getByText('Connecting to AI Theater...')).toBeInTheDocument();
    });

    it('renders theater header when loaded', async () => {
        renderWithProviders(<LiveMatchingTheater sessionId="test-session" />);

        // The component should render the header
        expect(screen.getByText('Live AI Theater')).toBeInTheDocument();
    });

    it('handles missing session ID', () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });

        renderWithProviders(<LiveMatchingTheater />);

        // Should handle gracefully
        expect(consoleSpy).not.toHaveBeenCalled();

        consoleSpy.mockRestore();
    });
});