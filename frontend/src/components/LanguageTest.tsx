import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Typography, Button, Stack } from '@mui/material';

/**
 * Simple component to test language switching
 */
const LanguageTest: React.FC = () => {
    const { t, i18n } = useTranslation();

    const changeLanguage = (lng: string) => {
        i18n.changeLanguage(lng);
    };

    return (
        <Box sx={{ p: 3, border: '1px solid #ccc', borderRadius: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
                Language Test Component
            </Typography>
            <Typography variant="body1" gutterBottom>
                Current Language: <strong>{i18n.language}</strong>
            </Typography>
            <Typography variant="body1" gutterBottom>
                {t('common.welcome')}
            </Typography>
            <Typography variant="body1" gutterBottom>
                {t('auth.login')} / {t('auth.register')}
            </Typography>
            <Typography variant="body1" gutterBottom>
                {t('navigation.dashboard')} | {t('navigation.matches')} | {t('navigation.messages')}
            </Typography>

            <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                <Button variant="outlined" size="small" onClick={() => changeLanguage('en')}>
                    English
                </Button>
                <Button variant="outlined" size="small" onClick={() => changeLanguage('zh')}>
                    中文
                </Button>
                <Button variant="outlined" size="small" onClick={() => changeLanguage('es')}>
                    Español
                </Button>
                <Button variant="outlined" size="small" onClick={() => changeLanguage('fr')}>
                    Français
                </Button>
                <Button variant="outlined" size="small" onClick={() => changeLanguage('de')}>
                    Deutsch
                </Button>
                <Button variant="outlined" size="small" onClick={() => changeLanguage('ja')}>
                    日本語
                </Button>
            </Stack>
        </Box>
    );
};

export default LanguageTest;
