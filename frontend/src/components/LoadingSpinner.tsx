import React from 'react';
import { Box, CircularProgress, Typography, Fade } from '@mui/material';

interface LoadingSpinnerProps {
    message?: string;
    size?: number;
    fullScreen?: boolean;
    delay?: number;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    message = 'Loading...',
    size = 40,
    fullScreen = false,
    delay = 0,
}) => {
    const [show, setShow] = React.useState(delay === 0);

    React.useEffect(() => {
        if (delay > 0) {
            const timer = setTimeout(() => setShow(true), delay);
            return () => clearTimeout(timer);
        }
    }, [delay]);

    const content = (
        <Fade in={show} timeout={300}>
            <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                gap={2}
                {...(fullScreen && {
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    bgcolor: 'background.default',
                    zIndex: 9999,
                })}
            >
                <CircularProgress
                    size={size}
                    thickness={4}
                    sx={{
                        color: 'primary.main',
                    }}
                />
                {message && (
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                            mt: 1,
                            textAlign: 'center',
                            maxWidth: 300,
                        }}
                    >
                        {message}
                    </Typography>
                )}
            </Box>
        </Fade>
    );

    if (!show) {
        return null;
    }

    return content;
};

export default LoadingSpinner;