import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { store } from './store/store';
import { createAppTheme } from './theme/theme';
import { useAppSelector } from './hooks/redux';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';
import './index.css';

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
                    <ThemedApp />
                </BrowserRouter>
            </Provider>
        </ErrorBoundary>
    </React.StrictMode>
);