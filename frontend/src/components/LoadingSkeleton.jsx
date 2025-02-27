import React from 'react';
import { Skeleton, Box, Grid, Paper } from '@mui/material';

export const LoadingSkeleton = ({ type = 'overview' }) => {
  const renderOverviewSkeleton = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Skeleton variant="text" width="40%" height={32} />
          <Box sx={{ mt: 2 }}>
            <Skeleton variant="text" width="70%" />
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="80%" />
            <Skeleton variant="text" width="50%" />
          </Box>
        </Paper>
      </Grid>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Skeleton variant="text" width="40%" height={32} />
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={4}>
              <Skeleton variant="rectangular" height={100} />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Skeleton variant="rectangular" height={100} />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Skeleton variant="rectangular" height={100} />
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderKeywordSkeleton = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Skeleton variant="text" width="40%" height={32} />
          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" width={100} height={32} />
            ))}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderReviewSkeleton = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Skeleton variant="text" width="40%" height={32} />
          <Box sx={{ mt: 2 }}>
            {[...Array(5)].map((_, i) => (
              <Box key={i} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Skeleton variant="text" width={50} />
                <Skeleton variant="rectangular" height={20} sx={{ ml: 1, flexGrow: 1 }} />
                <Skeleton variant="text" width={30} sx={{ ml: 1 }} />
              </Box>
            ))}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );

  switch (type) {
    case 'keywords':
      return renderKeywordSkeleton();
    case 'reviews':
      return renderReviewSkeleton();
    default:
      return renderOverviewSkeleton();
  }
};

export default LoadingSkeleton;