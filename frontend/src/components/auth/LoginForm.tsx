import React from 'react';
import { Box, Card, CardContent, Typography, TextField, Button } from '@mui/material';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';

interface LoginFormData {
    email: string;
    password: string;
}

const LoginForm: React.FC = () => {
    const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>();

    const onSubmit = (data: LoginFormData) => {
        console.log('Login data:', data);
        // TODO: Implement login logic
    };

    return (
        <Card sx={{ width: '100%', maxWidth: 400 }}>
            <CardContent>
                <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
                    Sign In
                </Typography>
                <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
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
                        {...register('password', { required: 'Password is required' })}
                        margin="normal"
                        fullWidth
                        label="Password"
                        type="password"
                        autoComplete="current-password"
                        error={!!errors.password}
                        helperText={errors.password?.message}
                    />
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Sign In
                    </Button>
                    <Box textAlign="center">
                        <Link to="/auth/register">
                            Don't have an account? Sign Up
                        </Link>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
};

export default LoginForm;