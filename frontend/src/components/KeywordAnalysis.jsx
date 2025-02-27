import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';

const KeywordAnalysis = ({ data }) => {
  const formatKeywordData = () => {
    if (!data?.keyword_analysis) return [];
    
    return Object.entries(data.keyword_analysis.keyword_trends).map(([keyword, details]) => ({
      keyword,
      difficulty: details.difficulty_score,
      volume: details.search_volume === 'High' ? 100 :
              details.search_volume === 'Medium' ? 70 :
              details.search_volume === 'Low' ? 40 : 10,
      potential: details.ranking_potential === 'High' ? 100 :
                details.ranking_potential === 'Medium' ? 70 :
                details.ranking_potential === 'Low' ? 40 : 10,
    }));
  };

  const renderKeywordTable = () => (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Keyword</TableCell>
            <TableCell>Difficulty</TableCell>
            <TableCell>Search Volume</TableCell>
            <TableCell>Ranking Potential</TableCell>
            <TableCell>Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {formatKeywordData().map((keyword) => (
            <TableRow key={keyword.keyword}>
              <TableCell>{keyword.keyword}</TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={keyword.difficulty}
                      sx={{
                        height: 10,
                        borderRadius: 5,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: 
                            keyword.difficulty > 80 ? '#f44336' :
                            keyword.difficulty > 60 ? '#ff9800' :
                            keyword.difficulty > 40 ? '#ffc107' : '#4caf50',
                        },
                      }}
                    />
                  </Box>
                  <Box sx={{ minWidth: 35 }}>
                    <Typography variant="body2" color="text.secondary">
                      {`${Math.round(keyword.difficulty)}%`}
                    </Typography>
                  </Box>
                </Box>
              </TableCell>
              <TableCell>
                <Chip
                  label={keyword.volume >= 80 ? 'High' :
                         keyword.volume >= 50 ? 'Medium' : 'Low'}
                  color={keyword.volume >= 80 ? 'success' :
                         keyword.volume >= 50 ? 'warning' : 'error'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Chip
                  label={keyword.potential >= 80 ? 'High' :
                         keyword.potential >= 50 ? 'Medium' : 'Low'}
                  color={keyword.potential >= 80 ? 'success' :
                         keyword.potential >= 50 ? 'warning' : 'error'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Tooltip title={getKeywordRecommendation(keyword)}>
                  <Chip
                    label={getKeywordStatus(keyword)}
                    color={getKeywordStatusColor(keyword)}
                    size="small"
                  />
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const getKeywordStatus = (keyword) => {
    const score = (keyword.potential + (100 - keyword.difficulty) + keyword.volume) / 3;
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  const getKeywordStatusColor = (keyword) => {
    const status = getKeywordStatus(keyword);
    switch (status) {
      case 'Excellent': return 'success';
      case 'Good': return 'primary';
      case 'Fair': return 'warning';
      default: return 'error';
    }
  };

  const getKeywordRecommendation = (keyword) => {
    if (keyword.difficulty > 80 && keyword.volume < 50)
      return 'Consider alternative keywords with lower difficulty';
    if (keyword.difficulty < 40 && keyword.volume > 80)
      return 'Great opportunity - prioritize this keyword';
    if (keyword.potential > 80)
      return 'Good ranking potential - optimize for this keyword';
    return 'Monitor and optimize based on performance';
  };

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Keyword Analysis
            </Typography>
            {renderKeywordTable()}
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Keyword Metrics Visualization
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={formatKeywordData()}>
                <PolarGrid />
                <PolarAngleAxis dataKey="keyword" />
                <PolarRadiusAxis />
                <Radar
                  name="Difficulty"
                  dataKey="difficulty"
                  stroke="#f44336"
                  fill="#f44336"
                  fillOpacity={0.3}
                />
                <Radar
                  name="Search Volume"
                  dataKey="volume"
                  stroke="#2196f3"
                  fill="#2196f3"
                  fillOpacity={0.3}
                />
                <Radar
                  name="Ranking Potential"
                  dataKey="potential"
                  stroke="#4caf50"
                  fill="#4caf50"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default KeywordAnalysis;