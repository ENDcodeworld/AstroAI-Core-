import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Paper,
  IconButton,
  Chip,
  Divider,
  Button,
  Skeleton,
} from '@mui/material';
import { ArrowBack, LocationOn, Timeline, FitnessCenter, Public, Thermostat, Star } from '@mui/icons-material';
import { OrbitViewer } from '../components/OrbitViewer';
import { useExoplanetStore } from '../store';

export const ExoplanetDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedPlanet, setSelectedPlanet, planets } = useExoplanetStore();

  useEffect(() => {
    if (id && planets.length > 0) {
      const planet = planets.find(p => p.id === id);
      if (planet) {
        setSelectedPlanet(planet);
      } else {
        navigate('/exoplanets');
      }
    }
  }, [id, planets, setSelectedPlanet, navigate]);

  if (!selectedPlanet) {
    return (
      <Box sx={{ p: 4 }}>
        <Skeleton variant="rectangular" height={400} sx={{ mb: 3, borderRadius: 2 }} />
        <Skeleton variant="text" height={60} width="60%" sx={{ mb: 2 }} />
        <Skeleton variant="text" height={40} width="80%" />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Back button */}
      <IconButton onClick={() => navigate('/exoplanets')} sx={{ mb: 2 }}>
        <ArrowBack />
      </IconButton>

      <Grid container spacing={4}>
        {/* Left column - Visualization */}
        <Grid item xs={12} lg={8}>
          <Paper
            elevation={3}
            sx={{
              p: 2,
              bgcolor: '#0a0a1a',
              borderRadius: 2,
              mb: 3,
            }}
          >
            <Typography variant="h6" sx={{ mb: 2, color: '#ffffff' }}>
              Orbital Visualization
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <OrbitViewer planet={selectedPlanet} width={700} height={500} />
            </Box>
          </Paper>

          {/* Description */}
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2 }}>
              About {selectedPlanet.name}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.8 }}>
              {selectedPlanet.description}
            </Typography>
            
            <Divider sx={{ my: 3 }} />
            
            <Typography variant="h6" sx={{ mb: 2 }}>
              Discovery Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary">
                  Discovery Year
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  {selectedPlanet.discoveryYear}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary">
                  Discovery Method
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  {selectedPlanet.discoveryMethod}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary">
                  Host Star
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  {selectedPlanet.hostStar}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary">
                  Constellation
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  {selectedPlanet.constellation}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Right column - Stats */}
        <Grid item xs={12} lg={4}>
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {selectedPlanet.name}
              </Typography>
              {selectedPlanet.habitableZone && (
                <Chip label="Habitable Zone" color="success" size="small" />
              )}
            </Box>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {selectedPlanet.hostStar} • {selectedPlanet.constellation}
            </Typography>

            <Divider sx={{ mb: 3 }} />

            {/* Physical Properties */}
            <Typography variant="h6" sx={{ mb: 2 }}>
              Physical Properties
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Box sx={{ bgcolor: 'primary.light', p: 1.5, borderRadius: 2, flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <FitnessCenter fontSize="small" />
                  <Typography variant="caption">Mass</Typography>
                </Box>
                <Typography variant="h6">{selectedPlanet.mass}</Typography>
                <Typography variant="caption" color="text.secondary">Earth masses</Typography>
              </Box>

              <Box sx={{ bgcolor: 'secondary.light', p: 1.5, borderRadius: 2, flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Public fontSize="small" />
                  <Typography variant="caption">Radius</Typography>
                </Box>
                <Typography variant="h6">{selectedPlanet.radius}</Typography>
                <Typography variant="caption" color="text.secondary">Earth radii</Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Box sx={{ bgcolor: 'info.light', p: 1.5, borderRadius: 2, flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Thermostat fontSize="small" />
                  <Typography variant="caption">Temperature</Typography>
                </Box>
                <Typography variant="h6">{selectedPlanet.temperature} K</Typography>
                <Typography variant="caption" color="text.secondary">Kelvin</Typography>
              </Box>

              <Box sx={{ bgcolor: 'warning.light', p: 1.5, borderRadius: 2, flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <LocationOn fontSize="small" />
                  <Typography variant="caption">Distance</Typography>
                </Box>
                <Typography variant="h6">{selectedPlanet.distance}</Typography>
                <Typography variant="caption" color="text.secondary">Light years</Typography>
              </Box>
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Orbital Properties */}
            <Typography variant="h6" sx={{ mb: 2 }}>
              Orbital Properties
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Timeline fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">
                  Orbital Period
                </Typography>
              </Box>
              <Typography variant="h6">{selectedPlanet.orbitalPeriod} days</Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Star fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">
                  Semi-Major Axis
                </Typography>
              </Box>
              <Typography variant="h6">{selectedPlanet.semiMajorAxis} AU</Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography variant="body2" color="text.secondary">
                  Eccentricity
                </Typography>
              </Box>
              <Typography variant="h6">{selectedPlanet.eccentricity}</Typography>
            </Box>
          </Paper>

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={() => navigate('/visualization')}
          >
            View in 3D Visualization
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};
