import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Import translation files
import enTranslations from './locales/en/translation.json';
import esTranslations from './locales/es/translation.json';
import frTranslations from './locales/fr/translation.json';
import deTranslations from './locales/de/translation.json';
import zhTranslations from './locales/zh/translation.json';
import jaTranslations from './locales/ja/translation.json';

// Supported languages with cultural metadata
export const supportedLanguages = {
    en: {
        code: 'en',
        name: 'English',
        nativeName: 'English',
        direction: 'ltr',
        culturalContext: 'western',
    },
    es: {
        code: 'es',
        name: 'Spanish',
        nativeName: 'Español',
        direction: 'ltr',
        culturalContext: 'western',
    },
    fr: {
        code: 'fr',
        name: 'French',
        nativeName: 'Français',
        direction: 'ltr',
        culturalContext: 'western',
    },
    de: {
        code: 'de',
        name: 'German',
        nativeName: 'Deutsch',
        direction: 'ltr',
        culturalContext: 'western',
    },
    zh: {
        code: 'zh',
        name: 'Chinese',
        nativeName: '中文',
        direction: 'ltr',
        culturalContext: 'eastern',
    },
    ja: {
        code: 'ja',
        name: 'Japanese',
        nativeName: '日本語',
        direction: 'ltr',
        culturalContext: 'eastern',
    },
} as const;

export type SupportedLanguage = keyof typeof supportedLanguages;

// Initialize i18next
i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources: {
            en: { translation: enTranslations },
            es: { translation: esTranslations },
            fr: { translation: frTranslations },
            de: { translation: deTranslations },
            zh: { translation: zhTranslations },
            ja: { translation: jaTranslations },
        },
        fallbackLng: 'en',
        supportedLngs: Object.keys(supportedLanguages),
        debug: true, // Enable debug to see what's happening
        interpolation: {
            escapeValue: false, // React already escapes values
        },
        detection: {
            order: ['localStorage', 'navigator', 'htmlTag'],
            caches: ['localStorage'],
            lookupLocalStorage: 'i18nextLng',
        },
        react: {
            useSuspense: false, // Disable suspense for better compatibility
        },
    });

// Expose i18n instance to window for debugging
if (typeof window !== 'undefined') {
    (window as any).i18next = i18n;
}

export default i18n;
