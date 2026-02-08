import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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
    const { t } = useTranslation();
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
                    {t('profile.title')}
                </Typography>
            </Box>

            {/* Profile Completeness */}
            <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                    <Typography variant="subtitle1">
                        {t('profile.completeness')}
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
                    {t('profile.completeProfile')}
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
                        <Tab label={t('profile.tabs.basicInfo')} />
                        <Tab label={t('profile.tabs.photos')} />
                        <Tab label={t('profile.tabs.privacy')} />
                        <Tab label={t('profile.tabs.notifications')} />
                        <Tab label={t('profile.tabs.verification')} />
                    </Tabs>
                </Box>

                {/* Basic Info Tab */}
                <TabPanel value={tabValue} index={0}>
                    <Typography variant="h5" gutterBottom>
                        {t('profile.basicInfo')}
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <Grid container spacing={3}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label={t('profile.firstName')}
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label={t('profile.lastName')}
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                required
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label={t('profile.bio')}
                                value={bio}
                                onChange={(e) => setBio(e.target.value)}
                                multiline
                                rows={4}
                                helperText={t('profile.characterCount', { count: bio.length })}
                                inputProps={{ maxLength: 500 }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label={t('profile.location')}
                                value={location}
                                onChange={(e) => setLocation(e.target.value)}
                                placeholder={t('profile.locationPlaceholder')}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel>{t('profile.gender')}</InputLabel>
                                <Select
                                    value={gender}
                                    onChange={(e) => setGender(e.target.value)}
                                    label={t('profile.gender')}
                                >
                                    <MenuItem value="">{t('profile.genderOptions.preferNotToSay')}</MenuItem>
                                    <MenuItem value="male">{t('profile.genderOptions.male')}</MenuItem>
                                    <MenuItem value="female">{t('profile.genderOptions.female')}</MenuItem>
                                    <MenuItem value="non-binary">{t('profile.genderOptions.nonBinary')}</MenuItem>
                                    <MenuItem value="other">{t('profile.genderOptions.other')}</MenuItem>
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
                            {loading ? t('profile.actions.saving') : t('profile.actions.saveChanges')}
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
                                        alt={t('profile.photoAlt')}
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
                                                <Chip label={t('profile.primaryPhoto')} size="small" color="primary" />
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
                                            {uploadingPhoto ? t('profile.uploading') : t('profile.addPhoto')}
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
                        {t('profile.privacy.title')}
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <FormGroup>
                        <Box mb={3}>
                            <FormControl fullWidth sx={{ mb: 2 }}>
                                <InputLabel>{t('profile.privacy.visibility')}</InputLabel>
                                <Select
                                    value={privacySettings.profile_visibility}
                                    onChange={(e) => setPrivacySettings({
                                        ...privacySettings,
                                        profile_visibility: e.target.value
                                    })}
                                    label={t('profile.privacy.visibility')}
                                >
                                    <MenuItem value="public">{t('profile.privacy.public')}</MenuItem>
                                    <MenuItem value="friends">{t('profile.privacy.friends')}</MenuItem>
                                    <MenuItem value="private">{t('profile.privacy.private')}</MenuItem>
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
                                label={t('profile.privacy.showAge')}
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
                                label={t('profile.privacy.showLocation')}
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
                                label={t('profile.privacy.showLastActive')}
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
                                label={t('profile.privacy.showInDiscovery')}
                            />

                            <FormControl fullWidth sx={{ mt: 2 }}>
                                <InputLabel>{t('profile.privacy.allowMessagesFrom')}</InputLabel>
                                <Select
                                    value={privacySettings.allow_messages_from}
                                    onChange={(e) => setPrivacySettings({
                                        ...privacySettings,
                                        allow_messages_from: e.target.value
                                    })}
                                    label={t('profile.privacy.allowMessagesFrom')}
                                >
                                    <MenuItem value="everyone">{t('profile.privacy.everyone')}</MenuItem>
                                    <MenuItem value="matches">{t('profile.privacy.matchesOnly')}</MenuItem>
                                    <MenuItem value="none">{t('profile.privacy.noOne')}</MenuItem>
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
                        {loading ? t('common.loading') : t('profile.privacy.save')}
                    </Button>
                </TabPanel>

                {/* Notifications Tab */}
                <TabPanel value={tabValue} index={3}>
                    <Typography variant="h5" gutterBottom>
                        {t('profile.notifications.title')}
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <FormGroup>
                        <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                            {t('profile.notifications.email')}
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
                            label={t('profile.notifications.newMatches')}
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
                            label={t('profile.notifications.newMessages')}
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
                            label={t('profile.notifications.reports')}
                        />

                        <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
                            {t('profile.notifications.push')}
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
                            label={t('profile.notifications.newMatches')}
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
                            label={t('profile.notifications.newMessages')}
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
                            label={t('profile.notifications.sessions')}
                        />
                    </FormGroup>

                    <Button
                        variant="contained"
                        startIcon={<Notifications />}
                        onClick={handleSaveNotificationPreferences}
                        disabled={loading}
                        sx={{ mt: 3 }}
                    >
                        {loading ? t('common.loading') : t('profile.notifications.save')}
                    </Button>
                </TabPanel>

                {/* Verification Tab */}
                <TabPanel value={tabValue} index={4}>
                    <Typography variant="h5" gutterBottom>
                        {t('profile.verification.title')}
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    {profile.is_verified ? (
                        <Alert severity="success" icon={<Verified />}>
                            <Typography variant="subtitle1" gutterBottom>
                                {t('profile.verification.verified')}
                            </Typography>
                            <Typography variant="body2">
                                {t('profile.verification.verifiedDesc')}
                            </Typography>
                        </Alert>
                    ) : (
                        <Box>
                            <Alert severity="info" sx={{ mb: 3 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                    {t('profile.verification.why')}
                                </Typography>
                                <Typography variant="body2" component="div">
                                    <ul>
                                        <li>{t('profile.verification.benefit1')}</li>
                                        <li>{t('profile.verification.benefit2')}</li>
                                        <li>{t('profile.verification.benefit3')}</li>
                                        <li>{t('profile.verification.benefit4')}</li>
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
