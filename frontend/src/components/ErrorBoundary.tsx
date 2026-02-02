import { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Container, Alert } from '@mui/material';
import { RefreshOutlined, BugReportOutlined } from '@mui/icons-material';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }

    static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
            errorInfo: null,
        };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        this.setState({
            error,
            errorInfo,
        });

        // Log error to console in development
        if (process.env.NODE_ENV === 'development') {
            console.error('Error caught by boundary:', error, errorInfo);
        }

        // In production, you would send this to an error reporting service
        // Example: Sentry.captureException(error, { extra: errorInfo });
    }

    handleReload = () => {
        window.location.reload();
    };

    handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        });
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <Container maxWidth="md">
                    <Box
                        display="flex"
                        flexDirection="column"
                        alignItems="center"
                        justifyContent="center"
                        minHeight="100vh"
                        textAlign="center"
                        p={3}
                    >
                        <BugReportOutlined
                            sx={{ fontSize: 64, color: 'error.main', mb: 2 }}
                        />

                        <Typography variant="h4" component="h1" gutterBottom>
                            Oops! Something went wrong
                        </Typography>

                        <Typography variant="body1" color="text.secondary" paragraph>
                            We're sorry, but something unexpected happened.
                            Please try refreshing the page or contact support if the problem persists.
                        </Typography>

                        {process.env.NODE_ENV === 'development' && this.state.error && (
                            <Alert severity="error" sx={{ mt: 2, mb: 2, textAlign: 'left', width: '100%' }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Error Details (Development Mode):
                                </Typography>
                                <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', overflow: 'auto' }}>
                                    {this.state.error.toString()}
                                    {this.state.errorInfo?.componentStack}
                                </Typography>
                            </Alert>
                        )}

                        <Box mt={3} display="flex" gap={2} flexWrap="wrap" justifyContent="center">
                            <Button
                                variant="contained"
                                startIcon={<RefreshOutlined />}
                                onClick={this.handleReload}
                                size="large"
                            >
                                Refresh Page
                            </Button>

                            <Button
                                variant="outlined"
                                onClick={this.handleReset}
                                size="large"
                            >
                                Try Again
                            </Button>
                        </Box>
                    </Box>
                </Container>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;