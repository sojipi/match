import React from 'react';
import { useTranslation } from 'react-i18next';
import {
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    SelectChangeEvent,
    Box,
    Typography,
} from '@mui/material';
import { supportedLanguages, SupportedLanguage } from '../i18n/config';

interface LanguageSwitcherProps {
    variant?: 'standard' | 'outlined' | 'filled';
    size?: 'small' | 'medium';
    showLabel?: boolean;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
    variant = 'outlined',
    size = 'medium',
    showLabel = true,
}) => {
    const { i18n, t } = useTranslation();

    const handleLanguageChange = (event: SelectChangeEvent<string>) => {
        const newLanguage = event.target.value as SupportedLanguage;
        i18n.changeLanguage(newLanguage);

        // Update HTML lang attribute for accessibility
        document.documentElement.lang = newLanguage;

        // Update HTML dir attribute for RTL languages
        document.documentElement.dir = supportedLanguages[newLanguage].direction;

        // Store preference in localStorage
        localStorage.setItem('preferredLanguage', newLanguage);
    };

    return (
        <FormControl variant={variant} size={size} fullWidth>
            {showLabel && (
                <InputLabel id="language-select-label">
                    {t('settings.language')}
                </InputLabel>
            )}
            <Select
                labelId="language-select-label"
                id="language-select"
                value={i18n.language}
                onChange={handleLanguageChange}
                label={showLabel ? t('settings.language') : undefined}
                aria-label={t('accessibility.changeLanguage')}
            >
                {Object.entries(supportedLanguages).map(([code, lang]) => (
                    <MenuItem key={code} value={code}>
                        <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body1">{lang.nativeName}</Typography>
                            <Typography variant="body2" color="text.secondary">
                                ({lang.name})
                            </Typography>
                        </Box>
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
};

export default LanguageSwitcher;
