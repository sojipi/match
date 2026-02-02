import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Alert,
    IconButton,
    InputAdornment,
    CircularProgress,
} from '@mui/material';
import {
    Visibility,
    VisibilityOff,
    CheckCircle,
    Error as ErrorIcon,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, useSearchParams } from 'react-router-dom';

// Validation schema
const resetPasswordSchema = z.object({
    password: z
        .string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
        .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
        .regex(/[0-9]/, 'Password must contain at least one number')
        .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
});

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

const ResetPasswordForm: React.FC = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [resetStatus, setResetStatus] = useState<'form' | 'success' | 'error' | 'invalid'>('form');
    const [error, setError] = useState<string | null>(null);

    const token = searchParams.get('token');
    const email = searchParams.get('email');

    const {
        register,
        handleSubmit,
        formState: { errors },
        watch,
    } = useForm<ResetPasswordFormData>({
        resolver: zodResolver(resetPasswordSchema),
        mode: 'onBlur',
    });

    const password = watch('password');

    useEffect(() => {
        if (!token || !email) {
            setResetStatus('invalid');
        } else {
            // Verify token validity
            verifyResetToken();
        }
    }, [token, email]);

    const verifyResetToken = async () => {
        try {
            const response = await fetch('/api/v1/auth/verify-reset-token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token, email }),
            });

            if (!response.ok) {
                setResetStatus('invalid');
            }
        } catch (err) {
            setResetStatus('invalid');
        }
    };

    const onSubmit = async (data: ResetPasswordFormData) => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await fetch('/api/v1/auth/confirm-password-reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token,
                    email,
                    password: data.password,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to reset password');
            }

            setResetStatus('success');

            // Redirect to login after a short delay
            setTimeout(() => {
                navigate('/auth/login', {
                    state: {
                        message: 'Password reset successful. Please sign in with your new password.'
                    }
                });
            }, 3000);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to reset password';
            setError(errorMessage);
            setResetStatus('error');
        } finally {
            setIsLoading(false);
        }
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const toggleConfirmPasswordVisibility = () => {
        setShowConfirmPassword(!showConfirmPassword);
    };

    // Password strength indicator
    const getPasswordStrength = (password: string) => {
        if (!password) return { strength: 0, label: '' };

        let strength = 0;
        if (password.length >= 8) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;

        const labels = ['', 'Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const colors = ['', '#f44336', '#ff9800', '#ffeb3b', '#8bc34a', '#4caf50'];

        return {
            strength,
            label: labels[strength],
            color: colors[strength],
            percentage: (strength / 5) * 100
        };
    };

    const passwordStrength = getPasswordStrength(password || '');

    const renderContent = () => {
        switch (resetStatus) {
            case 'success':
                return (
                    <Box textAlign="center">
                        <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                        <Typography
                            variant="h5"
                            component="h1"
                            gutterBottom
                            sx={{ fontWeight: 600 }}
                        >
                            Password Reset Successful!
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                            Your password has been successfully reset. You can now sign in with your new password.
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Redirecting to sign in page...
                        </Typography>
                        <Button
                            variant="contained"
                            onClick={() => navigate('/auth/login')}
                            sx={{ mt: 3 }}
                        >
                            Go to Sign In
                        </Button>
                    </Box>
                );

            case 'error':
                return (
                    <Box textAlign="center">
                        <ErrorIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
                        <Typography
                            variant="h5"
                            component="h1"
                            gutterBottom
                            sx={{ fontWeight: 600 }}
                        >
                            Reset Failed
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                            {error || 'We couldn\'t reset your password. Please try again or request a new reset link.'}
                        </Typography>
                        <Button
                            variant="contained"
                            onClick={() => navigate('/auth/forgot-password')}
                            sx={{ mt: 2 }}
                        >
                            Request New Reset Link
                        </Button>
                    </Box>
                );

            case 'invalid':
                return (
                    <Box textAlign="center">
                        <ErrorIcon sx={{ fontSize: 64, color: 'warning.main', mb: 2 }} />
                        <Typography
                            variant="h5"
                            component="h1"
                            gutterBottom
                            sx={{ fontWeight: 600 }}
                        >
                            Invalid Reset Link
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                            This password reset link is invalid or has expired. Please request a new one.
                        </Typography>
                        <Button
                            variant="contained"
                            onClick={() => navigate('/auth/forgot-password')}
                            sx={{ mt: 2 }}
                        >
                            Request New Reset Link
                        </Button>
                    </Box>
                );

            default:
                return (
                    <>
                        <Typography
                            variant="h4"
                            component="h1"
                            textAlign="center"
                            gutterBottom
                            sx={{ fontWeight: 600, mb: 2 }}
                        >
                            Reset Your Password
                        </Typography>

                        <Typography
                            variant="body2"
                            color="text.secondary"
                            textAlign="center"
                            sx={{ mb: 3 }}
                        >
                            Enter your new password below. Make sure it's strong and secure.
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
                                {...register('password')}
                                margin="normal"
                                fullWidth
                                label="New Password"
                                type={showPassword ? 'text' : 'password'}
                                autoComplete="new-password"
                                autoFocus
                                error={!!errors.password}
                                helperText={errors.password?.message}
                                disabled={isLoading}
                                InputProps={{
                                    endAdornment: (
                                        <InputAdornment position="end">
                                            <IconButton
                                                aria-label={showPassword ? 'Hide password' : 'Show password'}
                                                onClick={togglePasswordVisibility}
                                                edge="end"
                                                disabled={isLoading}
                                            >
                                                {showPassword ? <VisibilityOff /> : <Visibility />}
                                            </IconButton>
                                        </InputAdornment>
                                    ),
                                }}
                                inputProps={{
                                    'aria-describedby': errors.password ? 'password-error' : 'password-strength',
                                }}
                            />

                            {/* Password Strength Indicator */}
                            {password && (
                                <Box sx={{ mt: 1, mb: 1 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <Box
                                            sx={{
                                                flex: 1,
                                                height: 4,
                                                backgroundColor: 'grey.300',
                                                borderRadius: 2,
                                                overflow: 'hidden',
                                            }}
                                        >
                                            <Box
                                                sx={{
                                                    width: `${passwordStrength.percentage}%`,
                                                    height: '100%',
                                                    backgroundColor: passwordStrength.color,
                                                    transition: 'all 0.3s ease',
                                                }}
                                            />
                                        </Box>
                                        <Typography
                                            variant="caption"
                                            sx={{
                                                color: passwordStrength.color,
                                                fontWeight: 500,
                                                minWidth: 60,
                                            }}
                                            id="password-strength"
                                        >
                                            {passwordStrength.label}
                                        </Typography>
                                    </Box>
                                </Box>
                            )}

                            <TextField
                                {...register('confirmPassword')}
                                margin="normal"
                                fullWidth
                                label="Confirm New Password"
                                type={showConfirmPassword ? 'text' : 'password'}
                                autoComplete="new-password"
                                error={!!errors.confirmPassword}
                                helperText={errors.confirmPassword?.message}
                                disabled={isLoading}
                                InputProps={{
                                    endAdornment: (
                                        <InputAdornment position="end">
                                            <IconButton
                                                aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                                                onClick={toggleConfirmPasswordVisibility}
                                                edge="end"
                                                disabled={isLoading}
                                            >
                                                {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                                            </IconButton>
                                        </InputAdornment>
                                    ),
                                }}
                                inputProps={{
                                    'aria-describedby': errors.confirmPassword ? 'confirmPassword-error' : undefined,
                                }}
                            />

                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                disabled={isLoading}
                                sx={{
                                    mt: 3,
                                    mb: 2,
                                    py: 1.5,
                                    position: 'relative',
                                }}
                                aria-label="Reset password"
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
                                        <span style={{ opacity: 0 }}>Reset Password</span>
                                    </>
                                ) : (
                                    'Reset Password'
                                )}
                            </Button>
                        </Box>
                    </>
                );
        }
    };

    return (
        <Card sx={{ width: '100%', maxWidth: 400, mx: 'auto' }}>
            <CardContent sx={{ p: 4 }}>
                {renderContent()}
            </CardContent>
        </Card>
    );
};

export default ResetPasswordForm;