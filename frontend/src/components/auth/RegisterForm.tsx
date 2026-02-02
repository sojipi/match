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
    FormControlLabel,
    Checkbox,
    Grid,
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
import { Link, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { loginStart, loginSuccess, loginFailure } from '../../store/slices/authSlice';

// Validation schema
const registerSchema = z.object({
    firstName: z
        .string()
        .min(1, 'First name is required')
        .min(2, 'First name must be at least 2 characters')
        .max(50, 'First name must be less than 50 characters'),
    lastName: z
        .string()
        .min(1, 'Last name is required')
        .min(2, 'Last name must be at least 2 characters')
        .max(50, 'Last name must be less than 50 characters'),
    email: z
        .string()
        .min(1, 'Email is required')
        .email('Please enter a valid email address'),
    password: z
        .string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
        .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
        .regex(/[0-9]/, 'Password must contain at least one number')
        .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
    agreeToTerms: z.boolean().refine(val => val === true, {
        message: 'You must agree to the terms and conditions',
    }),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

const RegisterForm: React.FC = () => {
    const dispatch = useAppDispatch();
    const navigate = useNavigate();
    const { isLoading, error } = useAppSelector(state => state.auth);

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [socialLoading, setSocialLoading] = useState<'google' | 'facebook' | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        setError,
        watch,
    } = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema),
        mode: 'onBlur',
    });

    const password = watch('password');

    const onSubmit = async (data: RegisterFormData) => {
        try {
            dispatch(loginStart());

            // TODO: Replace with actual API call
            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    first_name: data.firstName,
                    last_name: data.lastName,
                    username: data.email.split('@')[0], // Generate username from email
                    email: data.email,
                    password: data.password,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Registration failed');
            }

            const result = await response.json();

            dispatch(loginSuccess({
                user: result.user,
                token: result.access_token,
                refreshToken: result.refresh_token,
            }));

            // Navigate to email verification or dashboard
            navigate(result.requiresVerification ? '/auth/verify-email' : '/dashboard');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Registration failed';
            dispatch(loginFailure(errorMessage));

            // Set form-specific errors if needed
            if (errorMessage.includes('email')) {
                setError('email', { message: errorMessage });
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
            dispatch(loginFailure(`${provider} registration failed`));
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

    return (
        <Card sx={{ width: '100%', maxWidth: 500, mx: 'auto' }}>
            <CardContent sx={{ p: 4 }}>
                <Typography
                    variant="h4"
                    component="h1"
                    textAlign="center"
                    gutterBottom
                    sx={{ fontWeight: 600, mb: 2 }}
                >
                    Create Account
                </Typography>

                <Typography
                    variant="body2"
                    color="text.secondary"
                    textAlign="center"
                    sx={{ mb: 3 }}
                >
                    Join AI Matchmaker and find your perfect match
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
                        aria-label="Sign up with Google"
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
                        aria-label="Sign up with Facebook"
                    >
                        Continue with Facebook
                    </Button>
                </Box>

                <Divider sx={{ my: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                        or
                    </Typography>
                </Divider>

                {/* Registration Form */}
                <Box
                    component="form"
                    onSubmit={handleSubmit(onSubmit)}
                    noValidate
                    role="form"
                    aria-label="Registration form"
                >
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                {...register('firstName')}
                                fullWidth
                                label="First Name"
                                autoComplete="given-name"
                                autoFocus
                                error={!!errors.firstName}
                                helperText={errors.firstName?.message}
                                disabled={isLoading}
                                inputProps={{
                                    'aria-describedby': errors.firstName ? 'firstName-error' : undefined,
                                }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                {...register('lastName')}
                                fullWidth
                                label="Last Name"
                                autoComplete="family-name"
                                error={!!errors.lastName}
                                helperText={errors.lastName?.message}
                                disabled={isLoading}
                                inputProps={{
                                    'aria-describedby': errors.lastName ? 'lastName-error' : undefined,
                                }}
                            />
                        </Grid>
                    </Grid>

                    <TextField
                        {...register('email')}
                        margin="normal"
                        fullWidth
                        label="Email Address"
                        type="email"
                        autoComplete="email"
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
                        autoComplete="new-password"
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
                        label="Confirm Password"
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

                    <FormControlLabel
                        control={
                            <Checkbox
                                {...register('agreeToTerms')}
                                disabled={isLoading}
                                inputProps={{
                                    'aria-describedby': errors.agreeToTerms ? 'terms-error' : undefined,
                                }}
                            />
                        }
                        label={
                            <Typography variant="body2">
                                I agree to the{' '}
                                <MuiLink
                                    component={Link}
                                    to="/terms"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    sx={{ textDecoration: 'none' }}
                                >
                                    Terms of Service
                                </MuiLink>
                                {' '}and{' '}
                                <MuiLink
                                    component={Link}
                                    to="/privacy"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    sx={{ textDecoration: 'none' }}
                                >
                                    Privacy Policy
                                </MuiLink>
                            </Typography>
                        }
                        sx={{ mt: 2, alignItems: 'flex-start' }}
                    />

                    {errors.agreeToTerms && (
                        <Typography
                            variant="caption"
                            color="error"
                            sx={{ mt: 1, display: 'block' }}
                            id="terms-error"
                        >
                            {errors.agreeToTerms.message}
                        </Typography>
                    )}

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        disabled={isLoading || isSubmitting}
                        sx={{
                            mt: 3,
                            mb: 3,
                            py: 1.5,
                            position: 'relative',
                        }}
                        aria-label="Create your account"
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
                                <span style={{ opacity: 0 }}>Create Account</span>
                            </>
                        ) : (
                            'Create Account'
                        )}
                    </Button>

                    <Box textAlign="center">
                        <Typography variant="body2" color="text.secondary">
                            Already have an account?{' '}
                            <MuiLink
                                component={Link}
                                to="/auth/login"
                                sx={{
                                    textDecoration: 'none',
                                    fontWeight: 500,
                                }}
                            >
                                Sign in here
                            </MuiLink>
                        </Typography>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
};

export default RegisterForm;