import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../hooks/redux';
import LoadingSpinner from './LoadingSpinner';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const { token, isLoading } = useAppSelector(state => state.auth);
    const location = useLocation();

    // Show loading spinner while checking authentication
    if (isLoading) {
        return (
            <LoadingSpinner
                fullScreen
                message="Verifying your session..."
                delay={200}
            />
        );
    }

    // Redirect to login if not authenticated, preserving the intended destination
    if (!token) {
        return (
            <Navigate
                to="/auth/login"
                state={{ from: location }}
                replace
            />
        );
    }

    return <>{children}</>;
};

export default ProtectedRoute;