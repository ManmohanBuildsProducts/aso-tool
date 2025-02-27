import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Component Error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onRetry) {
      this.props.onRetry();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            p: 3,
            textAlign: 'center',
            border: '1px solid #ffcdd2',
            borderRadius: 1,
            bgcolor: '#ffebee',
          }}
        >
          <Typography variant="h6" color="error" gutterBottom>
            Something went wrong
          </Typography>
          <Typography color="textSecondary" paragraph>
            {this.state.error?.message || 'An unexpected error occurred'}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<RefreshIcon />}
            onClick={this.handleRetry}
          >
            Retry
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;