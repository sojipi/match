import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type FontSize = 'small' | 'medium' | 'large' | 'extra-large';
export type ContrastMode = 'normal' | 'high';

interface AccessibilitySettings {
    fontSize: FontSize;
    highContrast: boolean;
    reducedMotion: boolean;
    screenReaderOptimized: boolean;
    keyboardNavigationEnabled: boolean;
}

interface AccessibilityContextType {
    settings: AccessibilitySettings;
    updateFontSize: (size: FontSize) => void;
    toggleHighContrast: () => void;
    toggleReducedMotion: () => void;
    toggleScreenReaderMode: () => void;
    increaseFontSize: () => void;
    decreaseFontSize: () => void;
    resetSettings: () => void;
}

const defaultSettings: AccessibilitySettings = {
    fontSize: 'medium',
    highContrast: false,
    reducedMotion: false,
    screenReaderOptimized: false,
    keyboardNavigationEnabled: true,
};

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const useAccessibility = () => {
    const context = useContext(AccessibilityContext);
    if (!context) {
        throw new Error('useAccessibility must be used within AccessibilityProvider');
    }
    return context;
};

interface AccessibilityProviderProps {
    children: ReactNode;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
    const [settings, setSettings] = useState<AccessibilitySettings>(() => {
        // Load settings from localStorage
        const saved = localStorage.getItem('accessibilitySettings');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch {
                return defaultSettings;
            }
        }

        // Check for system preferences
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;

        return {
            ...defaultSettings,
            reducedMotion: prefersReducedMotion,
            highContrast: prefersHighContrast,
        };
    });

    // Save settings to localStorage whenever they change
    useEffect(() => {
        localStorage.setItem('accessibilitySettings', JSON.stringify(settings));
        applyAccessibilitySettings(settings);
    }, [settings]);

    // Listen for system preference changes
    useEffect(() => {
        const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        const highContrastQuery = window.matchMedia('(prefers-contrast: high)');

        const handleReducedMotionChange = (e: MediaQueryListEvent) => {
            setSettings(prev => ({ ...prev, reducedMotion: e.matches }));
        };

        const handleHighContrastChange = (e: MediaQueryListEvent) => {
            setSettings(prev => ({ ...prev, highContrast: e.matches }));
        };

        reducedMotionQuery.addEventListener('change', handleReducedMotionChange);
        highContrastQuery.addEventListener('change', handleHighContrastChange);

        return () => {
            reducedMotionQuery.removeEventListener('change', handleReducedMotionChange);
            highContrastQuery.removeEventListener('change', handleHighContrastChange);
        };
    }, []);

    const applyAccessibilitySettings = (settings: AccessibilitySettings) => {
        const root = document.documentElement;

        // Apply font size
        const fontSizeMap: Record<FontSize, string> = {
            small: '14px',
            medium: '16px',
            large: '18px',
            'extra-large': '20px',
        };
        root.style.fontSize = fontSizeMap[settings.fontSize];

        // Apply high contrast
        if (settings.highContrast) {
            root.classList.add('high-contrast');
        } else {
            root.classList.remove('high-contrast');
        }

        // Apply reduced motion
        if (settings.reducedMotion) {
            root.classList.add('reduced-motion');
        } else {
            root.classList.remove('reduced-motion');
        }

        // Apply screen reader optimization
        if (settings.screenReaderOptimized) {
            root.classList.add('screen-reader-optimized');
        } else {
            root.classList.remove('screen-reader-optimized');
        }
    };

    const updateFontSize = (size: FontSize) => {
        setSettings(prev => ({ ...prev, fontSize: size }));
    };

    const increaseFontSize = () => {
        const sizes: FontSize[] = ['small', 'medium', 'large', 'extra-large'];
        const currentIndex = sizes.indexOf(settings.fontSize);
        if (currentIndex < sizes.length - 1) {
            updateFontSize(sizes[currentIndex + 1]);
        }
    };

    const decreaseFontSize = () => {
        const sizes: FontSize[] = ['small', 'medium', 'large', 'extra-large'];
        const currentIndex = sizes.indexOf(settings.fontSize);
        if (currentIndex > 0) {
            updateFontSize(sizes[currentIndex - 1]);
        }
    };

    const toggleHighContrast = () => {
        setSettings(prev => ({ ...prev, highContrast: !prev.highContrast }));
    };

    const toggleReducedMotion = () => {
        setSettings(prev => ({ ...prev, reducedMotion: !prev.reducedMotion }));
    };

    const toggleScreenReaderMode = () => {
        setSettings(prev => ({ ...prev, screenReaderOptimized: !prev.screenReaderOptimized }));
    };

    const resetSettings = () => {
        setSettings(defaultSettings);
    };

    const value: AccessibilityContextType = {
        settings,
        updateFontSize,
        toggleHighContrast,
        toggleReducedMotion,
        toggleScreenReaderMode,
        increaseFontSize,
        decreaseFontSize,
        resetSettings,
    };

    return (
        <AccessibilityContext.Provider value={value}>
            {children}
        </AccessibilityContext.Provider>
    );
};
