import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box, AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider, Avatar, Menu, MenuItem } from '@mui/material';
import { Menu as MenuIcon, Public, Image as ImageIcon, Assessment, Settings, Login, Logout, SpaceDashboard } from '@mui/icons-material';
import { Exoplanets } from './pages/Exoplanets';
import { ExoplanetDetail } from './pages/ExoplanetDetail';
import { ImageClassifier } from './pages/ImageClassifier';
import { Visualization } from './pages/Visualization';
import { useUserStore } from './store';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#4a90d9',
    },
    secondary: {
      main: '#feca57',
    },
    success: {
      main: '#4caf50',
    },
    background: {
      default: '#0a0a1a',
      paper: '#1a1a2e',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 700,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

const drawerWidth = 280;

const menuItems = [
  { text: 'Exoplanets', icon: <Public />, path: '/exoplanets' },
  { text: 'Image Classifier', icon: <ImageIcon />, path: '/classifier' },
  { text: 'Visualization', icon: <Assessment />, path: '/visualization' },
];

function App() {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const { user, isAuthenticated, logout, checkAuth } = useUserStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleUserMenuClose();
  };

  const drawer = (
    <Box>
      <Toolbar>
        <SpaceDashboard sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
          AstroAI-Core
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton component="a" href={item.path}>
              <ListItemIcon sx={{ color: 'primary.main' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton component="a" href="/settings">
            <ListItemIcon>
              <Settings />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          {/* App Bar */}
          <AppBar
            position="fixed"
            sx={{
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              ml: { sm: `${drawerWidth}px` },
              bgcolor: 'rgba(26, 26, 46, 0.95)',
              backdropFilter: 'blur(10px)',
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2, display: { sm: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                Astronomy × AI Research Platform
              </Typography>
              
              {isAuthenticated ? (
                <>
                  <IconButton onClick={handleUserMenuOpen} sx={{ ml: 2 }}>
                    <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                      {user?.username.charAt(0).toUpperCase()}
                    </Avatar>
                  </IconButton>
                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleUserMenuClose}
                  >
                    <MenuItem disabled>
                      {user?.username}
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={handleLogout}>
                      <ListItemIcon>
                        <Logout fontSize="small" />
                      </ListItemIcon>
                      Logout
                    </MenuItem>
                  </Menu>
                </>
              ) : (
                <IconButton component="a" href="/login" sx={{ ml: 2 }}>
                  <Login />
                </IconButton>
              )}
            </Toolbar>
          </AppBar>

          {/* Drawer */}
          <Box
            component="nav"
            sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
          >
            <Drawer
              variant="temporary"
              open={mobileOpen}
              onClose={handleDrawerToggle}
              ModalProps={{ keepMounted: true }}
              sx={{
                display: { xs: 'block', sm: 'none' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              {drawer}
            </Drawer>
            <Drawer
              variant="permanent"
              sx={{
                display: { xs: 'none', sm: 'block' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box>

          {/* Main Content */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              mt: 8,
            }}
          >
            <Routes>
              <Route path="/" element={<Navigate to="/exoplanets" replace />} />
              <Route path="/exoplanets" element={<Exoplanets />} />
              <Route path="/exoplanets/:id" element={<ExoplanetDetail />} />
              <Route path="/classifier" element={<ImageClassifier />} />
              <Route path="/visualization" element={<Visualization />} />
              <Route path="/login" element={
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Typography variant="h5">Login Page (To be implemented)</Typography>
                </Box>
              } />
              <Route path="/settings" element={
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Typography variant="h5">Settings Page (To be implemented)</Typography>
                </Box>
              } />
              <Route path="*" element={
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Typography variant="h4">404</Typography>
                  <Typography variant="body1">Page not found</Typography>
                </Box>
              } />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
