import React from 'react';
import { Box, CircularProgress, Typography, LinearProgress } from '@mui/material';

const loadingVariants = {
  circular: ({ size = 40, message }) => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
      }}
    >
      <CircularProgress size={size} />
      {message && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 2 }}
        >
          {message}
        </Typography>
      )}
    </Box>
  ),

  linear: ({ message }) => (
    <Box sx={{ width: '100%' }}>
      <LinearProgress />
      {message && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1 }}
        >
          {message}
        </Typography>
      )}
    </Box>
  ),

  skeleton: ({ children }) => children,

  pulse: ({ width = '100%', height = '100px' }) => (
    <Box
      sx={{
        width,
        height,
        backgroundColor: 'background.paper',
        animation: 'pulse 1.5s infinite',
        '@keyframes pulse': {
          '0%': {
            opacity: 1,
          },
          '50%': {
            opacity: 0.5,
          },
          '100%': {
            opacity: 1,
          },
        },
      }}
    />
  ),
};

const LoadingState = ({
  variant = 'circular',
  fullPage = false,
  message,
  size,
  width,
  height,
  children,
}) => {
  const LoadingComponent = loadingVariants[variant];

  if (!LoadingComponent) {
    console.warn(`Unknown loading variant: ${variant}`);
    return null;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: fullPage ? '60vh' : 'auto',
        width: '100%',
      }}
    >
      <LoadingComponent
        message={message}
        size={size}
        width={width}
        height={height}
      >
        {children}
      </LoadingComponent>
    </Box>
  );
};

export default LoadingState;