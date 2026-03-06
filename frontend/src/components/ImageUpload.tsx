import React, { useRef, useCallback } from 'react';
import { Box, Button, Typography, Paper, alpha } from '@mui/material';
import { CloudUpload, Image as ImageIcon } from '@mui/icons-material';
import { useClassificationStore } from '../store';

interface ImageUploadProps {
  onUpload?: (files: File[]) => void;
  multiple?: boolean;
  accept?: string;
  maxFiles?: number;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  onUpload,
  multiple = true,
  accept = 'image/*',
  maxFiles = 10,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const uploadImage = useClassificationStore((state) => state.uploadImage);
  const uploadMultiple = useClassificationStore((state) => state.uploadMultiple);
  const processing = useClassificationStore((state) => state.processing);
  const uploading = useClassificationStore((state) => state.uploading);

  const handleFileSelect = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    
    if (!files || files.length === 0) return;

    const fileArray = Array.from(files).slice(0, maxFiles);

    if (onUpload) {
      onUpload(fileArray);
    } else {
      if (fileArray.length === 1) {
        await uploadImage(fileArray[0]);
      } else {
        await uploadMultiple(fileArray);
      }
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [onUpload, uploadImage, uploadMultiple, maxFiles]);

  const handleDrop = useCallback(async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    const files = event.dataTransfer.files;
    
    if (!files || files.length === 0) return;

    const imageFiles = Array.from(files)
      .filter(file => file.type.startsWith('image/'))
      .slice(0, maxFiles);

    if (imageFiles.length === 0) return;

    if (onUpload) {
      onUpload(imageFiles);
    } else {
      if (imageFiles.length === 1) {
        await uploadImage(imageFiles[0]);
      } else {
        await uploadMultiple(imageFiles);
      }
    }
  }, [onUpload, uploadImage, uploadMultiple, maxFiles]);

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  }, []);

  return (
    <Paper
      variant="outlined"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      sx={{
        p: 4,
        textAlign: 'center',
        borderStyle: 'dashed',
        borderWidth: 2,
        borderColor: 'primary.main',
        bgcolor: alpha('#1976d2', 0.05),
        transition: 'all 0.2s',
        '&:hover': {
          borderColor: 'primary.dark',
          bgcolor: alpha('#1976d2', 0.1),
        },
      }}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />

      <CloudUpload 
        sx={{ 
          fontSize: 64, 
          color: 'primary.main', 
          mb: 2,
          opacity: processing || uploading ? 0.5 : 1,
        }} 
      />

      <Typography variant="h6" gutterBottom>
        {processing || uploading ? 'Processing...' : 'Upload Astronomical Images'}
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Drag and drop images here, or click to browse
      </Typography>

      <Typography variant="caption" color="text.secondary">
        Supports: JPG, PNG, GIF, WebP • Max {maxFiles} files
      </Typography>

      <Box sx={{ mt: 3 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => fileInputRef.current?.click()}
          disabled={processing || uploading}
          startIcon={<ImageIcon />}
        >
          Select Images
        </Button>
      </Box>

      {multiple && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
          Hold Ctrl/Cmd to select multiple files
        </Typography>
      )}
    </Paper>
  );
};
