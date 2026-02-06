/**
 * Settings Page - User settings and configuration
 */
import React, { useState, useEffect } from 'react';
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
    IconButton,
    InputAdornment,
    Link
} from '@mui/material';
import {
    Save,
    Visibility,
    VisibilityOff,
    Info
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
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
            id={`settings-tabpanel-${index}`}
            aria-labelledby={`settings-tab-${index}`}
            {...other}
        >
            {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
        </div>
    );
}

const SettingsPage: React.FC = () => {
    const navigate = useNavigate();
    const [tabValue, setTabValue] = useState(0);
    const [geminiApiKey, setGeminiApiKey] = useState('');
    const [showApiKey, setShowApiKey] = useState(false);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            const response = await api.get('/users/settings');
            if (response.data.gemini_api_key) {
                setGeminiApiKey(response.data.gemini_api_key);
            }
        } catch (err) {
            console.error('Failed to load settings:', err);
        }
    };

    const handleSaveApiKey = async () => {
        setLoading(true);
        setError('');
        setSuccess(false);

        try {
            await api.put('/users/settings', {
                gemini_api_key: geminiApiKey
            });
            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save settings. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            <Paper elevation={3}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange}>
                        <Tab label="API Configuration" />
                        <Tab label="Notifications" />
                        <Tab label="Privacy" />
                    </Tabs>
                </Box>

                <TabPanel value={tabValue} index={0}>
                    <Typography variant="h5" gutterBottom>
                        Gemini API Configuration
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <Alert severity="info" sx={{ mb: 3 }}>
                        <Typography variant="body2">
                            Configure your own Gemini API Key to avoid system quota limits and enjoy uninterrupted AI conversation services.
                        </Typography>
                    </Alert>

                    <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle2" gutterBottom>
                            How to get a Gemini API Key?
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            1. Visit{' '}
                            <Link
                                href="https://ai.google.dev/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Google AI Studio
                            </Link>
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            2. Sign in with your Google account
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            3. Click "Get API Key" to create a new API Key
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            4. Copy the API Key and paste it in the field below
                        </Typography>
                    </Box>

                    <TextField
                        fullWidth
                        label="Gemini API Key"
                        value={geminiApiKey}
                        onChange={(e) => setGeminiApiKey(e.target.value)}
                        type={showApiKey ? 'text' : 'password'}
                        placeholder="AIza..."
                        helperText="Your API Key will be securely encrypted and stored"
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton
                                        onClick={() => setShowApiKey(!showApiKey)}
                                        edge="end"
                                    >
                                        {showApiKey ? <VisibilityOff /> : <Visibility />}
                                    </IconButton>
                                </InputAdornment>
                            ),
                        }}
                        sx={{ mb: 2 }}
                    />

                    {success && (
                        <Alert severity="success" sx={{ mb: 2 }}>
                            API Key saved successfully!
                        </Alert>
                    )}

                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                            variant="contained"
                            startIcon={<Save />}
                            onClick={handleSaveApiKey}
                            disabled={loading || !geminiApiKey}
                        >
                            {loading ? 'Saving...' : 'Save Settings'}
                        </Button>
                        <Button
                            variant="outlined"
                            onClick={() => navigate(-1)}
                        >
                            Back
                        </Button>
                    </Box>

                    <Alert severity="warning" icon={<Info />} sx={{ mt: 3 }}>
                        <Typography variant="body2">
                            <strong>Important:</strong> Keep your API Key secure and do not share it with others.
                            If you suspect your API Key has been compromised, revoke it immediately in Google AI Studio and generate a new one.
                        </Typography>
                    </Alert>
                </TabPanel>

                <TabPanel value={tabValue} index={1}>
                    <Typography variant="h5" gutterBottom>
                        Notification Settings
                    </Typography>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                        Notification settings coming soon...
                    </Typography>
                </TabPanel>

                <TabPanel value={tabValue} index={2}>
                    <Typography variant="h5" gutterBottom>
                        Privacy Settings
                    </Typography>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                        Privacy settings coming soon...
                    </Typography>
                </TabPanel>
            </Paper>
        </Container>
    );
};

export default SettingsPage;