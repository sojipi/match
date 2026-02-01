import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material';
import { store } from './store/store';
import { theme } from './theme/theme';
import App from './App';

const renderWithProviders = (ui: React.ReactElement) => {
    return render(
        <Provider store={store}>
            <BrowserRouter>
                <ThemeProvider theme={theme}>
                    {ui}
                </ThemeProvider>
            </BrowserRouter>
        </Provider>
    );
};

describe('App', () => {
    it('renders without crashing', () => {
        renderWithProviders(<App />);
        // The app should render without throwing an error
        expect(document.body).toBeTruthy();
    });
});