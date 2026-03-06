import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  IconButton,
  Divider,
  Alert,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  History as HistoryIcon,
  ClearAll as ClearAllIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ImageUpload } from '../components/ImageUpload';
import { useClassificationStore } from '../store';

export const ImageClassifier: React.FC = () => {
  const [view, setView] = useState<'upload' | 'history'>('upload');
  const {
    results,
    currentResult,
    processing,
    uploadImage,
    setCurrentResult,
    clearHistory,
  } = useClassificationStore();

  const handleFileUpload = async (files: File[]) => {
    for (const file of files) {
      try {
        await uploadImage(file);
      } catch (error) {
        console.error('Upload failed:', error);
      }
    }
  };

  const handleDeleteResult = (id: string) => {
    // In a real app, you'd filter from the store
    console.log('Delete result:', id);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
          AI Image Classifier
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Classify astronomical images using deep learning
        </Typography>
      </Box>

      {/* View Toggle */}
      <Box sx={{ mb: 3, display: 'flex', gap: 1 }}>
        <Button
          variant={view === 'upload' ? 'contained' : 'outlined'}
          onClick={() => setView('upload')}
          startIcon={<HistoryIcon />}
        >
          Upload & Classify
        </Button>
        <Button
          variant={view === 'history' ? 'contained' : 'outlined'}
          onClick={() => setView('history')}
          startIcon={<HistoryIcon />}
        >
          History ({results.length})
        </Button>
        {results.length > 0 && (
          <Button
            variant="outlined"
            color="error"
            onClick={clearHistory}
            startIcon={<ClearAllIcon />}
            sx={{ ml: 'auto' }}
          >
            Clear All
          </Button>
        )}
      </Box>

      {view === 'upload' ? (
        <Grid container spacing={4}>
          {/* Upload Section */}
          <Grid item xs={12} lg={6}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
              <Typography variant="h6" sx={{ mb: 3 }}>
                Upload Images
              </Typography>
              <ImageUpload onUpload={handleFileUpload} multiple maxFiles={10} />
              
              {processing && (
                <Box sx={{ mt: 3 }}>
                  <LinearProgress />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                    Analyzing image...
                  </Typography>
                </Box>
              )}
            </Paper>

            {/* Instructions */}
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2, mt: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Supported Categories
              </Typography>
              <Grid container spacing={1}>
                {['Galaxies', 'Nebulae', 'Star Clusters', 'Supernova Remnants', 'Planetary Nebulae'].map((cat) => (
                  <Grid item xs={6} sm={4} key={cat}>
                    <Chip label={cat} variant="outlined" size="small" sx={{ width: '100%' }} />
                  </Grid>
                ))}
              </Grid>
              
              <Alert severity="info" sx={{ mt: 3 }}>
                Upload clear astronomical images for best classification results. 
                The AI model is trained on professional telescope imagery.
              </Alert>
            </Paper>
          </Grid>

          {/* Current Result */}
          <Grid item xs={12} lg={6}>
            {currentResult ? (
              <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Classification Result
                </Typography>

                <Card sx={{ mb: 3 }}>
                  <CardMedia
                    component="img"
                    height="300"
                    image={currentResult.imageUrl}
                    alt="Classified image"
                    sx={{ bgcolor: '#000' }}
                  />
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <CheckCircleIcon color="success" />
                      <Typography variant="h6">{currentResult.className}</Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2" color="text.secondary">
                          Confidence
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {(currentResult.confidence * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={currentResult.confidence * 100}
                        color="success"
                      />
                    </Box>

                    <Typography variant="caption" color="text.secondary">
                      Classified on {format(currentResult.timestamp, 'PPpp')}
                    </Typography>
                  </CardContent>
                </Card>

                {/* Alternative Classes */}
                {currentResult.alternativeClasses.length > 0 && (
                  <>
                    <Divider sx={{ mb: 2 }} />
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Alternative Classifications
                    </Typography>
                    {currentResult.alternativeClasses.map((alt, index) => (
                      <Box key={index} sx={{ mb: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="body2">{alt.class}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {(alt.confidence * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={alt.confidence * 100}
                          sx={{ height: 4, borderRadius: 2 }}
                        />
                      </Box>
                    ))}
                  </>
                )}
              </Paper>
            ) : (
              <Paper
                elevation={3}
                sx={{
                  p: 6,
                  borderRadius: 2,
                  textAlign: 'center',
                  bgcolor: 'background.default',
                }}
              >
                <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
                  No Image Classified Yet
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Upload an image to see classification results here
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      ) : (
        /* History View */
        <Grid container spacing={3}>
          {results.length === 0 ? (
            <Grid item xs={12}>
              <Paper
                elevation={3}
                sx={{ p: 6, borderRadius: 2, textAlign: 'center' }}
              >
                <Typography variant="h6" color="text.secondary">
                  No classification history
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Your classified images will appear here
                </Typography>
              </Paper>
            </Grid>
          ) : (
            results.map((result) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={result.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardMedia
                    component="img"
                    height="200"
                    image={result.imageUrl}
                    alt={result.className}
                    sx={{ bgcolor: '#000' }}
                  />
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {result.className}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Chip
                        label={`${(result.confidence * 100).toFixed(0)}%`}
                        size="small"
                        color={result.confidence > 0.7 ? 'success' : 'warning'}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {format(result.timestamp, 'PPp')}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => setCurrentResult(result)}
                    >
                      View Details
                    </Button>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteResult(result.id)}
                      sx={{ ml: 'auto' }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}
    </Box>
  );
};
