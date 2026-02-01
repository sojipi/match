import React from 'react';
import { Box, Card, CardContent, Typography, TextField, Button } from '@mui/material';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';

interface RegisterFormData {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
}

const RegisterForm: React.FC = () => {
    const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterFormData>();
    const password = watch('password');

    const onSubmit = (data: RegisterFormData) => {
        console.log('Register data:', data);
        // TODO: Implement registration logic
    };

    return (
        <Card sx={{ width: '100%', maxWidth: 400 }}>
            <CardContent>
                <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
                    Sign Up
                </Typography>
                <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
                    <TextField
                        {...register('firstName', { required: 'First name is required' })}
                        margin="normal"
                        fullWidth
                        label="First Name"
                        autoComplete="given-name"
                        error={!!errors.firstName}
                        helperText={errors.firstName?.message}
                    />
                    <TextField
                        {...register('lastName', { required: 'Last name is required' })}
                        margin="normal"
                        fullWidth
                        label="Last Name"
                        autoComplete="family-name"
                        error={!!errors.lastName}
                        helperText={errors.lastName?.message}
                    />
                    <TextField
                        {...register('email', {
                            required: 'Email is required',
                            pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                message: 'Invalid email address'
                            }
                        })}
                        margin="normal"
                        fullWidth
                        label="Email Address"
                        type="email"
                        autoComplete="email"
                        error={!!errors.email}
                        helperText={errors.email?.message}
                    />
                    <TextField
                        {...register('password', {
                            required: 'Password is required',
                            minLength: {
                                value: 8,
                                message: 'Password must be at least 8 characters'
                            }
                        })}
                        margin="normal"
                        fullWidth
                        label="Password"
                        type="password"
                        autoComplete="new-password"
                        error={!!errors.password}
                        helperText={errors.password?.message}
                    />
                    <TextField
                        {...register('confirmPassword', {
                            required: 'Please confirm your password',
                            validate: value => value === password || 'Passwords do not match'
                        })}
                        margin="normal"
                        fullWidth
                        label="Confirm Password"
                        type="password"
                        autoComplete="new-password"
                        error={!!errors.confirmPassword}
                        helperText={errors.confirmPassword?.message}
                    />
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Sign Up
                    </Button>
                    <Box textAlign="center">
                        <Link to="/auth/login">
                            Already have an account? Sign In
                        </Link>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
};

export default RegisterForm;