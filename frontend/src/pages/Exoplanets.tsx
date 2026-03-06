import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Pagination,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Search, FilterList, Sort } from '@mui/icons-material';
import { PlanetCard } from '../components/PlanetCard';
import { useExoplanetStore } from '../store';

export const Exoplanets: React.FC = () => {
  const {
    filteredPlanets,
    planets,
    filters,
    currentPage,
    itemsPerPage,
    loading,
    error,
    updateFilters,
    resetFilters,
    setCurrentPage,
    fetchPlanets,
  } = useExoplanetStore();

  useEffect(() => {
    fetchPlanets();
  }, [fetchPlanets]);

  const totalPages = Math.ceil(filteredPlanets.length / itemsPerPage);
  const paginatedPlanets = filteredPlanets.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const constellations = Array.from(new Set(planets.map(p => p.constellation))).sort();
  const discoveryMethods = Array.from(new Set(planets.map(p => p.discoveryMethod))).sort();

  const handlePageChange = (_: React.ChangeEvent<unknown>, page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
          Exoplanet Browser
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Explore discovered worlds beyond our solar system
        </Typography>
      </Box>

      {/* Filters */}
      <Box
        sx={{
          mb: 4,
          p: 3,
          bgcolor: 'background.paper',
          borderRadius: 2,
          boxShadow: 1,
        }}
      >
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search planets, stars, constellations..."
              value={filters.search}
              onChange={(e) => updateFilters({ search: e.target.value })}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Constellation</InputLabel>
              <Select
                value={filters.constellation}
                label="Constellation"
                onChange={(e) => updateFilters({ constellation: e.target.value })}
              >
                <MenuItem value="">All</MenuItem>
                {constellations.map(c => (
                  <MenuItem key={c} value={c}>{c}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Discovery Method</InputLabel>
              <Select
                value={filters.discoveryMethod}
                label="Discovery Method"
                onChange={(e) => updateFilters({ discoveryMethod: e.target.value })}
              >
                <MenuItem value="">All</MenuItem>
                {discoveryMethods.map(m => (
                  <MenuItem key={m} value={m}>{m}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Sort By</InputLabel>
              <Select
                value={filters.sortBy}
                label="Sort By"
                onChange={(e) => updateFilters({ sortBy: e.target.value as any })}
                startAdornment={
                  <InputAdornment position="start">
                    <Sort />
                  </InputAdornment>
                }
              >
                <MenuItem value="name">Name</MenuItem>
                <MenuItem value="distance">Distance</MenuItem>
                <MenuItem value="mass">Mass</MenuItem>
                <MenuItem value="discoveryYear">Discovery Year</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={filters.habitableOnly}
                  onChange={(e) => updateFilters({ habitableOnly: e.target.checked })}
                  color="success"
                />
              }
              label="Habitable Only"
            />
          </Grid>

          <Grid item xs={12} md={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Showing {filteredPlanets.length} of {planets.length} planets
              </Typography>
              {(filters.search || filters.constellation || filters.discoveryMethod || filters.habitableOnly) && (
                <Typography
                  variant="caption"
                  color="primary"
                  sx={{ cursor: 'pointer' }}
                  onClick={resetFilters}
                >
                  Clear Filters
                </Typography>
              )}
            </Box>
          </Grid>
        </Grid>
      </Box>

      {/* Content */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress size={60} />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
      ) : filteredPlanets.length === 0 ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          No planets found matching your criteria
        </Alert>
      ) : (
        <>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {paginatedPlanets.map(planet => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={planet.id}>
                <PlanetCard planet={planet} />
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={totalPages}
                page={currentPage}
                onChange={handlePageChange}
                color="primary"
                size="large"
                showFirstButton
                showLastButton
              />
            </Box>
          )}
        </>
      )}
    </Box>
  );
};
