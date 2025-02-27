import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tabs,
  Tab,
  Paper,
  Grid,
  Chip,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

const AppAnalyzer = () => {
  // State for main app and competitors
  const [mainApp, setMainApp] = useState({
    url: '',
    appId: '',
    loading: false,
  });
  
  const [competitors, setCompetitors] = useState([]);
  const [newCompetitorUrl, setNewCompetitorUrl] = useState('');
  const [editingIndex, setEditingIndex] = useState(-1);
  
  // State for analysis results
  const [analysisResults, setAnalysisResults] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  
  // Extract app ID from Play Store URL
  const extractAppId = (url) => {
    const match = url.match(/id=([^&]+)/);
    return match ? match[1] : '';
  };

  // Handle main app URL change
  const handleMainAppUrlChange = (event) => {
    const url = event.target.value;
    setMainApp({
      ...mainApp,
      url: url,
      appId: extractAppId(url),
    });
  };

  // Handle competitor management
  const handleAddCompetitor = () => {
    if (newCompetitorUrl) {
      const appId = extractAppId(newCompetitorUrl);
      if (appId) {
        setCompetitors([
          ...competitors,
          { url: newCompetitorUrl, appId, loading: false }
        ]);
        setNewCompetitorUrl('');
      }
    }
  };

  const handleEditCompetitor = (index) => {
    setEditingIndex(index);
  };

  const handleUpdateCompetitor = (index, newUrl) => {
    const updatedCompetitors = [...competitors];
    updatedCompetitors[index] = {
      url: newUrl,
      appId: extractAppId(newUrl),
      loading: false,
    };
    setCompetitors(updatedCompetitors);
    setEditingIndex(-1);
  };

  const handleDeleteCompetitor = (index) => {
    setCompetitors(competitors.filter((_, i) => i !== index));
  };

  // Handle analysis
  const handleAnalyze = async () => {
    if (!mainApp.appId) return;

    setMainApp({ ...mainApp, loading: true });
    setCompetitors(competitors.map(comp => ({ ...comp, loading: true })));

    try {
      // Call your backend API here
      const response = await fetch('/api/analyze/competitors/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          app_id: mainApp.appId,
          competitor_ids: competitors.map(comp => comp.appId),
        }),
      });

      const data = await response.json();
      setAnalysisResults(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setMainApp({ ...mainApp, loading: false });
      setCompetitors(competitors.map(comp => ({ ...comp, loading: false })));
    }
  };

  // Render functions
  const renderCompetitorList = () => (
    <List>
      {competitors.map((competitor, index) => (
        <ListItem key={index}>
          {editingIndex === index ? (
            <TextField
              fullWidth
              value={competitor.url}
              onChange={(e) => handleUpdateCompetitor(index, e.target.value)}
              variant="outlined"
              size="small"
            />
          ) : (
            <ListItemText
              primary={competitor.url}
              secondary={competitor.appId}
            />
          )}
          <ListItemSecondaryAction>
            {editingIndex === index ? (
              <>
                <IconButton
                  edge="end"
                  onClick={() => setEditingIndex(-1)}
                  size="small"
                >
                  <SaveIcon />
                </IconButton>
                <IconButton
                  edge="end"
                  onClick={() => setEditingIndex(-1)}
                  size="small"
                >
                  <CancelIcon />
                </IconButton>
              </>
            ) : (
              <>
                <IconButton
                  edge="end"
                  onClick={() => handleEditCompetitor(index)}
                  size="small"
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  edge="end"
                  onClick={() => handleDeleteCompetitor(index)}
                  size="small"
                >
                  <DeleteIcon />
                </IconButton>
              </>
            )}
          </ListItemSecondaryAction>
        </ListItem>
      ))}
    </List>
  );

  const renderAnalysisResults = () => {
    if (!analysisResults) return null;

    return (
      <Box mt={4}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Overview" />
          <Tab label="Keywords" />
          <Tab label="Reviews" />
          <Tab label="Metadata" />
          <Tab label="Performance" />
        </Tabs>

        <Box mt={2}>
          {activeTab === 0 && renderOverviewTab()}
          {activeTab === 1 && renderKeywordsTab()}
          {activeTab === 2 && renderReviewsTab()}
          {activeTab === 3 && renderMetadataTab()}
          {activeTab === 4 && renderPerformanceTab()}
        </Box>
      </Box>
    );
  };

  const renderOverviewTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6">Comparison Summary</Typography>
          {/* Add comparison charts and metrics */}
        </Paper>
      </Grid>
    </Grid>
  );

  const renderKeywordsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6">Keyword Analysis</Typography>
          {/* Add keyword comparison and trends */}
        </Paper>
      </Grid>
    </Grid>
  );

  const renderReviewsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6">Review Analysis</Typography>
          {/* Add review sentiment analysis and comparison */}
        </Paper>
      </Grid>
    </Grid>
  );

  const renderMetadataTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6">Metadata Analysis</Typography>
          {/* Add metadata comparison and optimization suggestions */}
        </Paper>
      </Grid>
    </Grid>
  );

  const renderPerformanceTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6">Performance Metrics</Typography>
          {/* Add performance metrics and trends */}
        </Paper>
      </Grid>
    </Grid>
  );

  return (
    <Container maxWidth="lg">
      <Box pt={2} pb={4}>
        <Typography variant="h4" gutterBottom>
          ASO Analysis Tool
        </Typography>

        {/* Main App Input */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Your App
            </Typography>
            <TextField
              fullWidth
              label="Play Store URL"
              value={mainApp.url}
              onChange={handleMainAppUrlChange}
              variant="outlined"
              placeholder="https://play.google.com/store/apps/details?id=your.app.id"
              sx={{ mb: 2 }}
            />
            {mainApp.appId && (
              <Chip
                label={`App ID: ${mainApp.appId}`}
                variant="outlined"
                size="small"
              />
            )}
          </CardContent>
        </Card>

        {/* Competitors Section */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Competitors
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                label="Add Competitor URL"
                value={newCompetitorUrl}
                onChange={(e) => setNewCompetitorUrl(e.target.value)}
                variant="outlined"
                placeholder="https://play.google.com/store/apps/details?id=competitor.app.id"
                sx={{ mb: 1 }}
              />
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddCompetitor}
                disabled={!newCompetitorUrl}
              >
                Add Competitor
              </Button>
            </Box>

            {renderCompetitorList()}
          </CardContent>
        </Card>

        {/* Analysis Button */}
        <Box sx={{ mb: 4 }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={handleAnalyze}
            disabled={!mainApp.appId || mainApp.loading}
            startIcon={mainApp.loading ? <CircularProgress size={20} /> : <RefreshIcon />}
          >
            {mainApp.loading ? 'Analyzing...' : 'Analyze'}
          </Button>
        </Box>

        {/* Analysis Results */}
        {renderAnalysisResults()}
      </Box>
    </Container>
  );
};

export default AppAnalyzer;