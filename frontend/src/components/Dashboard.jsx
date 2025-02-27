import React from 'react';
import HealthScore from './widgets/HealthScore';
import ActionCenter from './widgets/ActionCenter';
import MarketPosition from './widgets/MarketPosition';
import KeywordAnalysis from './widgets/KeywordAnalysis';
import { useQuery } from 'react-query';
import { fetchAppAnalysis } from '../services/api';
import LoadingState from './common/LoadingState';
import ErrorState from './common/ErrorState';

const Dashboard = ({ appId }) => {
  const { data, isLoading, error } = useQuery(
    ['appAnalysis', appId],
    () => fetchAppAnalysis(appId),
    {
      select: (data) => {
        // Transform markdown sections into structured data
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
      }
    }
  );

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;

  return (
    <div className="space-y-6">
      {/* Top Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <HealthScore score={data?.health_score} metrics={data?.metrics} />
        </div>
        <div>
          <MarketPosition position={data?.market_position} />
        </div>
      </div>

      {/* Middle Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActionCenter actions={data?.actions} appId={appId} />
        <KeywordAnalysis keywords={data?.keywords} appId={appId} />
      </div>
    </div>
  );
}

export default Dashboard;