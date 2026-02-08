import { useEffect, useCallback, RefObject } from 'react';

interface KeyboardNavigationOptions {
    onEscape?: () => void;
    onEnter?: () => void;
    onArrowUp?: () => void;
    onArrowDown?: () => void;
    onArrowLeft?: () => void;
    onArrowRight?: () => void;
    onTab?: () => void;
    onShiftTab?: () => void;
    enabled?: boolean;
}

/**
 * Hook for handling keyboard navigation
 */
export const useKeyboardNavigation = (
    ref: RefObject<HTMLElement>,
    options: KeyboardNavigationOptions = {}
) => {
    const {
        onEscape,
        onEnter,
        onArrowUp,
        onArrowDown,
        onArrowLeft,
        onArrowRight,
        onTab,
        onShiftTab,
        enabled = true,
    } = options;

    const handleKeyDown = useCallback(
        (event: KeyboardEvent) => {
            if (!enabled) return;

            switch (event.key) {
                case 'Escape':
                    if (onEscape) {
                        event.preventDefault();
                        onEscape();
                    }
                    break;
                case 'Enter':
                    if (onEnter) {
                        event.preventDefault();
                        onEnter();
                    }
                    break;
                case 'ArrowUp':
                    if (onArrowUp) {
                        event.preventDefault();
                        onArrowUp();
                    }
                    break;
                case 'ArrowDown':
                    if (onArrowDown) {
                        event.preventDefault();
                        onArrowDown();
                    }
                    break;
                case 'ArrowLeft':
                    if (onArrowLeft) {
                        event.preventDefault();
                        onArrowLeft();
                    }
                    break;
                case 'ArrowRight':
                    if (onArrowRight) {
                        event.preventDefault();
                        onArrowRight();
                    }
                    break;
                case 'Tab':
                    if (event.shiftKey && onShiftTab) {
                        event.preventDefault();
                        onShiftTab();
                    } else if (!event.shiftKey && onTab) {
                        event.preventDefault();
                        onTab();
                    }
                    break;
            }
        },
        [enabled, onEscape, onEnter, onArrowUp, onArrowDown, onArrowLeft, onArrowRight, onTab, onShiftTab]
    );

    useEffect(() => {
        const element = ref.current;
        if (!element) return;

        element.addEventListener('keydown', handleKeyDown);

        return () => {
            element.removeEventListener('keydown', handleKeyDown);
        };
    }, [ref, handleKeyDown]);
};

/**
 * Hook for managing focus trap in modals and dialogs
 */
export const useFocusTrap = (
    containerRef: RefObject<HTMLElement>,
    isActive: boolean = true
) => {
    useEffect(() => {
        if (!isActive || !containerRef.current) return;

        const container = containerRef.current;
        const focusableElements = container.querySelectorAll<HTMLElement>(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        const handleTabKey = (event: KeyboardEvent) => {
            if (event.key !== 'Tab') return;

            if (event.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    event.preventDefault();
                    lastElement?.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    event.preventDefault();
                    firstElement?.focus();
                }
            }
        };

        // Focus first element when trap activates
        firstElement?.focus();

        container.addEventListener('keydown', handleTabKey);

        return () => {
            container.removeEventListener('keydown', handleTabKey);
        };
    }, [containerRef, isActive]);
};

/**
 * Hook for announcing content to screen readers
 */
export const useAriaLiveAnnouncement = () => {
    const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', priority);
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }, []);

    return announce;
};

/**
 * Hook for managing focus restoration
 */
export const useFocusRestore = (shouldRestore: boolean = true) => {
    useEffect(() => {
        if (!shouldRestore) return;

        const previouslyFocused = document.activeElement as HTMLElement;

        return () => {
            if (previouslyFocused && previouslyFocused.focus) {
                previouslyFocused.focus();
            }
        };
    }, [shouldRestore]);
};
