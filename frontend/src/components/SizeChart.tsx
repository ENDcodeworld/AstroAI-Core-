import React, { useMemo } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bubble, Scatter } from 'react-chartjs-2';
import type { Exoplanet } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface SizeChartProps {
  planets: Exoplanet[];
  height?: number;
}

export const SizeChart: React.FC<SizeChartProps> = ({ planets, height = 400 }) => {
  // Prepare data for scatter plot (Mass vs Radius)
  const scatterData = useMemo(() => {
    return {
      datasets: [
        {
          label: 'Exoplanets',
          data: planets.map(p => ({
            x: p.radius,
            y: p.mass,
            name: p.name,
            habitable: p.habitableZone,
          })),
          backgroundColor: planets.map(p => 
            p.habitableZone ? 'rgba(76, 175, 80, 0.6)' : 'rgba(255, 107, 107, 0.6)'
          ),
          borderColor: planets.map(p => 
            p.habitableZone ? 'rgba(76, 175, 80, 1)' : 'rgba(255, 107, 107, 1)'
          ),
          borderWidth: 1,
        },
        {
          label: 'Earth (Reference)',
          data: [{ x: 1, y: 1 }],
          backgroundColor: 'rgba(33, 150, 243, 0.8)',
          borderColor: 'rgba(33, 150, 243, 1)',
          borderWidth: 2,
          pointRadius: 8,
        },
      ],
    };
  }, [planets]);

  const scatterOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'Exoplanet Mass vs Radius Comparison',
        color: '#ffffff',
        font: { size: 16, weight: 'bold' as const },
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const point = context.raw;
            return `${point.name}: ${point.x} R⊕, ${point.y} M⊕`;
          },
        },
      },
      legend: {
        labels: { color: '#ffffff' },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Radius (Earth Radii)',
          color: '#ffffff',
        },
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
      },
      y: {
        title: {
          display: true,
          text: 'Mass (Earth Masses)',
          color: '#ffffff',
        },
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
      },
    },
  };

  // Prepare data for size comparison bubbles
  const bubbleData = useMemo(() => {
    const sorted = [...planets].sort((a, b) => b.radius - a.radius).slice(0, 10);
    
    return {
      datasets: [
        {
          label: 'Planet Size',
          data: sorted.map((p, index) => ({
            x: index,
            y: p.radius,
            r: Math.max(5, Math.min(30, p.radius * 3)),
            name: p.name,
            mass: p.mass,
            habitable: p.habitableZone,
          })),
          backgroundColor: sorted.map(p => 
            p.habitableZone ? 'rgba(76, 175, 80, 0.6)' : 'rgba(255, 107, 107, 0.6)'
          ),
          borderColor: sorted.map(p => 
            p.habitableZone ? 'rgba(76, 175, 80, 1)' : 'rgba(255, 107, 107, 1)'
          ),
          borderWidth: 2,
        },
      ],
    };
  }, [planets]);

  const bubbleOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'Top 10 Largest Exoplanets',
        color: '#ffffff',
        font: { size: 16, weight: 'bold' as const },
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const point = context.raw;
            return `${point.name}: ${point.y} R⊕, ${point.mass} M⊕`;
          },
        },
      },
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        title: {
          display: true,
          text: 'Radius (Earth Radii)',
          color: '#ffffff',
        },
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
      },
    },
  };

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
      <Paper
        elevation={3}
        sx={{
          p: 2,
          bgcolor: '#1a1a2e',
          height,
        }}
      >
        <Scatter data={scatterData} options={scatterOptions} />
      </Paper>

      <Paper
        elevation={3}
        sx={{
          p: 2,
          bgcolor: '#1a1a2e',
          height,
        }}
      >
        <Bubble data={bubbleData} options={bubbleOptions} />
      </Paper>

      {/* Size comparison info */}
      <Paper
        elevation={3}
        sx={{
          p: 3,
          bgcolor: '#1a1a2e',
          gridColumn: { xs: '1fr', md: '1 / -1' },
        }}
      >
        <Typography variant="h6" sx={{ mb: 2, color: '#ffffff' }}>
          Size Reference
        </Typography>
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 20,
                height: 20,
                borderRadius: '50%',
                bgcolor: '#2196f3',
              }}
            />
            <Typography variant="body2" sx={{ color: '#ffffff' }}>
              Earth (1 R⊕, 1 M⊕)
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 20,
                height: 20,
                borderRadius: '50%',
                bgcolor: '#4caf50',
              }}
            />
            <Typography variant="body2" sx={{ color: '#ffffff' }}>
              Habitable Zone
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 20,
                height: 20,
                borderRadius: '50%',
                bgcolor: '#ff6b6b',
              }}
            />
            <Typography variant="body2" sx={{ color: '#ffffff' }}>
              Non-Habitable
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};
