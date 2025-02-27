import React, { useState, useCallback } from 'react';
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
  Alert,
  Snackbar,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
  ClearAll as ClearAllIcon,
} from '@mui/icons-material';

import ErrorBoundary from './ErrorBoundary';
import LoadingState from './states/LoadingState';
import EmptyState from './states/EmptyState';
import ProgressTracker from './ProgressTracker';
import { useAnalysisWithCache } from '../hooks/useAnalysisWithCache';
import { clearCache } from '../hooks/useCache';
import {
  formatNumber,
  formatDate,
  formatRating,
  formatPercentage,
  safeGet,
  validateAppData,
  formatInstallRange,
  getMarketPosition,
} from '../utils/dataFormatters';

const AppAnalyzer = () => {
  // State management
  const [mainApp, setMainApp] = useState({
    url: '',
    appId: '',
  });
  
  const [competitors, setCompetitors] = useState([]);
  const [newCompetitorUrl, setNewCompetitorUrl] = useState('');
  const [editingIndex, setEditingIndex] = useState(-1);
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [analysisResults, setAnalysisResults] = useState(null);
  
  const {
    analyzeApp,
    loading,
    error,
    progress,
  } = useAnalysisWithCache();

  // Handle cache clearing
  const handleClearCache = useCallback(() => {
    clearCache();
    setSnackbar({
      open: true,
      message: 'Cache cleared successfully',
      severity: 'success',
    });
  }, []);

  // Extract app ID from Play Store URL
  const extractAppId = useCallback((url) => {
    const match = url.match(/id=([^&]+)/);
    return match ? match[1] : '';
  }, []);

  // Handle main app URL change
  const handleMainAppUrlChange = useCallback((event) => {
    const url = event.target.value;
    const appId = extractAppId(url);
    setMainApp({ url, appId });
    
    if (!appId && url) {
      setSnackbar({
        open: true,
        message: 'Invalid Play Store URL. Please check the format.',
        severity: 'warning',
      });
    }
  }, [extractAppId]);

  // Handle competitor management
  const handleAddCompetitor = useCallback(() => {
    if (!newCompetitorUrl) {
      setSnackbar({
        open: true,
        message: 'Please enter a competitor URL',
        severity: 'warning',
      });
      return;
    }

    const appId = extractAppId(newCompetitorUrl);
    if (!appId) {
      setSnackbar({
        open: true,
        message: 'Invalid Play Store URL. Please check the format.',
        severity: 'warning',
      });
      return;
    }

    if (competitors.some(comp => comp.appId === appId)) {
      setSnackbar({
        open: true,
        message: 'This competitor is already added',
        severity: 'warning',
      });
      return;
    }

    setCompetitors(prev => [...prev, { url: newCompetitorUrl, appId }]);
    setNewCompetitorUrl('');
  }, [newCompetitorUrl, competitors, extractAppId]);

  // Handle analysis
  const handleAnalyze = useCallback(async (forceFresh = false) => {
    if (!mainApp.appId) {
      setSnackbar({
        open: true,
        message: 'Please enter a valid app URL',
        severity: 'error',
      });
      return;
    }

    try {
      const results = await analyzeApp(mainApp, competitors, { forceFresh });
      setAnalysisResults(results);
      setSnackbar({
        open: true,
        message: 'Analysis completed successfully',
        severity: 'success',
      });
      setActiveTab(0);
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Analysis failed: ${error.message}`,
        severity: 'error',
      });
    }
  }, [mainApp, competitors, analyzeApp]);

  // Render functions
  const renderHeader = () => (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        ASO Analysis Tool
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Analyze your app's performance and compare it with competitors
      </Typography>
      <Divider />
    </Box>
  );

  const renderMainAppInput = () => (
    <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Main App
      </Typography>
      <TextField
        fullWidth
        label="Play Store URL"
        variant="outlined"
        value={mainApp.url}
        onChange={handleMainAppUrlChange}
        error={mainApp.url && !mainApp.appId}
        helperText={mainApp.url && !mainApp.appId ? 'Invalid Play Store URL' : ''}
        disabled={loading}
        sx={{ mb: 2 }}
      />
    </Paper>
  );

  const renderCompetitorSection = () => (
    <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Competitors
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          fullWidth
          label="Competitor Play Store URL"
          variant="outlined"
          value={newCompetitorUrl}
          onChange={(e) => setNewCompetitorUrl(e.target.value)}
          error={newCompetitorUrl && !extractAppId(newCompetitorUrl)}
          helperText={
            newCompetitorUrl && !extractAppId(newCompetitorUrl)
              ? 'Invalid Play Store URL'
              : ''
          }
          disabled={loading}
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddCompetitor}
          disabled={!extractAppId(newCompetitorUrl) || loading}
        >
          Add
        </Button>
      </Box>

      {competitors.length > 0 ? (
        <List>
          {competitors.map((competitor, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={competitor.url}
                secondary={competitor.appId}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => {
                    setCompetitors(prev => prev.filter((_, i) => i !== index));
                  }}
                  disabled={loading}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      ) : (
        <EmptyState
          type="compact"
          title="No Competitors Added"
          message="Add competitor apps to compare and analyze"
          icon="search"
        />
      )}
    </Paper>
  );

  const renderAnalysisControls = () => (
    <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 4 }}>
      <Button
        variant="contained"
        color="primary"
        size="large"
        onClick={() => handleAnalyze(false)}
        disabled={!mainApp.appId || loading}
        startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </Button>

      <Button
        variant="outlined"
        color="primary"
        size="large"
        onClick={() => handleAnalyze(true)}
        disabled={!mainApp.appId || loading}
        startIcon={<RefreshIcon />}
      >
        Force Fresh Analysis
      </Button>

      <Button
        variant="outlined"
        color="secondary"
        size="large"
        onClick={handleClearCache}
        disabled={loading}
        startIcon={<ClearAllIcon />}
      >
        Clear Cache
      </Button>
    </Box>
  );

  const renderAnalysisResults = () => {
    if (loading) {
      return (
        <>
          <ProgressTracker
            current={progress.current}
            total={progress.total}
            error={error}
          />
          <LoadingState
            variant="skeleton"
            message="Analyzing app and competitors..."
          >
            <LoadingSkeleton type={
              activeTab === 1 ? 'keywords' :
              activeTab === 2 ? 'reviews' :
              'overview'
            } />
          </LoadingState>
        </>
      );
    }

    if (error) {
      return (
        <EmptyState
          type="error"
          title="Analysis Failed"
          message={error}
          actionText="Retry Analysis"
          onAction={() => handleAnalyze(true)}
          icon="error"
        />
      );
    }

    if (!analysisResults) {
      return (
        <EmptyState
          type="default"
          title="No Analysis Results"
          message="Start by analyzing your app and its competitors"
          icon="search"
        />
      );
    }

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

        <ErrorBoundary onRetry={() => handleAnalyze(true)}>
          <Box mt={2}>
            {activeTab === 0 && renderOverviewTab()}
            {activeTab === 1 && renderKeywordsTab()}
            {activeTab === 2 && renderReviewsTab()}
            {activeTab === 3 && renderMetadataTab()}
            {activeTab === 4 && renderPerformanceTab()}
          </Box>
        </ErrorBoundary>
      </Box>
    );
  };

  // ... [Previous tab rendering functions remain the same]

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        {renderHeader()}
        {renderMainAppInput()}
        {renderCompetitorSection()}
        {renderAnalysisControls()}
        {renderAnalysisResults()}
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AppAnalyzer;