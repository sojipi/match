import React, { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Alert,
    Avatar,
    IconButton,
    Grid,
    Divider,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    CircularProgress,
} from '@mui/material';
import {
    PhotoCamera,
    Save,
    Cancel,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAppSelector, useAppDispatch } from '../../hooks/redux';
import { loginSuccess } from '../../store/slices/authSlice';

// Validation schema
const profileSchema = z.object({
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
    bio: z
        .string()
        .max(500, 'Bio must be less than 500 characters')
        .optional(),
    location: z
        .string()
        .max(100, 'Location must be less than 100 characters')
        .optional(),
    dateOfBirth: z
        .string()
        .optional(),
    gender: z
        .string()
        .optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

interface UserProfileFormProps {
    onCancel?: () => void;
    onSave?: () => void;
}

const UserProfileForm: React.FC<UserProfileFormProps> = ({ onCancel, onSave }) => {
    const dispatch = useAppDispatch();
    const { user } = useAppSelector(state => state.auth);

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [avatarFile, setAvatarFile] = useState<File | null>(null);
    const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isDirty },
        reset,
    } = useForm<ProfileFormData>({
        resolver: zodResolver(profileSchema),
        defaultValues: {
            firstName: user?.first_name || '',
            lastName: user?.last_name || '',
            email: user?.email || '',
            bio: '', // TODO: Add bio to user state
            location: '', // TODO: Add location to user state
            dateOfBirth: '', // TODO: Add dateOfBirth to user state
            gender: '', // TODO: Add gender to user state
        },
        mode: 'onBlur',
    });

    const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            // Validate file type and size
            if (!file.type.startsWith('image/')) {
                setError('Please select a valid image file');
                return;
            }

            if (file.size > 5 * 1024 * 1024) { // 5MB limit
                setError('Image file must be less than 5MB');
                return;
            }

            setAvatarFile(file);

            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => {
                setAvatarPreview(e.target?.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const onSubmit = async (data: ProfileFormData) => {
        try {
            setIsLoading(true);
            setError(null);
            setSuccess(null);

            // Create FormData for file upload
            const formData = new FormData();
            Object.entries(data).forEach(([key, value]) => {
                if (value) formData.append(key, value);
            });

            if (avatarFile) {
                formData.append('avatar', avatarFile);
            }

            // TODO: Replace with actual API call
            const response = await fetch('/api/v1/users/profile', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to update profile');
            }

            const result = await response.json();

            // Update user state
            dispatch(loginSuccess({
                user: result.user,
                token: localStorage.getItem('token') || '',
            }));

            setSuccess('Profile updated successfully!');
            onSave?.();
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to update profile';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCancel = () => {
        reset();
        setAvatarFile(null);
        setAvatarPreview(null);
        setError(null);
        setSuccess(null);
        onCancel?.();
    };

    return (
        <Card sx={{ width: '100%', maxWidth: 600, mx: 'auto' }}>
            <CardContent sx={{ p: 4 }}>
                <Typography
                    variant="h5"
                    component="h2"
                    gutterBottom
                    sx={{ fontWeight: 600, mb: 3 }}
                >
                    Edit Profile
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

                {success && (
                    <Alert
                        severity="success"
                        sx={{ mb: 3 }}
                        onClose={() => setSuccess(null)}
                    >
                        {success}
                    </Alert>
                )}

                <Box
                    component="form"
                    onSubmit={handleSubmit(onSubmit)}
                    noValidate
                >
                    {/* Avatar Section */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                        <Avatar
                            sx={{ width: 80, height: 80, mr: 2 }}
                            src={avatarPreview || '/static/images/avatar/1.jpg'}
                            alt={`${user?.first_name} ${user?.last_name}`}
                        >
                            {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                        </Avatar>
                        <Box>
                            <input
                                accept="image/*"
                                style={{ display: 'none' }}
                                id="avatar-upload"
                                type="file"
                                onChange={handleAvatarChange}
                                disabled={isLoading}
                            />
                            <label htmlFor="avatar-upload">
                                <IconButton
                                    color="primary"
                                    aria-label="upload picture"
                                    component="span"
                                    disabled={isLoading}
                                >
                                    <PhotoCamera />
                                </IconButton>
                            </label>
                            <Typography variant="body2" color="text.secondary">
                                Click to change profile picture
                            </Typography>
                        </Box>
                    </Box>

                    <Divider sx={{ mb: 3 }} />

                    {/* Basic Information */}
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                {...register('firstName')}
                                fullWidth
                                label="First Name"
                                error={!!errors.firstName}
                                helperText={errors.firstName?.message}
                                disabled={isLoading}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                {...register('lastName')}
                                fullWidth
                                label="Last Name"
                                error={!!errors.lastName}
                                helperText={errors.lastName?.message}
                                disabled={isLoading}
                            />
                        </Grid>
                    </Grid>

                    <TextField
                        {...register('email')}
                        margin="normal"
                        fullWidth
                        label="Email Address"
                        type="email"
                        error={!!errors.email}
                        helperText={errors.email?.message}
                        disabled={isLoading}
                    />

                    <TextField
                        {...register('bio')}
                        margin="normal"
                        fullWidth
                        label="Bio"
                        multiline
                        rows={3}
                        placeholder="Tell us about yourself..."
                        error={!!errors.bio}
                        helperText={errors.bio?.message || 'Maximum 500 characters'}
                        disabled={isLoading}
                    />

                    <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                {...register('location')}
                                fullWidth
                                label="Location"
                                placeholder="City, Country"
                                error={!!errors.location}
                                helperText={errors.location?.message}
                                disabled={isLoading}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                {...register('dateOfBirth')}
                                fullWidth
                                label="Date of Birth"
                                type="date"
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                error={!!errors.dateOfBirth}
                                helperText={errors.dateOfBirth?.message}
                                disabled={isLoading}
                            />
                        </Grid>
                    </Grid>

                    <FormControl fullWidth margin="normal">
                        <InputLabel>Gender</InputLabel>
                        <Select
                            {...register('gender')}
                            label="Gender"
                            disabled={isLoading}
                        >
                            <MenuItem value="">Prefer not to say</MenuItem>
                            <MenuItem value="male">Male</MenuItem>
                            <MenuItem value="female">Female</MenuItem>
                            <MenuItem value="non-binary">Non-binary</MenuItem>
                            <MenuItem value="other">Other</MenuItem>
                        </Select>
                    </FormControl>

                    {/* Action Buttons */}
                    <Box sx={{ display: 'flex', gap: 2, mt: 4, justifyContent: 'flex-end' }}>
                        <Button
                            variant="outlined"
                            onClick={handleCancel}
                            disabled={isLoading}
                            startIcon={<Cancel />}
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            variant="contained"
                            disabled={isLoading || !isDirty}
                            startIcon={isLoading ? <CircularProgress size={20} /> : <Save />}
                        >
                            {isLoading ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
};

export default UserProfileForm;