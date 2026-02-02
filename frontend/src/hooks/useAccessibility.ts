import { useEffect, useRef } from 'react';

interface UseAccessibilityOptions {
    announcePageChange?: boolean;
    focusOnMount?: boolean;
    skipToContentId?: string;
}

export const useAccessibility = (options: UseAccessibilityOptions = {}) => {
    const {
        focusOnMount = false,
        skipToContentId = 'main-content',
    } = options;

    const announcementRef = useRef<HTMLDivElement>(null);
    const focusRef = useRef<HTMLElement>(null);

    // Announce page changes to screen readers
    const announceToScreenReader = (message: string) => {
        if (announcementRef.current) {
            announcementRef.current.textContent = message;
            // Clear after a short delay to allow for re-announcements
            setTimeout(() => {
                if (announcementRef.current) {
                    announcementRef.current.textContent = '';
                }
            }, 1000);
        }
    };

    // Focus management for keyboard navigation
    const focusElement = (element?: HTMLElement | null) => {
        const targetElement = element || focusRef.current;
        if (targetElement) {
            targetElement.focus();
        }
    };

    // Skip to main content functionality
    const skipToMainContent = () => {
        const mainContent = document.getElementById(skipToContentId);
        if (mainContent) {
            mainContent.focus();
            mainContent.scrollIntoView({ behavior: 'smooth' });
        }
    };

    // Set up keyboard event listeners
    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            // Skip to main content with Alt + S
            if (event.altKey && event.key === 's') {
                event.preventDefault();
                skipToMainContent();
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [skipToContentId]);

    // Focus on mount if requested
    useEffect(() => {
        if (focusOnMount && focusRef.current) {
            focusRef.current.focus();
        }
    }, [focusOnMount]);

    return {
        announcementRef,
        focusRef,
        announceToScreenReader,
        focusElement,
        skipToMainContent,
    };
};

// Hook for managing focus trap in modals/dialogs
export const useFocusTrap = (isActive: boolean) => {
    const containerRef = useRef<HTMLElement>(null);

    useEffect(() => {
        if (!isActive || !containerRef.current) return;

        const container = containerRef.current;
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        const handleTabKey = (event: KeyboardEvent) => {
            if (event.key !== 'Tab') return;

            if (event.shiftKey) {
                if (document.activeElement === firstElement) {
                    event.preventDefault();
                    lastElement?.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    event.preventDefault();
                    firstElement?.focus();
                }
            }
        };

        const handleEscapeKey = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                // Let parent components handle escape
                event.stopPropagation();
            }
        };

        container.addEventListener('keydown', handleTabKey);
        container.addEventListener('keydown', handleEscapeKey);

        // Focus first element when trap becomes active
        firstElement?.focus();

        return () => {
            container.removeEventListener('keydown', handleTabKey);
            container.removeEventListener('keydown', handleEscapeKey);
        };
    }, [isActive]);

    return containerRef;
};