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
            <pre className="mt-2 p-4 bg-gray-100 rounded-md overflow-auto">
              {JSON.stringify(data.app_metadata, null, 2)}
            </pre>
          </div>

          <div>
            <h3 className="text-lg font-medium text-gray-900">Analysis</h3>
            <pre className="mt-2 p-4 bg-gray-100 rounded-md overflow-auto">
              {JSON.stringify(data.analysis, null, 2)}
            </pre>
          </div>

          {data.competitor_analysis && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Competitor Analysis</h3>
              <pre className="mt-2 p-4 bg-gray-100 rounded-md overflow-auto">
                {JSON.stringify(data.competitor_analysis, null, 2)}
              </pre>
            </div>
          )}

          {data.keyword_suggestions && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Keyword Suggestions</h3>
              <pre className="mt-2 p-4 bg-gray-100 rounded-md overflow-auto">
                {JSON.stringify(data.keyword_suggestions, null, 2)}
              </pre>
            </div>
          )}

          {data.market_trends && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Market Trends</h3>
              <pre className="mt-2 p-4 bg-gray-100 rounded-md overflow-auto">
                {JSON.stringify(data.market_trends, null, 2)}
              </pre>
            </div>
          )}

          {data.description_optimization && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Description Optimization</h3>
              <pre className="mt-2 p-4 bg-gray-100 rounded-md overflow-auto">
                {JSON.stringify(data.description_optimization, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AppAnalyzer;