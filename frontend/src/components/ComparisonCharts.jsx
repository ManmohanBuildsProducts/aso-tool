import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

const ComparisonCharts = ({ data }) => {
  // Format data for charts
  const formatMetricsData = () => {
    if (!data) return [];
    
    const { main_app, competitors } = data;
    return [
      {
        name: main_app.app_id,
        ratings: main_app.details.score,
        installs: main_app.details.minInstalls,
        reviews: main_app.details.reviews,
      },
      ...competitors.map(comp => ({
        name: comp.app_id,
        ratings: comp.details.score,
        installs: comp.details.minInstalls,
        reviews: comp.details.reviews,
      })),
    ];
  };

  const formatKeywordData = () => {
    if (!data?.keyword_analysis) return [];
    
    return Object.entries(data.keyword_analysis.keyword_trends).map(([keyword, details]) => ({
      keyword,
      difficulty: details.difficulty_score,
      volume: details.search_volume === 'High' ? 80 : 
              details.search_volume === 'Medium' ? 60 :
              details.search_volume === 'Low' ? 40 : 20,
    }));
  };

  const formatReviewData = () => {
    if (!data?.review_analysis) return [];
    
    return Object.entries(data.review_analysis.sentiment_trends).map(([date, sentiment]) => ({
      date,
      sentiment: sentiment.compound * 100,
    }));
  };

  return (
    <Box>
      {/* Key Metrics Comparison */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Key Metrics Comparison
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={formatMetricsData()}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="ratings" fill="#8884d8" name="Ratings" />
            <Bar dataKey="installs" fill="#82ca9d" name="Installs" />
            <Bar dataKey="reviews" fill="#ffc658" name="Reviews" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Keyword Analysis */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Keyword Difficulty
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={formatKeywordData()}>
                <PolarGrid />
                <PolarAngleAxis dataKey="keyword" />
                <PolarRadiusAxis />
                <Radar
                  name="Difficulty"
                  dataKey="difficulty"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
                <Radar
                  name="Volume"
                  dataKey="volume"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  fillOpacity={0.6}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Review Sentiment Trends
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formatReviewData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="sentiment"
                  stroke="#8884d8"
                  name="Sentiment Score"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComparisonCharts;