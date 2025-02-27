import React, { useState, useEffect } from 'react';
import { HiArrowSmUp, HiArrowSmDown, HiMinus } from 'react-icons/hi';

const CompetitorComparison = ({ appId }) => {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState('rankings');

  useEffect(() => {
    fetchComparison();
  }, [appId]);

  const fetchComparison = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/ai/competitors/impact/${appId}`);
      const data = await response.json();
      setComparison(data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching comparison:', err);
      setLoading(false);
    }
  };

  const getChangeIndicator = (change) => {
    if (change > 0) {
      return <HiArrowSmUp className="text-green-500 w-5 h-5" />;
    } else if (change < 0) {
      return <HiArrowSmDown className="text-red-500 w-5 h-5" />;
    }
    return <HiMinus className="text-gray-400 w-5 h-5" />;
  };

  if (loading) {
    return (
      <div className="animate-pulse bg-white rounded-lg shadow p-6">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-32 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">
          Competitor Analysis
        </h2>
        <select
          value={selectedMetric}
          onChange={(e) => setSelectedMetric(e.target.value)}
          className="px-3 py-1 border rounded text-gray-600"
        >
          <option value="rankings">Rankings</option>
          <option value="keywords">Keywords</option>
          <option value="visibility">Visibility</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Your App */}
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-center">
            <div className="text-sm text-blue-600 font-medium">Your App</div>
            <div className="text-2xl font-bold text-blue-700 mt-2">
              {comparison?.your_app?.metrics[selectedMetric] || '-'}
            </div>
            <div className="flex items-center justify-center mt-2">
              {getChangeIndicator(comparison?.your_app?.changes[selectedMetric])}
              <span className="text-sm text-gray-600 ml-1">
                vs last week
              </span>
            </div>
          </div>
        </div>

        {/* Main Competitors */}
        {comparison?.competitors?.slice(0, 2).map((competitor, index) => (
          <div 
            key={index}
            className="bg-gray-50 rounded-lg p-4"
          >
            <div className="text-center">
              <div className="text-sm text-gray-600 font-medium">
                {competitor.name}
              </div>
              <div className="text-2xl font-bold text-gray-700 mt-2">
                {competitor.metrics[selectedMetric] || '-'}
              </div>
              <div className="flex items-center justify-center mt-2">
                {getChangeIndicator(competitor.changes[selectedMetric])}
                <span className="text-sm text-gray-600 ml-1">
                  vs last week
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Insights */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium text-gray-700 mb-2">Key Insights</h3>
        <ul className="text-sm text-gray-600 space-y-2">
          {comparison?.insights?.map((insight, index) => (
            <li key={index} className="flex items-start gap-2">
              <span className="text-blue-400">•</span>
              {insight}
            </li>
          ))}
        </ul>
      </div>

      {/* Opportunities */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-green-50 rounded-lg">
          <h3 className="font-medium text-green-700 mb-2">
            Your Advantages
          </h3>
          <ul className="text-sm text-green-600 space-y-2">
            {comparison?.advantages?.map((advantage, index) => (
              <li key={index} className="flex items-start gap-2">
                <span>•</span>
                {advantage}
              </li>
            ))}
          </ul>
        </div>

        <div className="p-4 bg-yellow-50 rounded-lg">
          <h3 className="font-medium text-yellow-700 mb-2">
            Areas to Improve
          </h3>
          <ul className="text-sm text-yellow-600 space-y-2">
            {comparison?.improvements?.map((improvement, index) => (
              <li key={index} className="flex items-start gap-2">
                <span>•</span>
                {improvement}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CompetitorComparison;