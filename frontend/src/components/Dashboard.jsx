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

  // Transform sections into actions
  const actions = React.useMemo(() => {
    if (!data?.sections) return [];
    
    return Object.entries(data.sections)
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
  }, [data?.sections]);

  // Transform sections into keywords
  const keywords = React.useMemo(() => {
    if (!data?.sections?.['keyword opportunities']) return [];
    
    const keywordSection = data.sections['keyword opportunities'];
    return keywordSection.split('\n')
      .filter(line => line.trim().startsWith('-') || line.trim().startsWith('•'))
      .map(line => ({
        keyword: line.replace(/^[-•]\s*/, '').trim(),
        relevance: Math.random() * 100  // TODO: Implement proper relevance calculation
      }));
  }, [data?.sections]);

  return (
    <div className="space-y-6">
      {/* Top Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <HealthScore data={data} />
        </div>
        <div>
          <MarketPosition data={data?.sections?.['competitive advantages']} />
        </div>
      </div>

      {/* Middle Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActionCenter actions={actions} appId={appId} />
        <KeywordAnalysis 
          keywords={keywords} 
          appId={appId}
          insights={data?.sections?.['keyword opportunities']}
        />
      </div>
    </div>
  );
}

export default Dashboard;