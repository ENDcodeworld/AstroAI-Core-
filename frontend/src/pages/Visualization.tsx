import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import { ViewList, ViewModule, Assessment } from '@mui/icons-material';
import { SizeChart } from '../components/SizeChart';
import { useExoplanetStore } from '../store';

type ViewMode = 'chart' | 'grid' | 'stats';

export const Visualization: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('chart');
  const [selectedConstellation, setSelectedConstellation] = useState<string>('all');
  const { planets } = useExoplanetStore();

  const constellations = Array.from(new Set(planets.map(p => p.constellation))).sort();

  const filteredPlanets = selectedConstellation === 'all'
    ? planets
    : planets.filter(p => p.constellation === selectedConstellation);

  const handleViewChange = (_: React.MouseEvent<HTMLElement>, newView: ViewMode | null) => {
    if (newView !== null) {
      setViewMode(newView);
    }
  };

  // Calculate statistics
  const stats = {
    total: planets.length,
    habitable: planets.filter(p => p.habitableZone).length,
    avgDistance: planets.reduce((sum, p) => sum + p.distance, 0) / planets.length,
    avgMass: planets.reduce((sum, p) => sum + p.mass, 0) / planets.length,
    closest: Math.min(...planets.map(p => p.distance)),
    farthest: Math.max(...planets.map(p => p.distance)),
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
          Data Visualization
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Interactive charts and visualizations of exoplanet data
        </Typography>
      </Box>

      {/* Controls */}
      <Paper elevation={3} sx={{ p: 2, mb: 4, borderRadius: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Constellation</InputLabel>
              <Select
                value={selectedConstellation}
                label="Constellation"
                onChange={(e) => setSelectedConstellation(e.target.value)}
              >
                <MenuItem value="all">All Constellations</MenuItem>
                {constellations.map(c => (
                  <MenuItem key={c} value={c}>{c}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={9}>
            <Box sx={{ display: 'flex', justifyContent: { xs: 'flex-start', sm: 'flex-end' } }}>
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={handleViewChange}
                size="small"
              >
                <ToggleButton value="chart">
                  <Assessment sx={{ mr: 1 }} />
                  Charts
                </ToggleButton>
                <ToggleButton value="grid">
                  <ViewModule sx={{ mr: 1 }} />
                  Grid
                </ToggleButton>
                <ToggleButton value="stats">
                  <ViewList sx={{ mr: 1 }} />
                  Statistics
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Content based on view mode */}
      {viewMode === 'chart' && (
        <SizeChart planets={filteredPlanets} height={500} />
      )}

      {viewMode === 'stats' && (
        <Grid container spacing={3}>
          {/* Overview Stats */}
          <Grid item xs={12} md={6} lg={3}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2, textAlign: 'center' }}>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                {stats.total}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Exoplanets
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2, textAlign: 'center' }}>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {stats.habitable}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                In Habitable Zone
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2, textAlign: 'center' }}>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                {stats.avgDistance.toFixed(0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Distance (ly)
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2, textAlign: 'center' }}>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                {stats.avgMass.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Mass (M⊕)
              </Typography>
            </Paper>
          </Grid>

          {/* Distance Range */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Distance Range
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Closest
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  {stats.closest} light years
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Farthest
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  {stats.farthest} light years
                </Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Distribution by Discovery Method */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Discovery Methods
              </Typography>
              {Array.from(new Set(planets.map(p => p.discoveryMethod))).map(method => {
                const count = planets.filter(p => p.discoveryMethod === method).length;
                const percentage = (count / planets.length) * 100;
                
                return (
                  <Box key={method} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2">{method}</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {count} ({percentage.toFixed(0)}%)
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        height: 8,
                        bgcolor: 'background.default',
                        borderRadius: 4,
                        overflow: 'hidden',
                      }}
                    >
                      <Box
                        sx={{
                          height: '100%',
                          width: `${percentage}%`,
                          bgcolor: 'primary.main',
                          borderRadius: 4,
                        }}
                      />
                    </Box>
                  </Box>
                );
              })}
            </Paper>
          </Grid>

          {/* Constellation Distribution */}
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Distribution by Constellation
              </Typography>
              <Grid container spacing={2}>
                {constellations.map(constellation => {
                  const count = planets.filter(p => p.constellation === constellation).length;
                  return (
                    <Grid item xs={6} sm={4} md={3} lg={2} key={constellation}>
                      <Box
                        sx={{
                          p: 2,
                          bgcolor: 'background.default',
                          borderRadius: 2,
                          textAlign: 'center',
                        }}
                      >
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {count}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {constellation}
                        </Typography>
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}

      {viewMode === 'grid' && (
        <Grid container spacing={3}>
          {filteredPlanets.map(planet => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={planet.id}>
              <Paper
                elevation={3}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <Box
                  sx={{
                    height: 120,
                    borderRadius: 2,
                    mb: 2,
                    background: `linear-gradient(135deg, ${
                      planet.habitableZone 
                        ? 'rgba(76, 175, 80, 0.3)' 
                        : 'rgba(255, 107, 107, 0.3)'
                    } 0%, rgba(26, 26, 46, 1) 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Box
                    sx={{
                      width: 40 + planet.radius * 8,
                      height: 40 + planet.radius * 8,
                      borderRadius: '50%',
                      background: planet.habitableZone 
                        ? 'linear-gradient(135deg, #4caf50 0%, #2196f3 100%)'
                        : 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)',
                      boxShadow: '0 0 20px rgba(255, 255, 255, 0.3)',
                    }}
                  />
                </Box>

                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {planet.name}
                </Typography>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {planet.hostStar}
                </Typography>

                <Box sx={{ mt: 'auto' }}>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Distance
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {planet.distance} ly
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Mass
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {planet.mass} M⊕
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Radius
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {planet.radius} R⊕
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Period
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {planet.orbitalPeriod}d
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};
