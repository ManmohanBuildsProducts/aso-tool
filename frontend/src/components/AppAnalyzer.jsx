import React, { useState } from 'react';
import { useQuery } from 'react-query';

const AppAnalyzer = () => {
  const [appData, setAppData] = useState({
    package_name: 'com.badhobuyer',
    competitor_package_names: ['club.kirana', 'com.udaan.android'],
    keywords: ['wholesale', 'b2b', 'business']
  });

  const { data, isLoading, error, refetch } = useQuery(
    ['analyze', appData],
    async () => {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(appData)
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    },
    {
      enabled: false
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    // Trigger the query
    refetch();
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name === 'competitor_package_names' || name === 'keywords') {
      setAppData({
        ...appData,
        [name]: value.split(',').map(item => item.trim())
      });
    } else {
      setAppData({
        ...appData,
        [name]: value
      });
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">App Store Optimization Analysis</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Package Name
          </label>
          <input
            type="text"
            name="package_name"
            value={appData.package_name}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Competitor Package Names (comma-separated)
          </label>
          <input
            type="text"
            name="competitor_package_names"
            value={appData.competitor_package_names.join(', ')}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Keywords (comma-separated)
          </label>
          <input
            type="text"
            name="keywords"
            value={appData.keywords.join(', ')}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
        
        <button
          type="submit"
          className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          disabled={isLoading}
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
          Error: {error.message}
        </div>
      )}

      {data && (
        <div className="mt-8 space-y-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900">App Metadata</h3>
            <div className="mt-2 p-4 bg-gray-100 rounded-md">
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Title</dt>
                  <dd className="mt-1 text-sm text-gray-900">{data.app_metadata?.title || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Category</dt>
                  <dd className="mt-1 text-sm text-gray-900">{data.app_metadata?.category || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Rating</dt>
                  <dd className="mt-1 text-sm text-gray-900">{data.app_metadata?.rating || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Installs</dt>
                  <dd className="mt-1 text-sm text-gray-900">{data.app_metadata?.installs || 'N/A'}</dd>
                </div>
              </dl>
              <div className="mt-4">
                <dt className="text-sm font-medium text-gray-500">Description</dt>
                <dd className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                  {data.app_metadata?.description || 'N/A'}
                </dd>
              </div>
            </div>
          </div>

          {data.analysis?.analysis && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Analysis</h3>
              <div className="mt-2 p-4 bg-gray-100 rounded-md">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Title Analysis</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.analysis.analysis.title_analysis || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Description Analysis</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.analysis.analysis.description_analysis || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Keyword Opportunities</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.analysis.analysis.keyword_opportunities || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Recommendations</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.analysis.analysis.recommendations || 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          )}

          {data.competitor_analysis?.analysis && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Competitor Analysis</h3>
              <div className="mt-2 p-4 bg-gray-100 rounded-md">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Competitive Analysis</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.competitor_analysis.analysis.competitive_analysis || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Keyword Comparison</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.competitor_analysis.analysis.keyword_comparison || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Description Comparison</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.competitor_analysis.analysis.description_comparison || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Market Position</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.competitor_analysis.analysis.market_position || 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          )}

          {data.keyword_suggestions?.suggestions && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Keyword Suggestions</h3>
              <div className="mt-2 p-4 bg-gray-100 rounded-md">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Related Keywords</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {Array.isArray(data.keyword_suggestions.suggestions.related_keywords)
                        ? data.keyword_suggestions.suggestions.related_keywords.join(', ')
                        : data.keyword_suggestions.suggestions.related_keywords || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Long-tail Keywords</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {Array.isArray(data.keyword_suggestions.suggestions.long_tail_keywords)
                        ? data.keyword_suggestions.suggestions.long_tail_keywords.join(', ')
                        : data.keyword_suggestions.suggestions.long_tail_keywords || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Volume Estimates</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.keyword_suggestions.suggestions.volume_estimates || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Competition Levels</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.keyword_suggestions.suggestions.competition_levels || 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          )}

          {data.market_trends?.trends && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Market Trends</h3>
              <div className="mt-2 p-4 bg-gray-100 rounded-md">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Market Trends</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.market_trends.trends.market_trends || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">User Expectations</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.market_trends.trends.user_expectations || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Growth Opportunities</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.market_trends.trends.growth_opportunities || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Challenges</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.market_trends.trends.challenges || 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          )}

          {data.description_optimization?.optimization && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Description Optimization</h3>
              <div className="mt-2 p-4 bg-gray-100 rounded-md">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Optimized Description</dt>
                    <dd className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                      {data.description_optimization.optimization.optimized_description || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Keyword Analysis</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.description_optimization.optimization.keyword_analysis || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Readability Score</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.description_optimization.optimization.readability_score || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Suggestions</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.description_optimization.optimization.suggestions || 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AppAnalyzer;