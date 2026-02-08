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
    Link,
    List,
    ListItem,
    ListItemText,
    ListItemIcon
} from '@mui/material';
import {
    Save,
    Visibility,
    VisibilityOff,
    Info,
    Person,
    Lock,
    Notifications,
    ArrowForward,
    Language
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import api from '../services/api';
import LanguageSwitcher from '../components/LanguageSwitcher';
import AccessibilitySettings from '../components/AccessibilitySettings';
import LanguageTest from '../components/LanguageTest';

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
    const { t } = useTranslation();
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
            const response = await api.get('/api/v1/users/settings');
            if (response.gemini_api_key) {
                setGeminiApiKey(response.gemini_api_key);
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
            await api.put('/api/v1/users/settings', {
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
            <Typography variant="h4" component="h1" gutterBottom>
                {t('settings.title')}
            </Typography>

            <Paper elevation={3} sx={{ mb: 3 }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange}>
                        <Tab label={t('settings.tabs.apiConfig')} />
                        <Tab label={t('settings.language') + ' & ' + t('settings.culturalPreferences')} />
                        <Tab label={t('settings.accessibility')} />
                        <Tab label={t('settings.tabs.quickLinks')} />
                    </Tabs>
                </Box>

                <TabPanel value={tabValue} index={0}>
                    <Typography variant="h5" gutterBottom>
                        {t('settings.api.title')}
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <Alert severity="info" sx={{ mb: 3 }}>
                        <Typography variant="body2">
                            {t('settings.api.description')}
                        </Typography>
                    </Alert>

                    <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle2" gutterBottom>
                            {t('settings.api.howToGet')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            1. {t('settings.api.step1')}{' '}
                            <Link
                                href="https://ai.google.dev/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Google AI Studio
                            </Link>
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            2. {t('settings.api.step2')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            3. {t('settings.api.step3')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            4. {t('settings.api.step4')}
                        </Typography>
                    </Box>

                    <TextField
                        fullWidth
                        label={t('settings.api.label')}
                        value={geminiApiKey}
                        onChange={(e) => setGeminiApiKey(e.target.value)}
                        type={showApiKey ? 'text' : 'password'}
                        placeholder="AIza..."
                        helperText={t('settings.api.helperText')}
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
                            {t('settings.api.success')}
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
                            {loading ? t('common.loading') : t('settings.api.save')}
                        </Button>
                        <Button
                            variant="outlined"
                            onClick={() => navigate(-1)}
                        >
                            {t('common.back')}
                        </Button>
                    </Box>

                    <Alert severity="warning" icon={<Info />} sx={{ mt: 3 }}>
                        <Typography variant="body2">
                            <strong>{t('settings.api.important')}:</strong> {t('settings.api.securityNote')}
                        </Typography>
                    </Alert>
                </TabPanel>

                <TabPanel value={tabValue} index={1}>
                    <Typography variant="h5" gutterBottom>
                        {t('settings.language')} & {t('settings.culturalPreferences')}
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    {/* Language Test Component */}
                    <LanguageTest />

                    <Alert severity="info" sx={{ mb: 3 }}>
                        <Typography variant="body2">
                            {t('settings.cultural.description')}
                        </Typography>
                    </Alert>

                    <Box sx={{ mb: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>
                            {t('settings.language')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {t('settings.cultural.languageDesc')}
                        </Typography>
                        <LanguageSwitcher />
                    </Box>

                    <Box sx={{ mb: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>
                            {t('settings.cultural.title')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {t('settings.cultural.adaptationDesc')}
                        </Typography>
                        <List dense>
                            <ListItem>
                                <ListItemText
                                    primary={t('settings.cultural.features.assessment')}
                                    secondary={t('settings.cultural.features.assessmentDesc')}
                                />
                            </ListItem>
                            <ListItem>
                                <ListItemText
                                    primary={t('settings.cultural.features.scenarios')}
                                    secondary={t('settings.cultural.features.scenariosDesc')}
                                />
                            </ListItem>
                            <ListItem>
                                <ListItemText
                                    primary={t('settings.cultural.features.aiStyle')}
                                    secondary={t('settings.cultural.features.aiStyleDesc')}
                                />
                            </ListItem>
                        </List>
                    </Box>

                    <Alert severity="success" icon={<Language />}>
                        <Typography variant="body2">
                            <strong>{t('settings.cultural.multilingualTitle')}:</strong> {t('settings.cultural.multilingualDesc')}
                        </Typography>
                    </Alert>
                </TabPanel>

                <TabPanel value={tabValue} index={2}>
                    <AccessibilitySettings />
                </TabPanel>

                <TabPanel value={tabValue} index={3}>
                    <Typography variant="h5" gutterBottom>
                        {t('settings.tabs.quickLinks')}
                    </Typography>
                    <Divider sx={{ my: 2 }} />

                    <List>
                        <ListItem button onClick={() => navigate('/profile')}>
                            <ListItemIcon>
                                <Person color="primary" />
                            </ListItemIcon>
                            <ListItemText
                                primary={t('settings.quickLinks.profile')}
                                secondary={t('settings.quickLinks.profileDesc')}
                            />
                            <ArrowForward />
                        </ListItem>
                        <Divider />
                        <ListItem button onClick={() => navigate('/profile')}>
                            <ListItemIcon>
                                <Lock color="primary" />
                            </ListItemIcon>
                            <ListItemText
                                primary={t('settings.quickLinks.privacy')}
                                secondary={t('settings.quickLinks.privacyDesc')}
                            />
                            <ArrowForward />
                        </ListItem>
                        <Divider />
                        <ListItem button onClick={() => navigate('/profile')}>
                            <ListItemIcon>
                                <Notifications color="primary" />
                            </ListItemIcon>
                            <ListItemText
                                primary={t('settings.quickLinks.notifications')}
                                secondary={t('settings.quickLinks.notificationsDesc')}
                            />
                            <ArrowForward />
                        </ListItem>
                    </List>

                    <Alert severity="info" sx={{ mt: 3 }}>
                        <Typography variant="body2">
                            {t('settings.quickLinks.detailsNote')}
                        </Typography>
                    </Alert>
                </TabPanel>
            </Paper>
        </Container>
    );
};

export default SettingsPage;