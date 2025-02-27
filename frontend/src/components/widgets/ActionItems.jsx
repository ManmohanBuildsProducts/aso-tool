import React, { useState, useEffect } from 'react';
import { HiExclamation, HiCheck, HiArrowRight } from 'react-icons/hi';

const ActionItems = ({ appId }) => {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchActionItems();
  }, [appId]);

  const fetchActionItems = async () => {
    try {
      setLoading(true);
      
      // Fetch various analyses
      const [metadataRes, keywordsRes, competitorsRes] = await Promise.all([
        fetch(`/api/ai/metadata/title/${appId}`),
        fetch(`/api/ai/keywords/${appId}`),
        fetch(`/api/ai/competitors/impact/${appId}`)
      ]);

      const [metadata, keywords, competitors] = await Promise.all([
        metadataRes.json(),
        keywordsRes.json(),
        competitorsRes.json()
      ]);

      // Combine and prioritize actions
      const allActions = [
        ...generateMetadataActions(metadata),
        ...generateKeywordActions(keywords),
        ...generateCompetitorActions(competitors)
      ];

      // Sort by priority and impact
      allActions.sort((a, b) => 
        (b.priority === a.priority) 
          ? b.impact - a.impact 
          : b.priority - a.priority
      );

      setActions(allActions);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching action items:', err);
      setLoading(false);
    }
  };

  const generateMetadataActions = (metadata) => {
    const actions = [];
    
    if (metadata.title_score < 70) {
      actions.push({
        type: 'metadata',
        priority: 3,
        impact: 85,
        title: 'Optimize App Title',
        description: metadata.title_recommendation || 'Your app title needs optimization for better visibility.',
        action: 'Update Title',
        link: '/metadata/title'
      });
    }

    if (metadata.description_score < 70) {
      actions.push({
        type: 'metadata',
        priority: 2,
        impact: 75,
        title: 'Improve Description',
        description: metadata.description_recommendation || 'Enhance your app description with more keywords and features.',
        action: 'Edit Description',
        link: '/metadata/description'
      });
    }

    return actions;
  };

  const generateKeywordActions = (keywords) => {
    const actions = [];
    
    if (keywords.opportunities?.length > 0) {
      actions.push({
        type: 'keywords',
        priority: 3,
        impact: 80,
        title: 'New Keyword Opportunities',
        description: `Found ${keywords.opportunities.length} high-potential keywords you're not targeting.`,
        action: 'View Keywords',
        link: '/keywords/opportunities'
      });
    }

    return actions;
  };

  const generateCompetitorActions = (competitors) => {
    const actions = [];
    
    if (competitors.gaps?.length > 0) {
      actions.push({
        type: 'competitors',
        priority: 2,
        impact: 70,
        title: 'Competitor Gaps',
        description: `Your competitors are ranking better for ${competitors.gaps.length} keywords.`,
        action: 'View Analysis',
        link: '/competitors/analysis'
      });
    }

    return actions;
  };

  if (loading) {
    return (
      <div className="animate-pulse bg-white rounded-lg shadow p-6">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        Priority Actions
      </h2>

      {actions.length === 0 ? (
        <div className="text-center py-8">
          <div className="bg-green-50 inline-block p-3 rounded-full mb-3">
            <HiCheck className="text-green-500 w-6 h-6" />
          </div>
          <p className="text-gray-600">
            Great job! No urgent actions needed.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {actions.map((action, index) => (
            <div 
              key={index}
              className={`p-4 rounded-lg border-l-4 ${
                action.priority === 3 
                  ? 'border-red-500 bg-red-50'
                  : action.priority === 2
                    ? 'border-yellow-500 bg-yellow-50'
                    : 'border-blue-500 bg-blue-50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-gray-800 flex items-center gap-2">
                    {action.priority === 3 && (
                      <HiExclamation className="text-red-500" />
                    )}
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {action.description}
                  </p>
                </div>
                <button
                  className="flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800"
                  onClick={() => {/* Handle navigation */}}
                >
                  {action.action}
                  <HiArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActionItems;