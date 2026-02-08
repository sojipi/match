/**
 * Accessibility Testing Utilities
 * 
 * Utilities for automated accessibility compliance checking
 */

export interface AccessibilityIssue {
    type: 'error' | 'warning' | 'info';
    rule: string;
    message: string;
    element?: HTMLElement;
    wcagLevel: 'A' | 'AA' | 'AAA';
}

/**
 * Check if an element has sufficient color contrast
 */
export const checkColorContrast = (element: HTMLElement): AccessibilityIssue | null => {
    const computedStyle = window.getComputedStyle(element);
    const backgroundColor = computedStyle.backgroundColor;
    const color = computedStyle.color;

    // Simple check - in production, use a proper contrast calculation library
    if (backgroundColor === 'transparent' || color === 'transparent') {
        return null;
    }

    // This is a placeholder - implement proper contrast ratio calculation
    const contrastRatio = calculateContrastRatio(color, backgroundColor);

    if (contrastRatio < 4.5) {
        return {
            type: 'error',
            rule: 'color-contrast',
            message: `Insufficient color contrast ratio: ${contrastRatio.toFixed(2)}:1 (minimum 4.5:1 required)`,
            element,
            wcagLevel: 'AA',
        };
    }

    return null;
};

/**
 * Calculate contrast ratio between two colors
 * Simplified version - use a proper library in production
 */
const calculateContrastRatio = (color1: string, color2: string): number => {
    // Placeholder implementation
    // In production, use a library like 'color-contrast-checker'
    return 4.5; // Assume passing for now
};

/**
 * Check if images have alt text
 */
export const checkImageAltText = (container: HTMLElement = document.body): AccessibilityIssue[] => {
    const issues: AccessibilityIssue[] = [];
    const images = container.querySelectorAll('img');

    images.forEach(img => {
        if (!img.hasAttribute('alt')) {
            issues.push({
                type: 'error',
                rule: 'img-alt',
                message: 'Image missing alt attribute',
                element: img,
                wcagLevel: 'A',
            });
        } else if (img.getAttribute('alt') === '' && !img.hasAttribute('role')) {
            // Empty alt is okay for decorative images, but should have role="presentation"
            issues.push({
                type: 'warning',
                rule: 'img-alt-decorative',
                message: 'Decorative image should have role="presentation" or role="none"',
                element: img,
                wcagLevel: 'A',
            });
        }
    });

    return issues;
};

/**
 * Check if form inputs have labels
 */
export const checkFormLabels = (container: HTMLElement = document.body): AccessibilityIssue[] => {
    const issues: AccessibilityIssue[] = [];
    const inputs = container.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        const id = input.getAttribute('id');
        const ariaLabel = input.getAttribute('aria-label');
        const ariaLabelledBy = input.getAttribute('aria-labelledby');

        if (!id && !ariaLabel && !ariaLabelledBy) {
            issues.push({
                type: 'error',
                rule: 'form-label',
                message: 'Form input missing label, aria-label, or aria-labelledby',
                element: input as HTMLElement,
                wcagLevel: 'A',
            });
        } else if (id) {
            const label = container.querySelector(`label[for="${id}"]`);
            if (!label && !ariaLabel && !ariaLabelledBy) {
                issues.push({
                    type: 'error',
                    rule: 'form-label',
                    message: 'Form input has id but no associated label',
                    element: input as HTMLElement,
                    wcagLevel: 'A',
                });
            }
        }
    });

    return issues;
};

/**
 * Check if interactive elements are keyboard accessible
 */
export const checkKeyboardAccessibility = (container: HTMLElement = document.body): AccessibilityIssue[] => {
    const issues: AccessibilityIssue[] = [];
    const interactiveElements = container.querySelectorAll('[onclick], [onkeydown], [onkeyup]');

    interactiveElements.forEach(element => {
        const tabIndex = element.getAttribute('tabindex');
        const role = element.getAttribute('role');
        const tagName = element.tagName.toLowerCase();

        // Check if element is naturally focusable or has tabindex
        const naturallyFocusable = ['a', 'button', 'input', 'select', 'textarea'].includes(tagName);

        if (!naturallyFocusable && tabIndex === null) {
            issues.push({
                type: 'error',
                rule: 'keyboard-accessible',
                message: 'Interactive element is not keyboard accessible (missing tabindex)',
                element: element as HTMLElement,
                wcagLevel: 'A',
            });
        }

        // Check if element has appropriate role
        if (!naturallyFocusable && !role) {
            issues.push({
                type: 'warning',
                rule: 'interactive-role',
                message: 'Interactive element should have an appropriate ARIA role',
                element: element as HTMLElement,
                wcagLevel: 'A',
            });
        }
    });

    return issues;
};

/**
 * Check if headings are in logical order
 */
export const checkHeadingOrder = (container: HTMLElement = document.body): AccessibilityIssue[] => {
    const issues: AccessibilityIssue[] = [];
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');

    let previousLevel = 0;

    headings.forEach(heading => {
        const level = parseInt(heading.tagName.substring(1));

        if (previousLevel > 0 && level > previousLevel + 1) {
            issues.push({
                type: 'warning',
                rule: 'heading-order',
                message: `Heading level skipped from h${previousLevel} to h${level}`,
                element: heading as HTMLElement,
                wcagLevel: 'A',
            });
        }

        previousLevel = level;
    });

    return issues;
};

/**
 * Check if buttons have accessible names
 */
export const checkButtonNames = (container: HTMLElement = document.body): AccessibilityIssue[] => {
    const issues: AccessibilityIssue[] = [];
    const buttons = container.querySelectorAll('button');

    buttons.forEach(button => {
        const text = button.textContent?.trim();
        const ariaLabel = button.getAttribute('aria-label');
        const ariaLabelledBy = button.getAttribute('aria-labelledby');

        if (!text && !ariaLabel && !ariaLabelledBy) {
            issues.push({
                type: 'error',
                rule: 'button-name',
                message: 'Button has no accessible name',
                element: button,
                wcagLevel: 'A',
            });
        }
    });

    return issues;
};

/**
 * Check if links have accessible names
 */
export const checkLinkNames = (container: HTMLElement = document.body): AccessibilityIssue[] => {
    const issues: AccessibilityIssue[] = [];
    const links = container.querySelectorAll('a');

    links.forEach(link => {
        const text = link.textContent?.trim();
        const ariaLabel = link.getAttribute('aria-label');
        const ariaLabelledBy = link.getAttribute('aria-labelledby');

        if (!text && !ariaLabel && !ariaLabelledBy) {
            issues.push({
                type: 'error',
                rule: 'link-name',
                message: 'Link has no accessible name',
                element: link,
                wcagLevel: 'A',
            });
        }

        // Check for generic link text
        const genericTexts = ['click here', 'read more', 'here', 'more'];
        if (text && genericTexts.includes(text.toLowerCase())) {
            issues.push({
                type: 'warning',
                rule: 'link-name-descriptive',
                message: 'Link text should be more descriptive',
                element: link,
                wcagLevel: 'AAA',
            });
        }
    });

    return issues;
};

/**
 * Run all accessibility checks
 */
export const runAccessibilityAudit = (container: HTMLElement = document.body): AccessibilityIssue[] => {
    const issues: AccessibilityIssue[] = [];

    issues.push(...checkImageAltText(container));
    issues.push(...checkFormLabels(container));
    issues.push(...checkKeyboardAccessibility(container));
    issues.push(...checkHeadingOrder(container));
    issues.push(...checkButtonNames(container));
    issues.push(...checkLinkNames(container));

    return issues;
};

/**
 * Generate accessibility report
 */
export const generateAccessibilityReport = (issues: AccessibilityIssue[]): string => {
    const errors = issues.filter(i => i.type === 'error');
    const warnings = issues.filter(i => i.type === 'warning');
    const info = issues.filter(i => i.type === 'info');

    let report = '=== Accessibility Audit Report ===\n\n';
    report += `Total Issues: ${issues.length}\n`;
    report += `Errors: ${errors.length}\n`;
    report += `Warnings: ${warnings.length}\n`;
    report += `Info: ${info.length}\n\n`;

    if (errors.length > 0) {
        report += '--- Errors ---\n';
        errors.forEach((issue, index) => {
            report += `${index + 1}. [${issue.wcagLevel}] ${issue.rule}: ${issue.message}\n`;
        });
        report += '\n';
    }

    if (warnings.length > 0) {
        report += '--- Warnings ---\n';
        warnings.forEach((issue, index) => {
            report += `${index + 1}. [${issue.wcagLevel}] ${issue.rule}: ${issue.message}\n`;
        });
        report += '\n';
    }

    return report;
};
