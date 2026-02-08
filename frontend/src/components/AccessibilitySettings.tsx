import React from 'react';
import {
    Box,
    Typography,
    Switch,
    FormControlLabel,
    Button,
    ButtonGroup,
    Paper,
    Divider,
    Alert,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
} from '@mui/material';
import {
    TextIncrease,
    TextDecrease,
    Contrast,
    MotionPhotosOff,
    Accessibility,
    Keyboard,
    RestartAlt,
} from '@mui/icons-material';
import { useAccessibility } from '../contexts/AccessibilityContext';
import { useTranslation } from 'react-i18next';

const AccessibilitySettings: React.FC = () => {
    const {
        settings,
        toggleHighContrast,
        toggleReducedMotion,
        toggleScreenReaderMode,
        increaseFontSize,
        decreaseFontSize,
        resetSettings,
    } = useAccessibility();

    const { t } = useTranslation();

    const fontSizeLabels = {
        small: 'Small (14px)',
        medium: 'Medium (16px)',
        large: 'Large (18px)',
        'extra-large': 'Extra Large (20px)',
    };

    return (
        <Box>
            <Typography variant="h5" gutterBottom>
                {t('settings.accessibility')}
            </Typography>
            <Divider sx={{ my: 2 }} />

            <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                    These settings help make the platform more accessible. Changes are saved automatically
                    and will persist across sessions.
                </Typography>
            </Alert>

            {/* Font Size Control */}
            <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                    <Box>
                        <Typography variant="subtitle1" gutterBottom>
                            {t('settings.fontSize')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Current: {fontSizeLabels[settings.fontSize]}
                        </Typography>
                    </Box>
                    <ButtonGroup variant="outlined" aria-label="font size controls">
                        <Button
                            onClick={decreaseFontSize}
                            disabled={settings.fontSize === 'small'}
                            aria-label={t('accessibility.decreaseFontSize')}
                            startIcon={<TextDecrease />}
                        >
                            Smaller
                        </Button>
                        <Button
                            onClick={increaseFontSize}
                            disabled={settings.fontSize === 'extra-large'}
                            aria-label={t('accessibility.increaseFontSize')}
                            startIcon={<TextIncrease />}
                        >
                            Larger
                        </Button>
                    </ButtonGroup>
                </Box>
            </Paper>

            {/* High Contrast Mode */}
            <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                <FormControlLabel
                    control={
                        <Switch
                            checked={settings.highContrast}
                            onChange={toggleHighContrast}
                            inputProps={{
                                'aria-label': 'Toggle high contrast mode',
                            }}
                        />
                    }
                    label={
                        <Box>
                            <Box display="flex" alignItems="center" gap={1}>
                                <Contrast />
                                <Typography variant="subtitle1">
                                    {t('settings.highContrast')}
                                </Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                                Increases color contrast for better visibility
                            </Typography>
                        </Box>
                    }
                />
            </Paper>

            {/* Reduced Motion */}
            <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                <FormControlLabel
                    control={
                        <Switch
                            checked={settings.reducedMotion}
                            onChange={toggleReducedMotion}
                            inputProps={{
                                'aria-label': 'Toggle reduced motion',
                            }}
                        />
                    }
                    label={
                        <Box>
                            <Box display="flex" alignItems="center" gap={1}>
                                <MotionPhotosOff />
                                <Typography variant="subtitle1">
                                    Reduce Motion
                                </Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                                Minimizes animations and transitions
                            </Typography>
                        </Box>
                    }
                />
            </Paper>

            {/* Screen Reader Optimization */}
            <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                <FormControlLabel
                    control={
                        <Switch
                            checked={settings.screenReaderOptimized}
                            onChange={toggleScreenReaderMode}
                            inputProps={{
                                'aria-label': 'Toggle screen reader optimization',
                            }}
                        />
                    }
                    label={
                        <Box>
                            <Box display="flex" alignItems="center" gap={1}>
                                <Accessibility />
                                <Typography variant="subtitle1">
                                    Screen Reader Optimization
                                </Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                                Optimizes layout and navigation for screen readers
                            </Typography>
                        </Box>
                    }
                />
            </Paper>

            {/* Keyboard Navigation Info */}
            <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <Keyboard />
                    <Typography variant="subtitle1">
                        Keyboard Navigation
                    </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                    Full keyboard navigation is always enabled. Use Tab to move forward, Shift+Tab to move backward,
                    and Enter or Space to activate elements.
                </Typography>
                <List dense>
                    <ListItem>
                        <ListItemText
                            primary="Tab / Shift+Tab"
                            secondary="Navigate between interactive elements"
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Enter / Space"
                            secondary="Activate buttons and links"
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Escape"
                            secondary="Close dialogs and menus"
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Arrow Keys"
                            secondary="Navigate within menus and lists"
                        />
                    </ListItem>
                </List>
            </Paper>

            {/* WCAG Compliance Info */}
            <Alert severity="success" sx={{ mb: 2 }}>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                    WCAG 2.1 AA Compliance
                </Typography>
                <Typography variant="body2">
                    This platform is designed to meet WCAG 2.1 Level AA accessibility standards, including:
                </Typography>
                <List dense>
                    <ListItem>
                        <ListItemIcon sx={{ minWidth: 32 }}>✓</ListItemIcon>
                        <ListItemText primary="Keyboard accessible navigation" />
                    </ListItem>
                    <ListItem>
                        <ListItemIcon sx={{ minWidth: 32 }}>✓</ListItemIcon>
                        <ListItemText primary="Screen reader compatible" />
                    </ListItem>
                    <ListItem>
                        <ListItemIcon sx={{ minWidth: 32 }}>✓</ListItemIcon>
                        <ListItemText primary="Sufficient color contrast" />
                    </ListItem>
                    <ListItem>
                        <ListItemIcon sx={{ minWidth: 32 }}>✓</ListItemIcon>
                        <ListItemText primary="Resizable text without loss of functionality" />
                    </ListItem>
                    <ListItem>
                        <ListItemIcon sx={{ minWidth: 32 }}>✓</ListItemIcon>
                        <ListItemText primary="Clear focus indicators" />
                    </ListItem>
                </List>
            </Alert>

            {/* Reset Button */}
            <Box display="flex" justifyContent="center" mt={3}>
                <Button
                    variant="outlined"
                    startIcon={<RestartAlt />}
                    onClick={resetSettings}
                    aria-label="Reset accessibility settings to defaults"
                >
                    Reset to Defaults
                </Button>
            </Box>
        </Box>
    );
};

export default AccessibilitySettings;
