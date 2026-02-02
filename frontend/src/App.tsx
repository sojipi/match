import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useAppSelector } from './hooks/redux';
import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import LoadingSpinner from './components/LoadingSpinner';

const App: React.FC = () => {
    const { isLoading } = useAppSelector(state => state.auth);

    if (isLoading) {
        return (
            <LoadingSpinner
                fullScreen
                message="Loading your profile..."
                delay={300}
            />
        );
    }

    return (
        <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/auth/*" element={<AuthPage />} />

            {/* Protected routes with layout */}
            <Route
                path="/dashboard/*"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <Dashboard />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/discover"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <div>Discover Page - Coming Soon</div>
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/matches"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <div>Matches Page - Coming Soon</div>
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/messages"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <div>Messages Page - Coming Soon</div>
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/profile"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <div>Profile Page - Coming Soon</div>
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/settings"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <div>Settings Page - Coming Soon</div>
                        </AppLayout>
                    </ProtectedRoute>
                }
            />

            {/* Catch-all route for 404 */}
            <Route
                path="*"
                element={
                    <div style={{
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        height: '100vh',
                        flexDirection: 'column',
                        gap: '1rem'
                    }}>
                        <h1>404 - Page Not Found</h1>
                        <p>The page you're looking for doesn't exist.</p>
                    </div>
                }
            />
        </Routes>
    );
};

export default App;