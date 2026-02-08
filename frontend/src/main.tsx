import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { store } from './store/store';
import { createAppTheme } from './theme/theme';
import { useAppSelector } from './hooks/redux';
import { updateToken } from './store/slices/authSlice';
import { AccessibilityProvider } from './contexts/AccessibilityContext';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';
import './index.css';
import './styles/accessibility.css';
import './i18n/config';

// Setup global token update handler for API client
window.dispatchTokenUpdate = (token: string) => {
    store.dispatch(updateToken(token));
};

// Theme wrapper component to access Redux state
const ThemedApp: React.FC = () => {
    const { mode } = useAppSelector(state => state.theme);
    const theme = React.useMemo(() => createAppTheme(mode), [mode]);

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <App />
        </ThemeProvider>
    );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ErrorBoundary>
            <Provider store={store}>
                <BrowserRouter>
                    <AccessibilityProvider>
                        <ThemedApp />
                    </AccessibilityProvider>
                </BrowserRouter>
            </Provider>
        </ErrorBoundary>
    </React.StrictMode>
);