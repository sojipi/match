import React, { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Alert,
    Divider,
    IconButton,
    InputAdornment,
    Link as MuiLink,
    CircularProgress,
} from '@mui/material';
import {
    Visibility,
    VisibilityOff,
    Google as GoogleIcon,
    Facebook as FacebookIcon,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { loginStart, loginSuccess, loginFailure } from '../../store/slices/authSlice';

// Validation schema
const loginSchema = z.object({
    email: z
        .string()
        .min(1, 'Email is required')
        .email('Please enter a valid email address'),
    password: z
        .string()
        .min(1, 'Password is required')
        .min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const LoginForm: React.FC = () => {
    const dispatch = useAppDispatch();
    const navigate = useNavigate();
    const location = useLocation();
    const { isLoading, error } = useAppSelector(state => state.auth);

    const [showPassword, setShowPassword] = useState(false);
    const [socialLoading, setSocialLoading] = useState<'google' | 'facebook' | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        setError,
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
        mode: 'onBlur',
    });

    // Get the intended destination from location state
    const from = (location.state as any)?.from?.pathname || '/dashboard';

    const onSubmit = async (data: LoginFormData) => {
        try {
            dispatch(loginStart());

            // TODO: Replace with actual API call
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Login failed');
            }

            const result = await response.json();

            dispatch(loginSuccess({
                user: result.user,
                token: result.access_token,
                refreshToken: result.refresh_token,
            }));

            // Navigate to intended destination
            navigate(from, { replace: true });
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Login failed';
            dispatch(loginFailure(errorMessage));

            // Set form-specific errors if needed
            if (errorMessage.includes('email')) {
                setError('email', { message: errorMessage });
            } else if (errorMessage.includes('password')) {
                setError('password', { message: errorMessage });
            }
        }
    };

    const handleSocialLogin = async (provider: 'google' | 'facebook') => {
        try {
            setSocialLoading(provider);

            // TODO: Implement actual social login
            // This would typically redirect to OAuth provider
            window.location.href = `/api/v1/auth/social/${provider}`;
        } catch (err) {
            setSocialLoading(null);
            dispatch(loginFailure(`${provider} login failed`));
        }
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    return (
        <Card sx={{ width: '100%', maxWidth: 400, mx: 'auto' }}>
            <CardContent sx={{ p: 4 }}>
                <Typography
                    variant="h4"
                    component="h1"
                    textAlign="center"
                    gutterBottom
                    sx={{ fontWeight: 600, mb: 3 }}
                >
                    Welcome Back
                </Typography>

                <Typography
                    variant="body2"
                    color="text.secondary"
                    textAlign="center"
                    sx={{ mb: 3 }}
                >
                    Sign in to your AI Matchmaker account
                </Typography>

                {error && (
                    <Alert
                        severity="error"
                        sx={{ mb: 3 }}
                        onClose={() => dispatch(loginFailure(''))}
                    >
                        {error}
                    </Alert>
                )}

                {/* Social Login Buttons */}
                <Box sx={{ mb: 3 }}>
                    <Button
                        fullWidth
                        variant="outlined"
                        startIcon={
                            socialLoading === 'google' ? (
                                <CircularProgress size={20} />
                            ) : (
                                <GoogleIcon />
                            )
                        }
                        onClick={() => handleSocialLogin('google')}
                        disabled={isLoading || socialLoading !== null}
                        sx={{ mb: 1.5, py: 1.5 }}
                        aria-label="Sign in with Google"
                    >
                        Continue with Google
                    </Button>

                    <Button
                        fullWidth
                        variant="outlined"
                        startIcon={
                            socialLoading === 'facebook' ? (
                                <CircularProgress size={20} />
                            ) : (
                                <FacebookIcon />
                            )
                        }
                        onClick={() => handleSocialLogin('facebook')}
                        disabled={isLoading || socialLoading !== null}
                        sx={{ py: 1.5 }}
                        aria-label="Sign in with Facebook"
                    >
                        Continue with Facebook
                    </Button>
                </Box>

                <Divider sx={{ my: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                        or
                    </Typography>
                </Divider>

                {/* Email/Password Form */}
                <Box
                    component="form"
                    onSubmit={handleSubmit(onSubmit)}
                    noValidate
                    role="form"
                    aria-label="Login form"
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

                    <TextField
                        {...register('password')}
                        margin="normal"
                        fullWidth
                        label="Password"
                        type={showPassword ? 'text' : 'password'}
                        autoComplete="current-password"
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
                            'aria-describedby': errors.password ? 'password-error' : undefined,
                        }}
                    />

                    <Box sx={{ textAlign: 'right', mt: 1, mb: 2 }}>
                        <MuiLink
                            component={Link}
                            to="/auth/forgot-password"
                            variant="body2"
                            sx={{ textDecoration: 'none' }}
                        >
                            Forgot your password?
                        </MuiLink>
                    </Box>

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        disabled={isLoading || isSubmitting}
                        sx={{
                            mt: 2,
                            mb: 3,
                            py: 1.5,
                            position: 'relative',
                        }}
                        aria-label="Sign in to your account"
                    >
                        {isLoading || isSubmitting ? (
                            <>
                                <CircularProgress
                                    size={20}
                                    sx={{
                                        position: 'absolute',
                                        left: '50%',
                                        marginLeft: '-10px',
                                    }}
                                />
                                <span style={{ opacity: 0 }}>Sign In</span>
                            </>
                        ) : (
                            'Sign In'
                        )}
                    </Button>

                    <Box textAlign="center">
                        <Typography variant="body2" color="text.secondary">
                            Don't have an account?{' '}
                            <MuiLink
                                component={Link}
                                to="/auth/register"
                                sx={{
                                    textDecoration: 'none',
                                    fontWeight: 500,
                                }}
                            >
                                Sign up for free
                            </MuiLink>
                        </Typography>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
};

export default LoginForm;