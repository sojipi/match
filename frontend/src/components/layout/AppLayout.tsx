import React, { useState } from 'react';
import {
    Box,
    AppBar,
    Toolbar,
    Typography,
    IconButton,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    useTheme,
    useMediaQuery,
    Avatar,
    Menu,
    MenuItem,
    Divider,
    Switch,
    FormControlLabel,
} from '@mui/material';
import {
    Menu as MenuIcon,
    Dashboard as DashboardIcon,
    Search as SearchIcon,
    Favorite as FavoriteIcon,
    Person as PersonIcon,
    Psychology as PsychologyIcon,
    Settings as SettingsIcon,
    Logout as LogoutIcon,
    LightMode,
    DarkMode,
    Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../hooks/redux';
import { logout } from '../../store/slices/authSlice';
import { toggleTheme } from '../../store/slices/themeSlice';
import { useAccessibility } from '../../hooks/useAccessibility';
import SkipLink from '../SkipLink';
import NotificationCenter from '../notifications/NotificationCenter';

interface AppLayoutProps {
    children: React.ReactNode;
}

const drawerWidth = 240;

const navigationItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Discover', icon: <SearchIcon />, path: '/discover' },
    { text: 'Matches', icon: <FavoriteIcon />, path: '/matches' },
    { text: 'Notifications', icon: <NotificationsIcon />, path: '/notifications' },
    { text: 'AI Avatar', icon: <PsychologyIcon />, path: '/avatar' },
    { text: 'Profile', icon: <PersonIcon />, path: '/profile' },
];

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
    const theme = useTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const dispatch = useAppDispatch();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));

    const { user } = useAppSelector(state => state.auth);
    const { mode } = useAppSelector(state => state.theme);

    const [mobileOpen, setMobileOpen] = useState(false);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

    const { announcementRef, announceToScreenReader } = useAccessibility({
        announcePageChange: true,
    });

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleProfileMenuClose = () => {
        setAnchorEl(null);
    };

    const handleLogout = () => {
        dispatch(logout());
        handleProfileMenuClose();
        navigate('/');
        announceToScreenReader('Logged out successfully');
    };

    const handleThemeToggle = () => {
        dispatch(toggleTheme());
        const newMode = mode === 'light' ? 'dark' : 'light';
        announceToScreenReader(`Switched to ${newMode} mode`);
    };

    const handleNavigation = (path: string, itemText: string) => {
        navigate(path);
        if (isMobile) {
            setMobileOpen(false);
        }
        announceToScreenReader(`Navigated to ${itemText}`);
    };

    const drawer = (
        <Box role="navigation" aria-label="Main navigation">
            <Toolbar>
                <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600 }}>
                    AI Matchmaker
                </Typography>
            </Toolbar>
            <Divider />
            <List>
                {navigationItems.map((item) => (
                    <ListItem key={item.text} disablePadding>
                        <ListItemButton
                            selected={location.pathname === item.path}
                            onClick={() => handleNavigation(item.path, item.text)}
                            sx={{
                                '&.Mui-selected': {
                                    backgroundColor: 'primary.main',
                                    color: 'primary.contrastText',
                                    '&:hover': {
                                        backgroundColor: 'primary.dark',
                                    },
                                    '& .MuiListItemIcon-root': {
                                        color: 'primary.contrastText',
                                    },
                                },
                                '&:focus-visible': {
                                    outline: '2px solid',
                                    outlineColor: 'secondary.main',
                                    outlineOffset: '2px',
                                },
                            }}
                            aria-current={location.pathname === item.path ? 'page' : undefined}
                        >
                            <ListItemIcon>{item.icon}</ListItemIcon>
                            <ListItemText primary={item.text} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
            <Divider />
            <List>
                <ListItem>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={mode === 'dark'}
                                onChange={handleThemeToggle}
                                icon={<LightMode />}
                                checkedIcon={<DarkMode />}
                                inputProps={{
                                    'aria-label': `Switch to ${mode === 'light' ? 'dark' : 'light'} mode`,
                                }}
                            />
                        }
                        label={mode === 'dark' ? 'Dark Mode' : 'Light Mode'}
                    />
                </ListItem>
            </List>
        </Box>
    );

    return (
        <Box sx={{ display: 'flex' }}>
            <SkipLink />

            {/* Screen reader announcements */}
            <div
                ref={announcementRef}
                aria-live="polite"
                aria-atomic="true"
                style={{
                    position: 'absolute',
                    left: '-10000px',
                    width: '1px',
                    height: '1px',
                    overflow: 'hidden',
                }}
            />

            <AppBar
                position="fixed"
                sx={{
                    width: { md: `calc(100% - ${drawerWidth}px)` },
                    ml: { md: `${drawerWidth}px` },
                }}
            >
                <Toolbar>
                    <IconButton
                        color="inherit"
                        aria-label="open navigation menu"
                        edge="start"
                        onClick={handleDrawerToggle}
                        sx={{ mr: 2, display: { md: 'none' } }}
                    >
                        <MenuIcon />
                    </IconButton>

                    <Typography variant="h6" noWrap component="h1" sx={{ flexGrow: 1 }}>
                        {navigationItems.find(item => item.path === location.pathname)?.text || 'AI Matchmaker'}
                    </Typography>

                    <NotificationCenter />

                    <IconButton
                        size="large"
                        edge="end"
                        aria-label="account menu"
                        aria-controls="profile-menu"
                        aria-haspopup="true"
                        onClick={handleProfileMenuOpen}
                        color="inherit"
                        sx={{ ml: 1 }}
                    >
                        <Avatar
                            sx={{ width: 32, height: 32 }}
                            alt={user?.firstName ? `${user.firstName} ${user.lastName}` : 'User'}
                            src="/static/images/avatar/1.jpg" // Placeholder
                        >
                            {user?.firstName?.charAt(0) || 'U'}
                        </Avatar>
                    </IconButton>
                </Toolbar>
            </AppBar>

            <Menu
                id="profile-menu"
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleProfileMenuClose}
                onClick={handleProfileMenuClose}
                PaperProps={{
                    elevation: 0,
                    sx: {
                        overflow: 'visible',
                        filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                        mt: 1.5,
                        '& .MuiAvatar-root': {
                            width: 32,
                            height: 32,
                            ml: -0.5,
                            mr: 1,
                        },
                    },
                }}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                MenuListProps={{
                    'aria-labelledby': 'profile-menu',
                    role: 'menu',
                }}
            >
                <MenuItem onClick={() => navigate('/profile')} role="menuitem">
                    <PersonIcon sx={{ mr: 2 }} />
                    Profile
                </MenuItem>
                <MenuItem onClick={() => navigate('/settings')} role="menuitem">
                    <SettingsIcon sx={{ mr: 2 }} />
                    Settings
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleLogout} role="menuitem">
                    <LogoutIcon sx={{ mr: 2 }} />
                    Logout
                </MenuItem>
            </Menu>

            <Box
                component="nav"
                sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
                aria-label="navigation menu"
            >
                <Drawer
                    variant="temporary"
                    open={mobileOpen}
                    onClose={handleDrawerToggle}
                    ModalProps={{
                        keepMounted: true, // Better open performance on mobile.
                    }}
                    sx={{
                        display: { xs: 'block', md: 'none' },
                        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                    }}
                >
                    {drawer}
                </Drawer>
                <Drawer
                    variant="permanent"
                    sx={{
                        display: { xs: 'none', md: 'block' },
                        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                    }}
                    open
                >
                    {drawer}
                </Drawer>
            </Box>

            <Box
                component="main"
                id="main-content"
                tabIndex={-1}
                sx={{
                    flexGrow: 1,
                    p: 3,
                    width: { md: `calc(100% - ${drawerWidth}px)` },
                    minHeight: '100vh',
                    backgroundColor: 'background.default',
                    '&:focus': {
                        outline: 'none',
                    },
                }}
            >
                <Toolbar />
                {children}
            </Box>
        </Box>
    );
};

export default AppLayout;