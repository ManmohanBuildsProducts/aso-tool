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
  LinearProgress,
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
      // Get main app analysis
      const appResponse = await fetch(`/api/analyze/app/${mainApp.appId}`);
      if (!appResponse.ok) throw new Error('App analysis failed');
      const appData = await appResponse.json();
      console.log('App analysis:', appData);

      // Get competitor analysis if there are competitors
      let competitorData = null;
      if (competitors.length > 0) {
        const competitorResponse = await fetch('/api/analyze/competitors/compare', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            app_id: mainApp.appId,
            competitor_ids: competitors.map(comp => comp.appId),
          }),
        });
        if (!competitorResponse.ok) throw new Error('Competitor analysis failed');
        competitorData = await competitorResponse.json();
        console.log('Competitor analysis:', competitorData);
      }

      // Get keyword analysis
      const keywordResponse = await fetch('/api/analyze/keywords/discover', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          app_id: mainApp.appId,
          competitor_ids: competitors.map(comp => comp.appId),
        }),
      });
      if (!keywordResponse.ok) throw new Error('Keyword analysis failed');
      const keywordData = await keywordResponse.json();
      console.log('Keyword analysis:', keywordData);

      setAnalysisResults({
        appAnalysis: appData,
        competitorAnalysis: competitorData,
        keywordAnalysis: keywordData
      });
      setActiveTab(0); // Switch to Overview tab after analysis
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed: ' + error.message);
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
          {activeTab === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>App Overview</Typography>
                  {analysisResults.appAnalysis && (
                    <>
                      <Typography><strong>Title:</strong> {analysisResults.appAnalysis.data.title}</Typography>
                      <Typography><strong>Installs:</strong> {analysisResults.appAnalysis.data.installs}</Typography>
                      <Typography><strong>Rating:</strong> {analysisResults.appAnalysis.data.score || 'N/A'}</Typography>
                      <Typography><strong>Reviews:</strong> {analysisResults.appAnalysis.data.reviews || 'N/A'}</Typography>
                    </>
                  )}
                </Paper>
              </Grid>
              {analysisResults.competitorAnalysis && (
                <Grid item xs={12}>
                  <Paper elevation={2} sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Competitor Analysis</Typography>
                    {analysisResults.competitorAnalysis.comparison.competitors.map((comp, index) => (
                      <Box key={index} mb={2}>
                        <Typography><strong>{comp.app_id}</strong></Typography>
                        <Typography>Installs: {comp.details.installs}</Typography>
                        <Typography>Rating: {comp.details.score || 'N/A'}</Typography>
                      </Box>
                    ))}
                  </Paper>
                </Grid>
              )}
            </Grid>
          )}
          {activeTab === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Keyword Analysis</Typography>
                  {analysisResults.keywordAnalysis && (
                    <Box>
                      <Typography variant="subtitle1" gutterBottom>Top Keywords:</Typography>
                      {Object.entries(analysisResults.keywordAnalysis.analysis.top_keywords || {}).map(([keyword, score]) => (
                        <Chip 
                          key={keyword}
                          label={`${keyword}: ${(score * 100).toFixed(1)}%`}
                          sx={{ m: 0.5 }}
                        />
                      ))}
                    </Box>
                  )}
                </Paper>
              </Grid>
            </Grid>
          )}
          {activeTab === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Review Analysis</Typography>
                  {analysisResults.appAnalysis && (
                    <Box>
                      <Typography><strong>Total Reviews:</strong> {analysisResults.appAnalysis.data.reviews || 'N/A'}</Typography>
                      <Typography><strong>Rating Distribution:</strong></Typography>
                      {analysisResults.appAnalysis.data.histogram && (
                        <Box sx={{ mt: 1 }}>
                          {analysisResults.appAnalysis.data.histogram.map((count, index) => (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              <Typography sx={{ minWidth: 70 }}>{5 - index} stars:</Typography>
                              <LinearProgress 
                                variant="determinate" 
                                value={(count / Math.max(...analysisResults.appAnalysis.data.histogram)) * 100}
                                sx={{ flexGrow: 1, ml: 1 }}
                              />
                              <Typography sx={{ ml: 1 }}>{count}</Typography>
                            </Box>
                          ))}
                        </Box>
                      )}
                    </Box>
                  )}
                </Paper>
              </Grid>
            </Grid>
          )}
          {activeTab === 3 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Metadata Analysis</Typography>
                  {analysisResults.appAnalysis && (
                    <Box>
                      <Typography><strong>App Size:</strong> {analysisResults.appAnalysis.data.size || 'N/A'}</Typography>
                      <Typography><strong>Last Updated:</strong> {new Date(analysisResults.appAnalysis.data.updated * 1000).toLocaleDateString()}</Typography>
                      <Typography><strong>Version:</strong> {analysisResults.appAnalysis.data.version || 'N/A'}</Typography>
                      <Typography><strong>Content Rating:</strong> {analysisResults.appAnalysis.data.contentRating}</Typography>
                    </Box>
                  )}
                </Paper>
              </Grid>
            </Grid>
          )}
          {activeTab === 4 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
                  {analysisResults.appAnalysis && (
                    <Box>
                      <Typography><strong>Install Range:</strong> {analysisResults.appAnalysis.data.installs}</Typography>
                      <Typography><strong>Rating:</strong> {analysisResults.appAnalysis.data.score || 'N/A'}</Typography>
                      <Typography><strong>Total Reviews:</strong> {analysisResults.appAnalysis.data.reviews || 'N/A'}</Typography>
                    </Box>
                  )}
                </Paper>
              </Grid>
            </Grid>
          )}
        </Box>
      </Box>
    );
  };

  const renderOverviewTab = () => {
    if (!analysisResults?.appAnalysis?.data) return null;

    const appData = analysisResults.appAnalysis.data;
    const competitors = analysisResults.competitorAnalysis?.comparison?.competitors || [];
    const metrics = analysisResults.competitorAnalysis?.comparison?.metrics_comparison || {};

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Your App Overview</Typography>
            <Box sx={{ mb: 2 }}>
              <Typography><strong>Name:</strong> {appData.title}</Typography>
              <Typography><strong>Installs:</strong> {appData.installs}</Typography>
              <Typography><strong>Rating:</strong> {appData.score || 'N/A'}</Typography>
              <Typography><strong>Reviews:</strong> {appData.reviews || 'N/A'}</Typography>
              <Typography><strong>Category:</strong> {appData.genre}</Typography>
              <Typography><strong>Last Updated:</strong> {new Date(appData.updated * 1000).toLocaleDateString()}</Typography>
            </Box>
          </Paper>
        </Grid>

        {competitors.length > 0 && (
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Market Position</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Typography><strong>Average Competitor Rating:</strong></Typography>
                  <Typography>{metrics.ratings?.avg_competitor_rating?.toFixed(2) || 'N/A'}</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={(metrics.ratings?.avg_competitor_rating || 0) * 20}
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography><strong>Average Competitor Installs:</strong></Typography>
                  <Typography>{(metrics.installs?.avg_competitor_installs || 0).toLocaleString()}</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={(appData.minInstalls / metrics.installs?.avg_competitor_installs || 0) * 100}
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography><strong>Market Position:</strong></Typography>
                  <Typography>
                    {metrics.market_position?.rating_percentile > 50 ? 'Leading' : 'Growing'}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        )}

        {competitors.length > 0 && (
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Competitor Analysis</Typography>
              {competitors.map((comp, index) => (
                <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #eee', borderRadius: 1 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    <strong>{comp.details.title}</strong>
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography><strong>Installs:</strong> {comp.details.installs}</Typography>
                      <Typography><strong>Rating:</strong> {comp.details.score?.toFixed(2) || 'N/A'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography><strong>Reviews:</strong> {comp.details.reviews?.toLocaleString() || 'N/A'}</Typography>
                      <Typography><strong>Category:</strong> {comp.details.genre}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography><strong>Rating Distribution:</strong></Typography>
                      {comp.details.histogram && (
                        <Box sx={{ mt: 1 }}>
                          {comp.details.histogram.map((count, idx) => (
                            <Box key={idx} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                              <Typography sx={{ minWidth: 70 }}>{5 - idx} stars:</Typography>
                              <LinearProgress 
                                variant="determinate" 
                                value={(count / Math.max(...comp.details.histogram)) * 100}
                                sx={{ flexGrow: 1, ml: 1 }}
                              />
                              <Typography sx={{ ml: 1 }}>{count.toLocaleString()}</Typography>
                            </Box>
                          ))}
                        </Box>
                      )}
                    </Grid>
                  </Grid>
                </Box>
              ))}
            </Paper>
          </Grid>
        )}

        {analysisResults.keywordAnalysis && (
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Keyword Analysis</Typography>
              <Box>
                <Typography variant="subtitle1" gutterBottom><strong>Common Keywords with Competitors:</strong></Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  {analysisResults.keywordAnalysis.analysis.keyword_comparison.common_keywords.map((keyword, index) => (
                    <Chip key={index} label={keyword} color="primary" variant="outlined" />
                  ))}
                </Box>

                <Typography variant="subtitle1" gutterBottom><strong>Your Unique Keywords:</strong></Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {analysisResults.keywordAnalysis.analysis.keyword_comparison.unique_keywords.map((keyword, index) => (
                    <Chip key={index} label={keyword} color="success" variant="outlined" />
                  ))}
                </Box>
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>
    );
  };

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