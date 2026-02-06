import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Paper,
    Typography,
    Box,
    TextField,
    Button,
    Alert,
    Tabs,
    Tab,
    Divider,
    Grid,
    Card,
    CardContent,
    CardMedia,
    IconButton,
    Switch,
    FormControlLabel,
    FormGroup,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Chip,
    Stack,
    LinearProgress,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import {
    Save,
    PhotoCamera,
    Delete,
    Star,
    StarBorder,
    Verified,
    Lock,
    Notifications,
    CardMembership,
    ArrowBack
} from '@mui/icons-material';
import { useAppSelector } from '../hooks/redux';
import api from '../services/api';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`profile-tabpanel-${index}`}
            aria-labelledby={`profile-tab-${index}`}
            {...other}
        >
            {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
        </div>
    );
}

interface Photo {
    id: string;
    file_url: string;
    is_primary: boolean;
    order_index: number;
    uploaded_at: string;
}

interface UserProfile {
    id: string;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    bio: string | null;
    location: string | null;
    date_of_birth: string | null;
    gender: string | null;
    photos: Photo[];
    profile_completeness: number;
    is_verified: boolean;
    subscription_tier: string;
}

interface PrivacySettings {
    profile_visibility: string;
    show_age: boolean;
    show_location: boolean;
    show_last_active: boolean;
    allow_messages_from: string;
    show_in_discovery: boolean;
}

interface NotificationPreferences {
    email_matches: boolean;
    email_messages: boolean;
    email_reports: boolean;
    push_matches: boolean;
    push_messages: boolean;
    push_sessions: boolean;
}

const ProfileManagementPage: React.FC = () => {
    const navigate = useNavigate();
    const { user } = useAppSelector(state => state.auth);
    const [tabValue, setTabValue] = useState(0);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    // Profile data
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [bio, setBio] = useState('');
    const [location, setLocation] = useState('');
    const [gender, setGender] = useState('');

    // Privacy settings
    const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
        profile_visibility: 'public',
        show_age: true,
        show_location: true,
        show_last_active: true,
        allow_messages_from: 'matches',
        show_in_discovery: true
    });

    // Notification preferences
    const [notificationPrefs, setNotificationPrefs] = useState<NotificationPreferences>({
        email_matches: true,
        email_messages: true,
        email_reports: true,
        push_matches: true,
        push_messages: true,
        push_sessions: true
    });

    // Photo upload
    const [uploadingPhoto, setUploadingPhoto] = useState(false);
    const [verificationDialog, setVerificationDialog] = useState(false);

    useEffect(() => {
        loadProfile();
        loadPrivacySettings();
        loadNotificationPreferences();
    }, []);

    const loadProfile = async () => {
        try {
            const response = await api.get('/api/v1/users/profile');
            // The response from api.get() is already the data, not wrapped in .data
            const profileData = response;

            // Check if we got valid data
            if (!profileData || !profileData.id) {
                console.error('Invalid profile data received:', profileData);
                setError('Failed to load profile data - invalid response');
                return;
            }

            setProfile(profileData);
            setFirstName(profileData.first_name || '');
            setLastName(profileData.last_name || '');
            setBio(profileData.bio || '');
            setLocation(profileData.location || '');
            setGender(profileData.gender || '');
        } catch (err: any) {
            console.error('Failed to load profile:', err);
            console.error('Error response:', err.response);
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to load profile';
            setError(errorMessage);
        }
    };

    const loadPrivacySettings = async () => {
        try {
            const response = await api.get('/api/v1/users/privacy');
            setPrivacySettings(response);
        } catch (err) {
            console.error('Failed to load privacy settings:', err);
        }
    };

    const loadNotificationPreferences = async () => {
        try {
            const response = await api.get('/api/v1/users/notifications/preferences');
            setNotificationPrefs(response);
        } catch (err) {
            console.error('Failed to load notification preferences:', err);
        }
    };

    const handleSaveProfile = async () => {
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            await api.put('/api/v1/users/profile', {
                first_name: firstName,
                last_name: lastName,
                bio: bio,
                location: location,
                gender: gender
            });
            setSuccess('Profile updated successfully!');
            await loadProfile();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    const handlePhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setUploadingPhoto(true);
        setError('');

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('is_primary', profile?.photos.length === 0 ? 'true' : 'false');

            await api.post('/api/v1/users/photos/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setSuccess('Photo uploaded successfully!');
            await loadProfile();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to upload photo');
        } finally {
            setUploadingPhoto(false);
        }
    };

    const handleDeletePhoto = async (photoId: string) => {
        try {
            await api.delete(`/api/v1/users/photos/${photoId}`);
            setSuccess('Photo deleted successfully!');
            await loadProfile();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete photo');
        }
    };

    const handleSetPrimaryPhoto = async (photoId: string) => {
        try {
            await api.put(`/api/v1/users/photos/${photoId}/primary`);
            setSuccess('Primary photo updated!');
            await loadProfile();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to set primary photo');
        }
    };

    const handleSavePrivacySettings = async () => {
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            await api.put('/api/v1/users/privacy', privacySettings);
            setSuccess('Privacy settings updated successfully!');
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to update privacy settings');
        } finally {
            setLoading(false);
        }
    };

    const handleSaveNotificationPreferences = async () => {
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            await api.put('/api/v1/users/notifications/preferences', notificationPrefs);
            setSuccess('Notification preferences updated successfully!');
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to update notification preferences');
        } finally {
            setLoading(false);
        }
    };

    const handleRequestVerification = async () => {
        try {
            await api.post('/api/v1/users/verify/request');
            setSuccess('Verification request submitted! You will be notified once reviewed.');
            setVerificationDialog(false);
            setTimeout(() => setSuccess(''), 5000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to request verification');
        }
    };

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
        setError('');
        setSuccess('');
    };

    if (!profile) {
        return (
            <Container maxWidth="md" sx={{ py: 4 }}>
                <LinearProgress />
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Box display="flex" alignItems="center" mb={3}>
                <IconButton onClick={() => navigate(-1)} sx={{ mr: 2 }}>
                    <ArrowBack />
                </IconButton>
                <Typography variant="h4" component="h1">
                    Profile Management
                </Typography>
            </Box>

            {/* Profile Completeness */}
            <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                    <Typography variant="subtitle1">
                        Profile Completeness
                    </Typography>
                    <Typography variant="h6" color="primary">
                        {Math.round(profile.profile_completeness * 100)}%
                    </Typography>
                </Box>
                <LinearProgress
                    variant="determinate"
                    value={profile.profile_completeness * 100}
                    sx={{ height: 8, borderRadius: 4 }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Complete your profile to improve match quality and visibility
                </Typography>
            </Paper>

            {success && (
                <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
                    {success}
                </Alert>
            )}

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            <Paper elevation={3}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange}>
                        <Tab label="Basic Info" />
                        <Tab label="Photos" />
                        <Tab label="Privacy" />
                        <Tab label="Notifications" />
                        <Tab label="Verification" />
                    </Tabs>
                </Box>

                {/* Basic Info Tab */}
                <TabPanel value={tabValue} index={0}>
                    <Typography variant="h5" gutterBottom>
                        Basic Information
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <Grid container spacing={3}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="First Name"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Last Name"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                required
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Bio"
                                value={bio}
                                onChange={(e) => setBio(e.target.value)}
                                multiline
                                rows={4}
                                helperText={`${bio.length}/500 characters`}
                                inputProps={{ maxLength: 500 }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Location"
                                value={location}
                                onChange={(e) => setLocation(e.target.value)}
                                placeholder="City, State"
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel>Gender</InputLabel>
                                <Select
                                    value={gender}
                                    onChange={(e) => setGender(e.target.value)}
                                    label="Gender"
                                >
                                    <MenuItem value="">Prefer not to say</MenuItem>
                                    <MenuItem value="male">Male</MenuItem>
                                    <MenuItem value="female">Female</MenuItem>
                                    <MenuItem value="non-binary">Non-binary</MenuItem>
                                    <MenuItem value="other">Other</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                    </Grid>

                    <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                        <Button
                            variant="contained"
                            startIcon={<Save />}
                            onClick={handleSaveProfile}
                            disabled={loading}
                        >
                            {loading ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </Box>
                </TabPanel>

                {/* Photos Tab */}
                <TabPanel value={tabValue} index={1}>
                    <Typography variant="h5" gutterBottom>
                        Profile Photos
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <Alert severity="info" sx={{ mb: 3 }}>
                        Add up to 6 photos. Your primary photo will be shown in match discovery.
                    </Alert>

                    <Grid container spacing={2}>
                        {profile.photos.map((photo) => (
                            <Grid item xs={12} sm={6} md={4} key={photo.id}>
                                <Card>
                                    <CardMedia
                                        component="img"
                                        height="200"
                                        image={photo.file_url}
                                        alt="Profile photo"
                                    />
                                    <CardContent>
                                        <Box display="flex" justifyContent="space-between" alignItems="center">
                                            <IconButton
                                                onClick={() => handleSetPrimaryPhoto(photo.id)}
                                                color={photo.is_primary ? 'primary' : 'default'}
                                            >
                                                {photo.is_primary ? <Star /> : <StarBorder />}
                                            </IconButton>
                                            {photo.is_primary && (
                                                <Chip label="Primary" size="small" color="primary" />
                                            )}
                                            <IconButton
                                                onClick={() => handleDeletePhoto(photo.id)}
                                                color="error"
                                            >
                                                <Delete />
                                            </IconButton>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}

                        {profile.photos.length < 6 && (
                            <Grid item xs={12} sm={6} md={4}>
                                <Card
                                    sx={{
                                        height: 200,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        cursor: 'pointer',
                                        border: '2px dashed',
                                        borderColor: 'divider',
                                        '&:hover': { borderColor: 'primary.main' }
                                    }}
                                    component="label"
                                >
                                    <input
                                        type="file"
                                        hidden
                                        accept="image/*"
                                        onChange={handlePhotoUpload}
                                        disabled={uploadingPhoto}
                                    />
                                    <Box textAlign="center">
                                        <PhotoCamera sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                                        <Typography variant="body2" color="text.secondary">
                                            {uploadingPhoto ? 'Uploading...' : 'Add Photo'}
                                        </Typography>
                                    </Box>
                                </Card>
                            </Grid>
                        )}
                    </Grid>
                </TabPanel>

                {/* Privacy Tab */}
                <TabPanel value={tabValue} index={2}>
                    <Typography variant="h5" gutterBottom>
                        Privacy Settings
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <FormGroup>
                        <Box mb={3}>
                            <FormControl fullWidth sx={{ mb: 2 }}>
                                <InputLabel>Profile Visibility</InputLabel>
                                <Select
                                    value={privacySettings.profile_visibility}
                                    onChange={(e) => setPrivacySettings({
                                        ...privacySettings,
                                        profile_visibility: e.target.value
                                    })}
                                    label="Profile Visibility"
                                >
                                    <MenuItem value="public">Public - Visible to everyone</MenuItem>
                                    <MenuItem value="friends">Friends - Visible to matches only</MenuItem>
                                    <MenuItem value="private">Private - Hidden from discovery</MenuItem>
                                </Select>
                            </FormControl>

                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={privacySettings.show_age}
                                        onChange={(e) => setPrivacySettings({
                                            ...privacySettings,
                                            show_age: e.target.checked
                                        })}
                                    />
                                }
                                label="Show my age on profile"
                            />

                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={privacySettings.show_location}
                                        onChange={(e) => setPrivacySettings({
                                            ...privacySettings,
                                            show_location: e.target.checked
                                        })}
                                    />
                                }
                                label="Show my location"
                            />

                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={privacySettings.show_last_active}
                                        onChange={(e) => setPrivacySettings({
                                            ...privacySettings,
                                            show_last_active: e.target.checked
                                        })}
                                    />
                                }
                                label="Show when I was last active"
                            />

                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={privacySettings.show_in_discovery}
                                        onChange={(e) => setPrivacySettings({
                                            ...privacySettings,
                                            show_in_discovery: e.target.checked
                                        })}
                                    />
                                }
                                label="Show my profile in match discovery"
                            />

                            <FormControl fullWidth sx={{ mt: 2 }}>
                                <InputLabel>Allow Messages From</InputLabel>
                                <Select
                                    value={privacySettings.allow_messages_from}
                                    onChange={(e) => setPrivacySettings({
                                        ...privacySettings,
                                        allow_messages_from: e.target.value
                                    })}
                                    label="Allow Messages From"
                                >
                                    <MenuItem value="everyone">Everyone</MenuItem>
                                    <MenuItem value="matches">Matches only</MenuItem>
                                    <MenuItem value="none">No one</MenuItem>
                                </Select>
                            </FormControl>
                        </Box>
                    </FormGroup>

                    <Button
                        variant="contained"
                        startIcon={<Lock />}
                        onClick={handleSavePrivacySettings}
                        disabled={loading}
                    >
                        {loading ? 'Saving...' : 'Save Privacy Settings'}
                    </Button>
                </TabPanel>

                {/* Notifications Tab */}
                <TabPanel value={tabValue} index={3}>
                    <Typography variant="h5" gutterBottom>
                        Notification Preferences
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <FormGroup>
                        <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                            Email Notifications
                        </Typography>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={notificationPrefs.email_matches}
                                    onChange={(e) => setNotificationPrefs({
                                        ...notificationPrefs,
                                        email_matches: e.target.checked
                                    })}
                                />
                            }
                            label="New matches"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={notificationPrefs.email_messages}
                                    onChange={(e) => setNotificationPrefs({
                                        ...notificationPrefs,
                                        email_messages: e.target.checked
                                    })}
                                />
                            }
                            label="New messages"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={notificationPrefs.email_reports}
                                    onChange={(e) => setNotificationPrefs({
                                        ...notificationPrefs,
                                        email_reports: e.target.checked
                                    })}
                                />
                            }
                            label="Compatibility reports"
                        />

                        <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
                            Push Notifications
                        </Typography>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={notificationPrefs.push_matches}
                                    onChange={(e) => setNotificationPrefs({
                                        ...notificationPrefs,
                                        push_matches: e.target.checked
                                    })}
                                />
                            }
                            label="New matches"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={notificationPrefs.push_messages}
                                    onChange={(e) => setNotificationPrefs({
                                        ...notificationPrefs,
                                        push_messages: e.target.checked
                                    })}
                                />
                            }
                            label="New messages"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={notificationPrefs.push_sessions}
                                    onChange={(e) => setNotificationPrefs({
                                        ...notificationPrefs,
                                        push_sessions: e.target.checked
                                    })}
                                />
                            }
                            label="AI session updates"
                        />
                    </FormGroup>

                    <Button
                        variant="contained"
                        startIcon={<Notifications />}
                        onClick={handleSaveNotificationPreferences}
                        disabled={loading}
                        sx={{ mt: 3 }}
                    >
                        {loading ? 'Saving...' : 'Save Notification Preferences'}
                    </Button>
                </TabPanel>

                {/* Verification Tab */}
                <TabPanel value={tabValue} index={4}>
                    <Typography variant="h5" gutterBottom>
                        Profile Verification
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    {profile.is_verified ? (
                        <Alert severity="success" icon={<Verified />}>
                            <Typography variant="subtitle1" gutterBottom>
                                Your profile is verified!
                            </Typography>
                            <Typography variant="body2">
                                Verified profiles get more visibility and trust from other users.
                            </Typography>
                        </Alert>
                    ) : (
                        <Box>
                            <Alert severity="info" sx={{ mb: 3 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                    Why verify your profile?
                                </Typography>
                                <Typography variant="body2" component="div">
                                    <ul>
                                        <li>Increase trust with potential matches</li>
                                        <li>Get priority in match discovery</li>
                                        <li>Stand out with a verified badge</li>
                                        <li>Access to premium features</li>
                                    </ul>
                                </Typography>
                            </Alert>

                            <Button
                                variant="contained"
                                startIcon={<Verified />}
                                onClick={() => setVerificationDialog(true)}
                                size="large"
                            >
                                Request Verification
                            </Button>
                        </Box>
                    )}

                    <Divider sx={{ my: 4 }} />

                    <Typography variant="h6" gutterBottom>
                        Subscription
                    </Typography>
                    <Card sx={{ mt: 2 }}>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography variant="h6">
                                        {profile.subscription_tier.charAt(0).toUpperCase() + profile.subscription_tier.slice(1)} Plan
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {profile.subscription_tier === 'free' && 'Basic features included'}
                                        {profile.subscription_tier === 'premium' && 'Unlimited matching and AI sessions'}
                                        {profile.subscription_tier === 'pro' && 'All features + advanced analytics'}
                                    </Typography>
                                </Box>
                                <CardMembership color="primary" sx={{ fontSize: 40 }} />
                            </Box>
                            {profile.subscription_tier === 'free' && (
                                <Button
                                    variant="outlined"
                                    sx={{ mt: 2 }}
                                    onClick={() => navigate('/subscription')}
                                >
                                    Upgrade Plan
                                </Button>
                            )}
                        </CardContent>
                    </Card>
                </TabPanel>
            </Paper>

            {/* Verification Dialog */}
            <Dialog open={verificationDialog} onClose={() => setVerificationDialog(false)}>
                <DialogTitle>Request Profile Verification</DialogTitle>
                <DialogContent>
                    <Typography variant="body2" paragraph>
                        To verify your profile, we'll need to review your account and photos.
                        This process typically takes 24-48 hours.
                    </Typography>
                    <Typography variant="body2" paragraph>
                        Make sure you have:
                    </Typography>
                    <Typography variant="body2" component="div">
                        <ul>
                            <li>At least one clear photo of yourself</li>
                            <li>Completed your personality assessment</li>
                            <li>Filled out your bio and basic information</li>
                        </ul>
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setVerificationDialog(false)}>Cancel</Button>
                    <Button onClick={handleRequestVerification} variant="contained">
                        Submit Request
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default ProfileManagementPage;
