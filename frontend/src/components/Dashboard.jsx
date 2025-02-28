import React from 'react';
import { useQuery } from 'react-query';
import { fetchAppAnalysis, fetchKeywordAnalysis, fetchCompetitorImpact } from '../services/api';
import ASOScoreCard from './dashboard/ASOScoreCard';
import KeywordTable from './dashboard/KeywordTable';
import CompetitorAnalysis from './dashboard/CompetitorAnalysis';
import LoadingState from './common/LoadingState';
import ErrorState from './common/ErrorState';

const Dashboard = ({ appId }) => {
  // Fetch app analysis
  const { 
    data: appData,
    isLoading: isLoadingApp,
    error: appError
  } = useQuery(
    ['appAnalysis', appId],
    () => fetchAppAnalysis(appId),
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
    () => fetchKeywordAnalysis('b2b wholesale'),  // TODO: Make dynamic
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
    () => fetchCompetitorImpact(appId, []),
    {
      staleTime: 5 * 60 * 1000
    }
  );

  // Show loading state
  if (isLoadingApp || isLoadingKeywords || isLoadingCompetitors) {
    return (
      <div className="space-y-6">
        <LoadingState message="Analyzing app data..." />
        <LoadingState message="Analyzing keywords..." />
        <LoadingState message="Analyzing competitors..." />
      </div>
    );
  }

  // Show error state with details
  if (appError || keywordError || competitorError) {
    const error = appError || keywordError || competitorError;
    const errorMessage = error?.response?.data?.detail || error?.message || 'An error occurred';
    
    return (
      <ErrorState 
        error={{ message: errorMessage }}
        showReset
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ASOScoreCard data={appData} />
        </div>
        <div>
          <CompetitorAnalysis data={competitorData} />
        </div>
      </div>

      {/* Bottom Row */}
      <div>
        <KeywordTable data={keywordData} />
      </div>
    </div>
  );
};

export default Dashboard;