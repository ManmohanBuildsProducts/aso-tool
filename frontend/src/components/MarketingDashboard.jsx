import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Star,
  GetApp,
  RateReview,
  Speed,
} from '@mui/icons-material';

const MetricCard = ({ title, value, trend, description, icon: Icon }) => (
  <Card elevation={2}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Icon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6" component="div">
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" component="div" gutterBottom>
        {value}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        {trend > 0 ? (
          <TrendingUp color="success" />
        ) : trend < 0 ? (
          <TrendingDown color="error" />
        ) : (
          <TrendingFlat color="action" />
        )}
        <Typography
          variant="body2"
          color={trend > 0 ? 'success.main' : trend < 0 ? 'error.main' : 'text.secondary'}
          sx={{ ml: 1 }}
        >
          {trend > 0 ? '+' : ''}{trend}%
        </Typography>
      </Box>
      <Typography variant="body2" color="text.secondary">
        {description}
      </Typography>
    </CardContent>
  </Card>
);

const CompetitorComparison = ({ mainApp, competitors }) => (
  <Paper elevation={2} sx={{ p: 2 }}>
    <Typography variant="h6" gutterBottom>
      Competitive Analysis
    </Typography>
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1">Rating Comparison</Typography>
          {competitors.map((comp, index) => (
            <Box key={index} sx={{ mt: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">{comp.name}</Typography>
                <Typography variant="body2">{comp.rating}</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={(comp.rating / 5) * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                  },
                }}
              />
            </Box>
          ))}
        </Box>
      </Grid>
    </Grid>
  </Paper>
);

const KeywordInsights = ({ keywords }) => (
  <Paper elevation={2} sx={{ p: 2 }}>
    <Typography variant="h6" gutterBottom>
      Keyword Insights
    </Typography>
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
      {keywords.map((keyword, index) => (
        <Tooltip
          key={index}
          title={`Score: ${keyword.score}, Volume: ${keyword.volume}`}
        >
          <Chip
            label={keyword.term}
            color={keyword.score > 0.7 ? 'primary' : 'default'}
            size="small"
          />
        </Tooltip>
      ))}
    </Box>
  </Paper>
);

const MarketingDashboard = ({ data }) => {
  const {
    appMetrics,
    competitorData,
    keywordInsights,
    marketPosition,
  } = data;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Marketing Intelligence Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <MetricCard
            title="App Rating"
            value={appMetrics.rating}
            trend={appMetrics.ratingTrend}
            description="Overall app rating"
            icon={Star}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Installations"
            value={appMetrics.installs}
            trend={appMetrics.installsTrend}
            description="Total app installations"
            icon={GetApp}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Reviews"
            value={appMetrics.reviews}
            trend={appMetrics.reviewsTrend}
            description="Total user reviews"
            icon={RateReview}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Market Position"
            value={marketPosition.category}
            trend={marketPosition.trend}
            description="Current market standing"
            icon={Speed}
          />
        </Grid>

        {/* Competitor Analysis */}
        <Grid item xs={12}>
          <CompetitorComparison
            mainApp={appMetrics}
            competitors={competitorData}
          />
        </Grid>

        {/* Keyword Insights */}
        <Grid item xs={12}>
          <KeywordInsights keywords={keywordInsights} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default MarketingDashboard;