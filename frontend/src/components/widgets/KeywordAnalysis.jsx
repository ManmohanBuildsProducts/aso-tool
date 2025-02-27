import React, { useState, useEffect } from 'react';
import { HiTrendingUp, HiTrendingDown } from 'react-icons/hi';

const KeywordAnalysis = ({ appId, keywords }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedKeyword, setSelectedKeyword] = useState(keywords[0]);

  useEffect(() => {
    fetchAnalysis();
  }, [appId, selectedKeyword]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/ai/keywords/${selectedKeyword}`
      );
      const data = await response.json();
      setAnalysis(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="animate-pulse bg-gray-100 rounded-lg p-4">
      <div className="h-48 bg-gray-200 rounded"></div>
    </div>
  );

  if (error) return (
    <div className="bg-red-50 text-red-600 p-4 rounded-lg">
      Error loading keyword analysis: {error}
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800">
          Keyword Analysis
        </h2>
        <select
          value={selectedKeyword}
          onChange={(e) => setSelectedKeyword(e.target.value)}
          className="px-3 py-1 border rounded text-gray-600"
        >
          {keywords.map(kw => (
            <option key={kw} value={kw}>{kw}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-sm text-blue-600">Search Volume</div>
          <div className="text-2xl font-bold text-blue-700">
            {analysis?.search_volume_score || '-'}
          </div>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="text-sm text-green-600">Difficulty</div>
          <div className="text-2xl font-bold text-green-700">
            {analysis?.difficulty_score || '-'}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="font-semibold text-gray-700">Related Keywords</h3>
        <div className="grid grid-cols-2 gap-2">
          {analysis?.suggestions?.slice(0, 6).map((suggestion, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-2 bg-gray-50 rounded"
            >
              <span className="text-sm text-gray-600">
                {suggestion.keyword}
              </span>
              {suggestion.trend === 'up' ? (
                <HiTrendingUp className="text-green-500" />
              ) : (
                <HiTrendingDown className="text-red-500" />
              )}
            </div>
          ))}
        </div>
      </div>

      {analysis?.recommendations && (
        <div className="mt-4 p-4 bg-purple-50 rounded-lg">
          <h3 className="font-semibold text-purple-800 mb-2">
            AI Recommendations
          </h3>
          <ul className="space-y-2 text-sm text-purple-700">
            {analysis.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-purple-400">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default KeywordAnalysis;