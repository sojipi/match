import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Switch,
    FormControlLabel,
    FormGroup,
    Divider,
    Button,
    Alert,
    CircularProgress,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Grid
} from '@mui/material';
import {
    Notifications,
    Email,
    PhoneIphone,
    Schedule
} from '@mui/icons-material';
import { api } from '../../utils/api';

interface NotificationPreferences {
    in_app_enabled: boolean;
    email_enabled: boolean;
    push_enabled: boolean;
    match_notifications: boolean;
    message_notifications: boolean;
    like_notifications: boolean;
    profile_view_notifications: boolean;
    system_notifications: boolean;
    quiet_hours_start: string | null;
    quiet_hours_end: string | null;
    timezone: string;
    email_digest_frequency: string;
}

const NotificationPreferences: React.FC = () => {
    const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [pushSupported, setPushSupported] = useState(false);

    useEffect(() => {
        loadPreferences();
        checkPushSupport();
    }, []);

    const checkPushSupport = () => {
        const supported = 'serviceWorker' in navigator && 'PushManager' in window;
        setPushSupported(supported);
    };

    const loadPreferences = async () => {
        try {
            setLoading(true);
            setError(null);

            const data = await api.get('/api/v1/notifications/preferences');
            setPreferences(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load notification preferences');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!preferences) return;

        try {
            setSaving(true);
            setError(null);
            setSuccess(false);

            await api.put('/api/v1/notifications/preferences', preferences);
            setSuccess(true);

            // Hide success message after 3 seconds
            setTimeout(() => setSuccess(false), 3000);
        } catch (err: any) {
            setError(err.message || 'Failed to save notification preferences');
        } finally {
            setSaving(false);
        }
    };

    const handleToggle = (field: keyof NotificationPreferences) => {
        if (!preferences) return;

        setPreferences({
            ...preferences,
            [field]: !preferences[field]
        });
    };

    const handleChange = (field: keyof NotificationPreferences, value: any) => {
        if (!preferences) return;

        setPreferences({
            ...preferences,
            [field]: value
        });
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
                <CircularProgress />
            </Box>
        );
    }

    if (!preferences) {
        return (
            <Alert severity="error">
                Failed to load notification preferences
            </Alert>
        );
    }

    return (
        <Box>
            <Typography variant="h5" gutterBottom>
                Notification Preferences
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
                Manage how and when you receive notifications
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {success && (
                <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(false)}>
                    Notification preferences saved successfully!
                </Alert>
            )}

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                        <Notifications sx={{ mr: 1 }} />
                        <Typography variant="h6">
                            Notification Channels
                        </Typography>
                    </Box>

                    <FormGroup>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.in_app_enabled}
                                    onChange={() => handleToggle('in_app_enabled')}
                                />
                            }
                            label="In-App Notifications"
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
                            Show notifications within the app
                        </Typography>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.email_enabled}
                                    onChange={() => handleToggle('email_enabled')}
                                />
                            }
                            label={
                                <Box display="flex" alignItems="center">
                                    <Email sx={{ mr: 1, fontSize: 20 }} />
                                    Email Notifications
                                </Box>
                            }
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
                            Receive notifications via email
                        </Typography>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.push_enabled}
                                    onChange={() => handleToggle('push_enabled')}
                                    disabled={!pushSupported}
                                />
                            }
                            label={
                                <Box display="flex" alignItems="center">
                                    <PhoneIphone sx={{ mr: 1, fontSize: 20 }} />
                                    Push Notifications
                                    {!pushSupported && (
                                        <Typography variant="caption" color="error" sx={{ ml: 1 }}>
                                            (Not supported)
                                        </Typography>
                                    )}
                                </Box>
                            }
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
                            Receive push notifications on your device
                        </Typography>
                    </FormGroup>
                </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Notification Types
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                        Choose which types of notifications you want to receive
                    </Typography>

                    <FormGroup>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.match_notifications}
                                    onChange={() => handleToggle('match_notifications')}
                                />
                            }
                            label="Match Notifications"
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
                            Get notified when you have new matches
                        </Typography>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.message_notifications}
                                    onChange={() => handleToggle('message_notifications')}
                                />
                            }
                            label="Message Notifications"
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
                            Get notified when you receive messages
                        </Typography>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.like_notifications}
                                    onChange={() => handleToggle('like_notifications')}
                                />
                            }
                            label="Like Notifications"
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
                            Get notified when someone likes your profile
                        </Typography>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.profile_view_notifications}
                                    onChange={() => handleToggle('profile_view_notifications')}
                                />
                            }
                            label="Profile View Notifications"
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
                            Get notified when someone views your profile
                        </Typography>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.system_notifications}
                                    onChange={() => handleToggle('system_notifications')}
                                />
                            }
                            label="System Notifications"
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
                            Get notified about system updates and announcements
                        </Typography>
                    </FormGroup>
                </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                        <Schedule sx={{ mr: 1 }} />
                        <Typography variant="h6">
                            Quiet Hours
                        </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" paragraph>
                        Set times when you don't want to receive notifications
                    </Typography>

                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Start Time"
                                type="time"
                                value={preferences.quiet_hours_start || ''}
                                onChange={(e) => handleChange('quiet_hours_start', e.target.value)}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="End Time"
                                type="time"
                                value={preferences.quiet_hours_end || ''}
                                onChange={(e) => handleChange('quiet_hours_end', e.target.value)}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <FormControl fullWidth>
                                <InputLabel>Timezone</InputLabel>
                                <Select
                                    value={preferences.timezone}
                                    label="Timezone"
                                    onChange={(e) => handleChange('timezone', e.target.value)}
                                >
                                    <MenuItem value="UTC">UTC</MenuItem>
                                    <MenuItem value="America/New_York">Eastern Time</MenuItem>
                                    <MenuItem value="America/Chicago">Central Time</MenuItem>
                                    <MenuItem value="America/Denver">Mountain Time</MenuItem>
                                    <MenuItem value="America/Los_Angeles">Pacific Time</MenuItem>
                                    <MenuItem value="Europe/London">London</MenuItem>
                                    <MenuItem value="Europe/Paris">Paris</MenuItem>
                                    <MenuItem value="Asia/Tokyo">Tokyo</MenuItem>
                                    <MenuItem value="Asia/Shanghai">Shanghai</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Email Digest
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                        Receive a summary of your notifications via email
                    </Typography>

                    <FormControl fullWidth>
                        <InputLabel>Digest Frequency</InputLabel>
                        <Select
                            value={preferences.email_digest_frequency}
                            label="Digest Frequency"
                            onChange={(e) => handleChange('email_digest_frequency', e.target.value)}
                        >
                            <MenuItem value="none">Never</MenuItem>
                            <MenuItem value="daily">Daily</MenuItem>
                            <MenuItem value="weekly">Weekly</MenuItem>
                        </Select>
                    </FormControl>
                </CardContent>
            </Card>

            <Box display="flex" justifyContent="flex-end" gap={2}>
                <Button
                    variant="outlined"
                    onClick={loadPreferences}
                    disabled={saving}
                >
                    Reset
                </Button>
                <Button
                    variant="contained"
                    onClick={handleSave}
                    disabled={saving}
                >
                    {saving ? <CircularProgress size={24} /> : 'Save Preferences'}
                </Button>
            </Box>
        </Box>
    );
};

export default NotificationPreferences;
