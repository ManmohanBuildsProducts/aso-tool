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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Button,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Star,
  GetApp,
  RateReview,
  Speed,
  Check,
  Warning,
  Lightbulb,
  Share,
  MonetizationOn,
  Assessment,
  Timeline,
  Info,
} from '@mui/icons-material';

const formatNumber = (num) => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

const formatPercentage = (num) => {
  return `${num.toFixed(1)}%`;
};

const formatCurrency = (num) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
};

const MetricCard = ({
  title,
  value,
  trend,
  description,
  icon: Icon,
  color = 'primary',
  size = 'medium',
}) => (
  <Card elevation={2}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Icon sx={{ mr: 1, color: `${color}.main` }} />
        <Typography variant="h6" component="div">
          {title}
        </Typography>
      </Box>
      <Typography
        variant={size === 'large' ? 'h3' : 'h4'}
        component="div"
        gutterBottom
        color={color === 'default' ? 'text.primary' : `${color}.main`}
      >
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
          <Typography variant="subtitle1" gutterBottom>Rating Comparison</Typography>
          <Box sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2">Your App</Typography>
              <Typography variant="body2">{mainApp.metrics.rating_score.toFixed(1)}</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={(mainApp.metrics.rating_score / 5) * 100}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  bgcolor: 'primary.main',
                },
              }}
            />
          </Box>
          
          {competitors.map((comp, index) => (
            <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">{comp.details.title}</Typography>
                <Typography variant="body2">{comp.metrics.rating_score.toFixed(1)}</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={(comp.metrics.rating_score / 5) * 100}
                sx={{
                  height: 10,
                  borderRadius: 5,
                  bgcolor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 5,
                    bgcolor: 'secondary.main',
                  },
                }}
              />
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {comp.comparison.rating_difference.percentage > 0 ? (
                    <span style={{ color: '#4caf50' }}>
                      +{comp.comparison.rating_difference.percentage.toFixed(1)}% higher
                    </span>
                  ) : (
                    <span style={{ color: '#f44336' }}>
                      {comp.comparison.rating_difference.percentage.toFixed(1)}% lower
                    </span>
                  )} than your app
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </Grid>

      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>Market Share</Typography>
        <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{ flexGrow: 1 }}>
              <LinearProgress
                variant="determinate"
                value={mainApp.market_share}
                sx={{
                  height: 20,
                  borderRadius: 2,
                  bgcolor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 2,
                    bgcolor: 'primary.main',
                  },
                }}
              />
            </Box>
            <Typography variant="body2" sx={{ ml: 2 }}>
              {mainApp.market_share.toFixed(1)}%
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            Your market share based on total installs
          </Typography>
        </Box>
      </Grid>
    </Grid>
  </Paper>
);

const MarketInsights = ({ marketAnalysis }) => (
  <Paper elevation={2} sx={{ p: 2 }}>
    <Typography variant="h6" gutterBottom>
      Market Insights
    </Typography>
    
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom color="success.main">
              <Check /> Strengths
            </Typography>
            <List dense>
              {marketAnalysis.competitive_analysis.strengths.map((strength, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Check color="success" />
                  </ListItemIcon>
                  <ListItemText primary={strength} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom color="error.main">
              <Warning /> Weaknesses
            </Typography>
            <List dense>
              {marketAnalysis.competitive_analysis.weaknesses.map((weakness, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Warning color="error" />
                  </ListItemIcon>
                  <ListItemText primary={weakness} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom color="info.main">
              <Lightbulb /> Opportunities
            </Typography>
            <List dense>
              {marketAnalysis.competitive_analysis.opportunities.map((opportunity, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Lightbulb color="info" />
                  </ListItemIcon>
                  <ListItemText primary={opportunity} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  </Paper>
);

const PerformanceMetrics = ({ metrics }) => (
  <Paper elevation={2} sx={{ p: 2 }}>
    <Typography variant="h6" gutterBottom>
      Performance Metrics
    </Typography>
    
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <MetricCard
          title="Review Quality"
          value={`${metrics.review_quality.toFixed(1)}`}
          trend={metrics.review_quality > 70 ? 15 : metrics.review_quality > 50 ? 5 : -5}
          description="Overall review quality score"
          icon={Star}
          color={metrics.review_quality > 70 ? 'success' : metrics.review_quality > 50 ? 'primary' : 'error'}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <MetricCard
          title="Engagement"
          value={`${metrics.engagement_score.toFixed(1)}`}
          trend={metrics.engagement_score > 70 ? 12 : metrics.engagement_score > 50 ? 3 : -8}
          description="User engagement score"
          icon={Speed}
          color={metrics.engagement_score > 70 ? 'success' : metrics.engagement_score > 50 ? 'primary' : 'error'}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <MetricCard
          title="Daily Installs"
          value={formatNumber(metrics.growth_metrics.daily_installs)}
          trend={metrics.growth_metrics.daily_installs > 1000 ? 10 : metrics.growth_metrics.daily_installs > 500 ? 5 : 0}
          description="Estimated daily installations"
          icon={GetApp}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <MetricCard
          title="Monthly Revenue"
          value={formatCurrency(metrics.estimated_revenue.estimated_total_revenue)}
          trend={metrics.estimated_revenue.estimated_total_revenue > 10000 ? 20 : metrics.estimated_revenue.estimated_total_revenue > 5000 ? 10 : 0}
          description="Estimated monthly revenue"
          icon={MonetizationOn}
          color="success"
        />
      </Grid>
    </Grid>
  </Paper>
);

const MarketingDashboard = ({ data }) => {
  const {
    main_app,
    competitors,
    market_analysis,
    metrics_comparison,
  } = data;

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Marketing Intelligence Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive analysis of your app's market position and competitive landscape
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12}>
          <PerformanceMetrics metrics={main_app.metrics} />
        </Grid>

        {/* Market Position */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Market Position
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Assessment sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h5" color="primary">
                {market_analysis.market_position}
              </Typography>
            </Box>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>Rating Percentile</Typography>
                  <Typography variant="h6">{formatPercentage(market_analysis.percentiles.rating)}</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={market_analysis.percentiles.rating}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>Install Percentile</Typography>
                  <Typography variant="h6">{formatPercentage(market_analysis.percentiles.installs)}</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={market_analysis.percentiles.installs}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>Engagement Percentile</Typography>
                  <Typography variant="h6">{formatPercentage(market_analysis.percentiles.engagement)}</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={market_analysis.percentiles.engagement}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>Overall Percentile</Typography>
                  <Typography variant="h6">{formatPercentage(market_analysis.percentiles.overall)}</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={market_analysis.percentiles.overall}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Competitor Analysis */}
        <Grid item xs={12}>
          <CompetitorComparison
            mainApp={main_app}
            competitors={competitors}
          />
        </Grid>

        {/* Market Insights */}
        <Grid item xs={12}>
          <MarketInsights marketAnalysis={market_analysis} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default MarketingDashboard;