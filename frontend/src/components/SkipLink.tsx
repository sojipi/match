import React from 'react';
import { Button, styled } from '@mui/material';

const SkipLinkButton = styled(Button)(({ theme }) => ({
    position: 'absolute',
    top: -40,
    left: 6,
    zIndex: 10000,
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    padding: '8px 16px',
    textDecoration: 'none',
    borderRadius: 4,
    fontSize: '14px',
    fontWeight: 600,
    border: `2px solid ${theme.palette.primary.main}`,
    transition: 'top 0.3s ease',
    '&:focus': {
        top: 6,
        outline: `2px solid ${theme.palette.secondary.main}`,
        outlineOffset: 2,
    },
    '&:hover:focus': {
        top: 6,
        backgroundColor: theme.palette.primary.dark,
    },
}));

interface SkipLinkProps {
    targetId?: string;
    children?: React.ReactNode;
}

const SkipLink: React.FC<SkipLinkProps> = ({
    targetId = 'main-content',
    children = 'Skip to main content'
}) => {
    const handleSkip = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        const target = document.getElementById(targetId);
        if (target) {
            target.focus();
            target.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <SkipLinkButton
            onClick={handleSkip}
            onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    handleSkip(event as any);
                }
            }}
            aria-label={`Skip to ${targetId.replace('-', ' ')}`}
        >
            {children}
        </SkipLinkButton>
    );
};

export default SkipLink;