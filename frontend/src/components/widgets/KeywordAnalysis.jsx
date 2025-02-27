import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { fetchKeywordAnalysis } from '../../services/api';
import { HiSearch, HiTrendingUp, HiTrendingDown } from 'react-icons/hi';

const KeywordAnalysis = ({ keywords, appId }) => {
  const [selectedKeyword, setSelectedKeyword] = useState(keywords?.[0]?.keyword);

  const { data: analysis, isLoading } = useQuery(
    ['keywordAnalysis', selectedKeyword],
    () => fetchKeywordAnalysis(selectedKeyword),
    {
      enabled: !!selectedKeyword
    }
  );

  const getTrendIcon = (trend) => {
    if (trend === 'up') {
      return <HiTrendingUp className="w-5 h-5 text-green-500" />;
    }
    return <HiTrendingDown className="w-5 h-5 text-red-500" />;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">
          Keyword Analysis
        </h2>
        <div className="relative">
          <select
            value={selectedKeyword}
            onChange={(e) => setSelectedKeyword(e.target.value)}
            className="pl-8 pr-4 py-1.5 border border-gray-300 rounded-lg text-sm appearance-none"
          >
            {keywords?.map((kw) => (
              <option key={kw.keyword} value={kw.keyword}>
                {kw.keyword}
              </option>
            ))}
          </select>
          <HiSearch className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        </div>
      </div>

      {isLoading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-40 bg-gray-200 rounded"></div>
        </div>
      ) : (
        <>
          {/* Metrics */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="text-sm text-blue-600">Volume</div>
              <div className="text-2xl font-bold text-blue-700">
                {analysis?.metrics?.volume || 0}
              </div>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <div className="text-sm text-green-600">Difficulty</div>
              <div className="text-2xl font-bold text-green-700">
                {analysis?.metrics?.difficulty || 0}
              </div>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <div className="text-sm text-purple-600">Relevance</div>
              <div className="text-2xl font-bold text-purple-700">
                {analysis?.metrics?.relevance || 0}
              </div>
            </div>
          </div>

          {/* Related Keywords */}
          <div className="mb-6">
            <h3 className="font-medium text-gray-900 mb-3">
              Related Keywords
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {analysis?.related_keywords?.map((kw, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded"
                >
                  <span className="text-sm text-gray-600">
                    {kw.keyword}
                  </span>
                  {getTrendIcon(kw.trend)}
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="font-medium text-green-900 mb-2">
              Optimization Suggestions
            </h3>
            <ul className="space-y-2 text-sm text-green-700">
              {analysis?.recommendations?.map((rec, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span>•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default KeywordAnalysis;