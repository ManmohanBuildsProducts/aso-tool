import React from 'react';
import { useQuery } from 'react-query';
import { 
  fetchAppAnalysis, 
  fetchKeywordAnalysis, 
  fetchCompetitorAnalysis,
  fetchMarketTrends 
} from '../services/api';
import ASOScoreCard from './dashboard/ASOScoreCard';
import KeywordTable from './dashboard/KeywordTable';
import CompetitorAnalysis from './dashboard/CompetitorAnalysis';
import MarketTrends from './dashboard/MarketTrends';
import LoadingState from './common/LoadingState';
import ErrorState from './common/ErrorState';

const Dashboard = ({ appId }) => {
  const appMetadata = {
    title: "BadhoBuyer - B2B Wholesale Trading App",
    description: "BadhoBuyer is a B2B wholesale trading platform connecting businesses with suppliers.",
    category: "Business",
    keywords: ["wholesale", "b2b", "business", "trading", "supplier"]
  };

  const competitors = [
    {
      title: "Kirana Club - B2B Wholesale App",
      description: "Kirana Club is a B2B wholesale app for retailers and suppliers.",
      category: "Business",
      keywords: ["wholesale", "b2b", "kirana", "retail", "supplier"]
    },
    {
      title: "Udaan - B2B Trading Platform",
      description: "Udaan is India's largest B2B trading platform for businesses.",
      category: "Business",
      keywords: ["wholesale", "b2b", "trading", "marketplace", "business"]
    }
  ];

  // Fetch app analysis
  const { 
    data: appData,
    isLoading: isLoadingApp,
    error: appError
  } = useQuery(
    ['appAnalysis', appId],
    () => fetchAppAnalysis(appId, appMetadata),
    {
      staleTime: 5 * 60 * 1000  // 5 minutes
    }
  );

  // Fetch keyword analysis
  const {
    data: keywordData,
    isLoading: isLoadingKeywords,
    error: keywordError
  } = useQuery(
    ['keywordAnalysis', appId],
    () => fetchKeywordAnalysis('wholesale b2b', 'B2B wholesale'),
    {
      staleTime: 5 * 60 * 1000
    }
  );

  // Fetch competitor analysis
  const {
    data: competitorData,
    isLoading: isLoadingCompetitors,
    error: competitorError
  } = useQuery(
    ['competitorAnalysis', appId],
    () => fetchCompetitorAnalysis({
      app_metadata: appMetadata,
      competitor_metadata: competitors
    }),
    {
      staleTime: 5 * 60 * 1000
    }
  );

  // Fetch market trends
  const {
    data: trendsData,
    isLoading: isLoadingTrends,
    error: trendsError
  } = useQuery(
    ['marketTrends'],
    () => fetchMarketTrends({ category: 'B2B wholesale' }),
    {
      staleTime: 15 * 60 * 1000  // 15 minutes
    }
  );

  // Show loading state
  if (isLoadingApp || isLoadingKeywords || isLoadingCompetitors || isLoadingTrends) {
    return (
      <div className="space-y-6" data-testid="dashboard-loading">
        <LoadingState 
          message="Analyzing app data..." 
          testId="aso-score-loading"
        />
        <LoadingState 
          message="Analyzing keywords..." 
          testId="keyword-loading"
        />
        <LoadingState 
          message="Analyzing competitors..." 
          testId="competitor-loading"
        />
        <LoadingState 
          message="Analyzing market trends..." 
          testId="trends-loading"
        />
      </div>
    );
  }

  // Show error state with details
  if (appError || keywordError || competitorError || trendsError) {
    const error = appError || keywordError || competitorError || trendsError;
    const errorMessage = error?.response?.data?.detail || error?.message || 'An error occurred';
    
    return (
      <ErrorState 
        error={{ message: errorMessage }}
        showReset
      />
    );
  }

  return (
    <div className="space-y-8" data-testid="dashboard-container">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">ASO Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>

      {/* Top Row - ASO Score and Market Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6" data-testid="aso-score-section">
          <h2 className="text-xl font-semibold mb-4">ASO Score</h2>
          <ASOScoreCard data={appData?.analysis} />
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6" data-testid="trends-section">
          <h2 className="text-xl font-semibold mb-4">Market Trends</h2>
          <MarketTrends data={trendsData?.analysis} />
        </div>
      </div>

      {/* Middle Row - Competitor Analysis */}
      <div className="bg-white rounded-lg shadow-lg p-6" data-testid="competitor-section">
        <h2 className="text-xl font-semibold mb-4">Competitor Analysis</h2>
        <CompetitorAnalysis data={competitorData?.analysis} />
      </div>

      {/* Bottom Row - Keyword Analysis */}
      <div className="bg-white rounded-lg shadow-lg p-6" data-testid="keyword-section">
        <h2 className="text-xl font-semibold mb-4">Keyword Analysis</h2>
        <KeywordTable data={keywordData?.analysis} />
      </div>
    </div>
  );
};

export default Dashboard;