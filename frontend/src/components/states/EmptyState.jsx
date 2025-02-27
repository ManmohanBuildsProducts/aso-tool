import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Search as SearchIcon, Refresh as RefreshIcon, Error as ErrorIcon } from '@mui/icons-material';

const illustrations = {
  search: SearchIcon,
  refresh: RefreshIcon,
  error: ErrorIcon,
};

const EmptyState = ({
  type = 'default',
  title = 'No Data Available',
  message = 'There is no data to display at the moment.',
  actionText,
  onAction,
  icon = 'search',
  customIcon,
}) => {
  const IconComponent = customIcon || illustrations[icon];

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
        textAlign: 'center',
        minHeight: type === 'fullPage' ? '60vh' : '300px',
        backgroundColor: 'background.paper',
        borderRadius: 1,
      }}
    >
      <IconComponent
        sx={{
          fontSize: 64,
          color: 'text.secondary',
          mb: 2,
          opacity: 0.5,
        }}
      />
      
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      
      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ maxWidth: 400, mb: 3 }}
      >
        {message}
      </Typography>

      {actionText && onAction && (
        <Button
          variant="contained"
          onClick={onAction}
          startIcon={<RefreshIcon />}
        >
          {actionText}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;