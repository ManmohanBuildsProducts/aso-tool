import React, { useState, useEffect } from 'react';
import { HiStar, HiTrendingUp, HiLightningBolt } from 'react-icons/hi';

const KeywordOpportunities = ({ appId }) => {
  const [opportunities, setOpportunities] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchOpportunities();
  }, [appId]);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/ai/keywords/${appId}`);
      const data = await response.json();
      setOpportunities(data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching opportunities:', err);
      setLoading(false);
    }
  };

  const getOpportunityScore = (difficulty, volume) => {
    // Higher volume and lower difficulty = better opportunity
    return Math.round(((100 - difficulty) * 0.4 + volume * 0.6));
  };

  if (loading) {
    return (
      <div className="animate-pulse bg-white rounded-lg shadow p-6">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">
          Keyword Opportunities
        </h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-1 border rounded text-gray-600"
        >
          <option value="all">All Keywords</option>
          <option value="high">High Impact</option>
          <option value="trending">Trending</option>
          <option value="quick">Quick Wins</option>
        </select>
      </div>

      <div className="space-y-4">
        {opportunities?.keywords
          ?.filter(kw => {
            if (filter === 'high') return kw.impact_score > 80;
            if (filter === 'trending') return kw.trend === 'up';
            if (filter === 'quick') return kw.difficulty_score < 40;
            return true;
          })
          ?.map((keyword, index) => (
            <div 
              key={index}
              className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-800">
                      {keyword.keyword}
                    </span>
                    {keyword.impact_score > 80 && (
                      <HiStar className="text-yellow-400 w-5 h-5" />
                    )}
                    {keyword.trend === 'up' && (
                      <HiTrendingUp className="text-green-500 w-5 h-5" />
                    )}
                    {keyword.difficulty_score < 40 && (
                      <HiLightningBolt className="text-blue-500 w-5 h-5" />
                    )}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Volume: {keyword.search_volume_score} • 
                    Difficulty: {keyword.difficulty_score}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-600">
                    {getOpportunityScore(
                      keyword.difficulty_score,
                      keyword.search_volume_score
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    Opportunity Score
                  </div>
                </div>
              </div>

              {keyword.recommendation && (
                <div className="mt-3 text-sm text-blue-600">
                  Tip: {keyword.recommendation}
                </div>
              )}
            </div>
          ))}
      </div>

      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-medium text-blue-700 mb-2">Legend</h3>
        <div className="grid grid-cols-3 gap-2 text-sm">
          <div className="flex items-center gap-1">
            <HiStar className="text-yellow-400" />
            <span>High Impact</span>
          </div>
          <div className="flex items-center gap-1">
            <HiTrendingUp className="text-green-500" />
            <span>Trending</span>
          </div>
          <div className="flex items-center gap-1">
            <HiLightningBolt className="text-blue-500" />
            <span>Quick Win</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KeywordOpportunities;