import React from 'react';
import { Card, CardContent, Typography, Chip, Box } from '@mui/material';
import { LocationOn, Timeline, FitnessCenter, Public } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import type { Exoplanet } from '../types';

interface PlanetCardProps {
  planet: Exoplanet;
}

export const PlanetCard: React.FC<PlanetCardProps> = ({ planet }) => {
  const navigate = useNavigate();

  const handleCardClick = () => {
    navigate(`/exoplanets/${planet.id}`);
  };

  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6,
          cursor: 'pointer',
        },
      }}
      onClick={handleCardClick}
    >
      <Box
        sx={{
          height: 160,
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Planet visualization */}
        <Box
          sx={{
            width: 80 + planet.radius * 10,
            height: 80 + planet.radius * 10,
            borderRadius: '50%',
            background: planet.habitableZone 
              ? 'linear-gradient(135deg, #4caf50 0%, #2196f3 100%)'
              : 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)',
            boxShadow: '0 0 30px rgba(255, 255, 255, 0.3)',
            position: 'relative',
          }}
        >
          {/* Atmosphere glow */}
          <Box
            sx={{
              position: 'absolute',
              top: -5,
              left: -5,
              right: -5,
              bottom: -5,
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
            }}
          />
        </Box>
      </Box>

      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold' }}>
            {planet.name}
          </Typography>
          {planet.habitableZone && (
            <Chip 
              label="Habitable" 
              size="small" 
              color="success" 
              sx={{ height: 20 }}
            />
          )}
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {planet.hostStar} • {planet.constellation}
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <LocationOn fontSize="small" color="action" />
            <Typography variant="caption">{planet.distance} ly</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <FitnessCenter fontSize="small" color="action" />
            <Typography variant="caption">{planet.mass} M⊕</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Public fontSize="small" color="action" />
            <Typography variant="caption">{planet.radius} R⊕</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Timeline fontSize="small" color="action" />
            <Typography variant="caption">{planet.orbitalPeriod}d</Typography>
          </Box>
        </Box>
      </CardContent>

      <CardActions>
        <Typography variant="caption" color="text.secondary">
          Discovered {planet.discoveryYear} • {planet.discoveryMethod}
        </Typography>
      </CardActions>
    </Card>
  );
};
