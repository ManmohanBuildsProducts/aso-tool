import React from 'react';
import { useQuery } from 'react-query';
import { fetchAppAnalysis } from '../services/api';
import HealthScore from './widgets/HealthScore';
import ActionCenter from './widgets/ActionCenter';
import MarketPosition from './widgets/MarketPosition';
import KeywordAnalysis from './widgets/KeywordAnalysis';
import LoadingState from './LoadingState';
import ErrorBoundary from './ErrorBoundary';

const Dashboard = ({ appId }) => {
  // Transform API response
  const transformResponse = React.useCallback((data) => {
    const sections = {};
    if (data?.analysis) {
      Object.entries(data.analysis).forEach(([key, value]) => {
        const sectionName = key.replace(/^\d+\.\s+/, '').toLowerCase();
        sections[sectionName] = value.split('---')[0].trim();
      });
    }
    return {
      sections,
      format: data?.format
    };
  }, []);

  // Transform sections into actions
  const transformActions = React.useCallback((sections) => {
    if (!sections) return [];
    
    return Object.entries(sections)
      .filter(([key]) => key.includes('recommendations') || key.includes('actions'))
      .flatMap(([_, value]) => {
        return value.split('\n')
          .filter(line => line.trim().startsWith('-') || line.trim().startsWith('•'))
          .map(line => ({
            id: Math.random().toString(36).substr(2, 9),
            title: line.replace(/^[-•]\s*/, '').trim(),
            priority: line.toLowerCase().includes('urgent') || line.toLowerCase().includes('critical') 
              ? 'high' 
              : line.toLowerCase().includes('consider') 
                ? 'low' 
                : 'medium',
            effort: line.toLowerCase().includes('simple') || line.toLowerCase().includes('quick')
              ? 'low'
              : line.toLowerCase().includes('complex') || line.toLowerCase().includes('major')
                ? 'high'
                : 'medium'
          }));
      });
  }, []);

  // Transform sections into keywords
  const transformKeywords = React.useCallback((sections) => {
    const keywordSection = sections?.['keyword opportunities'] || '';
    return keywordSection.split('\n')
      .filter(line => line.trim().startsWith('-') || line.trim().startsWith('•'))
      .map(line => ({
        keyword: line.replace(/^[-•]\s*/, '').trim(),
        relevance: Math.random() * 100  // TODO: Implement proper relevance calculation
      }));
  }, []);

  const { data, isLoading, error } = useQuery(
    ['appAnalysis', appId],
    () => fetchAppAnalysis(appId),
    {
      select: transformResponse,
      retry: 2,
      staleTime: 5 * 60 * 1000  // 5 minutes
    }
  );

  const actions = React.useMemo(() => transformActions(data?.sections), [data?.sections, transformActions]);
  const keywords = React.useMemo(() => transformKeywords(data?.sections), [data?.sections, transformKeywords]);

  if (isLoading) return <LoadingState message="Analyzing app data..." />;
  if (error) {
    return (
      <ErrorBoundary showReset>
        <div>Error loading dashboard data</div>
      </ErrorBoundary>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ErrorBoundary>
            <HealthScore data={data} />
          </ErrorBoundary>
        </div>
        <div>
          <ErrorBoundary>
            <MarketPosition data={data?.sections?.['competitive advantages']} />
          </ErrorBoundary>
        </div>
      </div>

      {/* Middle Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ErrorBoundary>
          <ActionCenter actions={actions} appId={appId} />
        </ErrorBoundary>
        <ErrorBoundary>
          <KeywordAnalysis 
            keywords={keywords} 
            appId={appId}
            insights={data?.sections?.['keyword opportunities']}
          />
        </ErrorBoundary>
      </div>
    </div>
  );
};

export default Dashboard;