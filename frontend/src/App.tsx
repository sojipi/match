import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useAppSelector } from './hooks/redux';
import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import PersonalityAssessmentPage from './pages/PersonalityAssessmentPage';
import AvatarPage from './pages/AvatarPage';
import MatchDiscoveryPage from './pages/MatchDiscoveryPage';
import MatchesPage from './pages/MatchesPage';
import MessagesPage from './pages/MessagesPage';
import NotificationsPage from './pages/NotificationsPage';
import LiveMatchingTheaterPage from './pages/LiveMatchingTheaterPage';
import WebSocketTestPage from './pages/WebSocketTestPage';
import SettingsPage from './pages/SettingsPage';
import CompatibilityReportPage from './pages/CompatibilityReportPage';
import ConversationHistoryPage from './pages/ConversationHistoryPage';
import MatchConversationsPage from './pages/MatchConversationsPage';
import ProfileManagementPage from './pages/ProfileManagementPage';
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
                path="/personality-assessment"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <PersonalityAssessmentPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/avatar"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <AvatarPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/discover"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <MatchDiscoveryPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/matches"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <MatchesPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/messages"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <MessagesPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/messages/:matchId"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <MessagesPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/notifications"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <NotificationsPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/theater/:sessionId"
                element={
                    <ProtectedRoute>
                        <LiveMatchingTheaterPage />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/websocket-test"
                element={
                    <ProtectedRoute>
                        <WebSocketTestPage />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/profile"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <ProfileManagementPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/settings"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <SettingsPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/compatibility/:reportId"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <CompatibilityReportPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/match/:matchId/conversations"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <MatchConversationsPage />
                        </AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/conversation/:sessionId"
                element={
                    <ProtectedRoute>
                        <AppLayout>
                            <ConversationHistoryPage />
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