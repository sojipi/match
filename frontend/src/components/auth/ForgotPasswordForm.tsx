import React, { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Alert,
    Link as MuiLink,
    CircularProgress,
} from '@mui/material';
import { ArrowBack, Email } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';

// Validation schema
const forgotPasswordSchema = z.object({
    email: z
        .string()
        .min(1, 'Email is required')
        .email('Please enter a valid email address'),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

const ForgotPasswordForm: React.FC = () => {
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors },
        getValues,
    } = useForm<ForgotPasswordFormData>({
        resolver: zodResolver(forgotPasswordSchema),
        mode: 'onBlur',
    });

    const onSubmit = async (data: ForgotPasswordFormData) => {
        try {
            setIsLoading(true);
            setError(null);

            // TODO: Replace with actual API call
            const response = await fetch('/api/v1/auth/request-password-reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to send reset email');
            }

            setIsSubmitted(true);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to send reset email';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleResendEmail = async () => {
        const email = getValues('email');
        if (email) {
            await onSubmit({ email });
        }
    };

    if (isSubmitted) {
        return (
            <Card sx={{ width: '100%', maxWidth: 400, mx: 'auto' }}>
                <CardContent sx={{ p: 4, textAlign: 'center' }}>
                    <Email sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />

                    <Typography
                        variant="h5"
                        component="h1"
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                    >
                        Check Your Email
                    </Typography>

                    <Typography
                        variant="body1"
                        color="text.secondary"
                        sx={{ mb: 3 }}
                    >
                        We've sent a password reset link to{' '}
                        <strong>{getValues('email')}</strong>
                    </Typography>

                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 3 }}
                    >
                        Didn't receive the email? Check your spam folder or try again.
                    </Typography>

                    <Button
                        variant="outlined"
                        onClick={handleResendEmail}
                        disabled={isLoading}
                        sx={{ mb: 2 }}
                        fullWidth
                    >
                        {isLoading ? (
                            <CircularProgress size={20} />
                        ) : (
                            'Resend Email'
                        )}
                    </Button>

                    <MuiLink
                        component={Link}
                        to="/auth/login"
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 1,
                            textDecoration: 'none',
                            mt: 2,
                        }}
                    >
                        <ArrowBack fontSize="small" />
                        Back to Sign In
                    </MuiLink>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card sx={{ width: '100%', maxWidth: 400, mx: 'auto' }}>
            <CardContent sx={{ p: 4 }}>
                <Typography
                    variant="h4"
                    component="h1"
                    textAlign="center"
                    gutterBottom
                    sx={{ fontWeight: 600, mb: 2 }}
                >
                    Reset Password
                </Typography>

                <Typography
                    variant="body2"
                    color="text.secondary"
                    textAlign="center"
                    sx={{ mb: 3 }}
                >
                    Enter your email address and we'll send you a link to reset your password.
                </Typography>

                {error && (
                    <Alert
                        severity="error"
                        sx={{ mb: 3 }}
                        onClose={() => setError(null)}
                    >
                        {error}
                    </Alert>
                )}

                <Box
                    component="form"
                    onSubmit={handleSubmit(onSubmit)}
                    noValidate
                    role="form"
                    aria-label="Password reset form"
                >
                    <TextField
                        {...register('email')}
                        margin="normal"
                        fullWidth
                        label="Email Address"
                        type="email"
                        autoComplete="email"
                        autoFocus
                        error={!!errors.email}
                        helperText={errors.email?.message}
                        disabled={isLoading}
                        inputProps={{
                            'aria-describedby': errors.email ? 'email-error' : undefined,
                        }}
                    />

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        disabled={isLoading}
                        sx={{
                            mt: 3,
                            mb: 3,
                            py: 1.5,
                            position: 'relative',
                        }}
                        aria-label="Send password reset email"
                    >
                        {isLoading ? (
                            <>
                                <CircularProgress
                                    size={20}
                                    sx={{
                                        position: 'absolute',
                                        left: '50%',
                                        marginLeft: '-10px',
                                    }}
                                />
                                <span style={{ opacity: 0 }}>Send Reset Link</span>
                            </>
                        ) : (
                            'Send Reset Link'
                        )}
                    </Button>

                    <Box textAlign="center">
                        <MuiLink
                            component={Link}
                            to="/auth/login"
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: 1,
                                textDecoration: 'none',
                            }}
                        >
                            <ArrowBack fontSize="small" />
                            Back to Sign In
                        </MuiLink>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
};

export default ForgotPasswordForm;