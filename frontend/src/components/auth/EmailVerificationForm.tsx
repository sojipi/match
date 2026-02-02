import React, { useState, useEffect } from 'react';
import {
    Card,
    CardContent,
    Typography,
    Button,
    Alert,
    CircularProgress,
} from '@mui/material';
import {
    Email,
    CheckCircle,
    Error as ErrorIcon,
    Refresh,
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../hooks/redux';
import { loginSuccess } from '../../store/slices/authSlice';

const EmailVerificationForm: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useAppDispatch();
    const [searchParams] = useSearchParams();
    const { user } = useAppSelector(state => state.auth);

    const [verificationStatus, setVerificationStatus] = useState<'pending' | 'success' | 'error' | 'expired'>('pending');
    const [isResending, setIsResending] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [countdown, setCountdown] = useState(0);

    const token = searchParams.get('token');
    const email = searchParams.get('email') || user?.email;

    useEffect(() => {
        if (token) {
            verifyEmail(token);
        }
    }, [token]);

    useEffect(() => {
        let timer: NodeJS.Timeout;
        if (countdown > 0) {
            timer = setTimeout(() => setCountdown(countdown - 1), 1000);
        }
        return () => clearTimeout(timer);
    }, [countdown]);

    const verifyEmail = async (verificationToken: string) => {
        try {
            const response = await fetch('/api/v1/auth/verify-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: verificationToken }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                if (response.status === 410) {
                    setVerificationStatus('expired');
                } else {
                    throw new Error(errorData.message || 'Verification failed');
                }
                return;
            }

            const result = await response.json();

            // Update user state if verification successful
            if (result.user) {
                dispatch(loginSuccess({
                    user: result.user,
                    token: result.token || localStorage.getItem('token') || '',
                }));
            }

            setVerificationStatus('success');

            // Redirect to dashboard after a short delay
            setTimeout(() => {
                navigate('/dashboard', { replace: true });
            }, 2000);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Verification failed';
            setError(errorMessage);
            setVerificationStatus('error');
        }
    };

    const resendVerificationEmail = async () => {
        if (!email || countdown > 0) return;

        try {
            setIsResending(true);
            setError(null);

            const response = await fetch('/api/v1/auth/resend-verification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to resend verification email');
            }

            setCountdown(60); // 60 second cooldown
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to resend email';
            setError(errorMessage);
        } finally {
            setIsResending(false);
        }
    };

    const renderContent = () => {
        switch (verificationStatus) {
            case 'pending':
                return (
                    <>
                        <CircularProgress sx={{ fontSize: 64, mb: 2 }} />
                        <Typography
                            variant="h5"
                            component="h1"
                            gutterBottom
                            sx={{ fontWeight: 600 }}
                        >
                            Verifying Your Email
                        </Typography>
                        <Typography variant="body1" color="text.secondary">
                            Please wait while we verify your email address...
                        </Typography>
                    </>
                );

            case 'success':
                return (
                    <>
                        <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                        <Typography
                            variant="h5"
                            component="h1"
                            gutterBottom
                            sx={{ fontWeight: 600 }}
                        >
                            Email Verified!
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                            Your email has been successfully verified. You'll be redirected to your dashboard shortly.
                        </Typography>
                        <Button
                            variant="contained"
                            onClick={() => navigate('/dashboard')}
                            sx={{ mt: 2 }}
                        >
                            Go to Dashboard
                        </Button>
                    </>
                );

            case 'error':
                return (
                    <>
                        <ErrorIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
                        <Typography
                            variant="h5"
                            component="h1"
                            gutterBottom
                            sx={{ fontWeight: 600 }}
                        >
                            Verification Failed
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                            {error || 'We couldn\'t verify your email address. The link may be invalid or expired.'}
                        </Typography>
                        {email && (
                            <Button
                                variant="contained"
                                onClick={resendVerificationEmail}
                                disabled={isResending || countdown > 0}
                                startIcon={isResending ? <CircularProgress size={20} /> : <Refresh />}
                                sx={{ mt: 2 }}
                            >
                                {countdown > 0
                                    ? `Resend in ${countdown}s`
                                    : isResending
                                        ? 'Sending...'
                                        : 'Resend Verification Email'
                                }
                            </Button>
                        )}
                    </>
                );

            case 'expired':
                return (
                    <>
                        <ErrorIcon sx={{ fontSize: 64, color: 'warning.main', mb: 2 }} />
                        <Typography
                            variant="h5"
                            component="h1"
                            gutterBottom
                            sx={{ fontWeight: 600 }}
                        >
                            Link Expired
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                            This verification link has expired. Please request a new one.
                        </Typography>
                        {email && (
                            <Button
                                variant="contained"
                                onClick={resendVerificationEmail}
                                disabled={isResending || countdown > 0}
                                startIcon={isResending ? <CircularProgress size={20} /> : <Email />}
                                sx={{ mt: 2 }}
                            >
                                {countdown > 0
                                    ? `Resend in ${countdown}s`
                                    : isResending
                                        ? 'Sending...'
                                        : 'Send New Verification Email'
                                }
                            </Button>
                        )}
                    </>
                );

            default:
                return (
                    <>
                        <Email sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                        <Typography
                            variant="h5"
                            component="h1"
                            gutterBottom
                            sx={{ fontWeight: 600 }}
                        >
                            Verify Your Email
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                            We've sent a verification link to <strong>{email}</strong>.
                            Please check your email and click the link to verify your account.
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                            Didn't receive the email? Check your spam folder or request a new one.
                        </Typography>
                        <Button
                            variant="outlined"
                            onClick={resendVerificationEmail}
                            disabled={isResending || countdown > 0 || !email}
                            startIcon={isResending ? <CircularProgress size={20} /> : <Refresh />}
                            fullWidth
                        >
                            {countdown > 0
                                ? `Resend in ${countdown}s`
                                : isResending
                                    ? 'Sending...'
                                    : 'Resend Verification Email'
                            }
                        </Button>
                    </>
                );
        }
    };

    return (
        <Card sx={{ width: '100%', maxWidth: 400, mx: 'auto' }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
                {error && verificationStatus !== 'error' && (
                    <Alert
                        severity="error"
                        sx={{ mb: 3, textAlign: 'left' }}
                        onClose={() => setError(null)}
                    >
                        {error}
                    </Alert>
                )}

                {renderContent()}
            </CardContent>
        </Card>
    );
};

export default EmailVerificationForm;