import React, { useState } from 'react';
import { useQuery } from 'react-query';

const AppAnalyzer = () => {
  const [appData, setAppData] = useState({
    package_name: 'com.badhobuyer',
    competitor_package_names: ['club.kirana', 'com.udaan.android'],
    keywords: ['wholesale', 'b2b', 'business']
  });

  const [taskId, setTaskId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const { data: jobData, isLoading: isJobLoading, error: jobError, refetch: createJob } = useQuery(
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
      const result = await response.json();
      if (result.error) {
        throw new Error(result.error);
      }
      setTaskId(result.task_id); // Changed from job_id to task_id
      setIsAnalyzing(true);
      return result;
    },
    {
      enabled: false,
      retry: 3,
      retryDelay: 1000,
      onError: (error) => {
        console.error('Error creating job:', error);
        setIsAnalyzing(false);
      }
    }
  );

  const { data, isLoading, error } = useQuery(
    ['result', taskId],
    async () => {
      if (!taskId) return null;
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analyze/${taskId}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const result = await response.json();
      if (result.error) {
        throw new Error(result.error);
      }
      
      // Update status and progress
      if (result.status === 'completed') {
        setIsAnalyzing(false);
        setProgress(100);
      } else if (result.status === 'error') {
        setIsAnalyzing(false);
        throw new Error(result.error || 'Analysis failed');
      } else {
        // Calculate progress based on available data
        let currentProgress = 0;
        if (result.app_data) currentProgress += 20;
        if (result.competitor_data?.length) currentProgress += 20;
        if (result.analysis?.app_analysis) currentProgress += 20;
        if (result.analysis?.competitor_analysis) currentProgress += 20;
        if (result.analysis?.market_trends) currentProgress += 20;
        setProgress(currentProgress);
      }
      
      return {
        app_metadata: result.app_data,
        analysis: result.analysis?.app_analysis,
        competitor_analysis: result.analysis?.competitor_analysis,
        keyword_suggestions: result.analysis?.keyword_suggestions,
        market_trends: result.analysis?.market_trends,
        description_optimization: result.analysis?.description_optimization
      };
    },
    {
      enabled: !!taskId && isAnalyzing,
      refetchInterval: (data, query) => {
        if (!isAnalyzing) return false;
        if (query.state.error) return false;
        return 2000;  // Poll every 2 seconds
      },
      retry: 3,
      retryDelay: 1000,
      onError: (error) => {
        console.error('Error fetching results:', error);
        setIsAnalyzing(false);
        setProgress(0);
      }
    }
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setTaskId(null);
    setProgress(0);
    setIsAnalyzing(false);
    await createJob();
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
          className={`inline-flex justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 ${
            isAnalyzing || isLoading || isJobLoading
              ? 'bg-indigo-400 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700'
          }`}
          disabled={isAnalyzing || isLoading || isJobLoading}
        >
          {isAnalyzing ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing...
            </span>
          ) : isLoading || isJobLoading ? (
            'Starting analysis...'
          ) : (
            'Analyze'
          )}
        </button>
      </form>

      {(error || jobError) && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
          <div className="flex items-center">
            <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Error: {(error || jobError).message}</span>
          </div>
          <div className="mt-2 text-sm text-red-600">
            {error?.message?.includes('timeout') && (
              <p>The analysis is taking longer than expected. Please try again with fewer competitors or keywords.</p>
            )}
            {error?.message?.includes('rate limit') && (
              <p>We're processing too many requests. Please wait a few minutes and try again.</p>
            )}
          </div>
          <div className="mt-4 flex space-x-4">
            <button
              onClick={() => createJob()}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Retry Analysis
            </button>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 hover:text-red-800 focus:outline-none"
            >
              Reset Form
            </button>
          </div>
        </div>
      )}

      {(isAnalyzing || isLoading || isJobLoading) && (
        <div className="mt-4">
          <div className="relative pt-1">
            <div className="flex mb-2 items-center justify-between">
              <div>
                <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-200">
                  {isJobLoading ? "Starting Analysis" : "Analyzing"}
                </span>
              </div>
              <div className="text-right">
                <span className="text-xs font-semibold inline-block text-indigo-600">
                  {progress}%
                </span>
              </div>
            </div>
            <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-indigo-200">
              <div
                style={{ width: `${progress}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500 transition-all duration-500"
              />
            </div>
            <div className="text-sm text-gray-600 text-center">
              {isJobLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-500 mr-2"></div>
                  Starting analysis...
                </div>
              ) : (
                <>
                  {progress === 0 && "Initializing analysis..."}
                  {progress > 0 && progress < 20 && "Fetching app metadata..."}
                  {progress >= 20 && progress < 40 && "Analyzing competitor data..."}
                  {progress >= 40 && progress < 60 && "Generating insights..."}
                  {progress >= 60 && progress < 80 && "Optimizing recommendations..."}
                  {progress >= 80 && progress < 100 && "Finalizing analysis..."}
                  {progress === 100 && "Analysis complete!"}
                </>
              )}
            </div>
          </div>
          <div className="mt-4 text-xs text-gray-500">
            {progress >= 20 && (
              <div className="space-y-1">
                {progress >= 20 && <div>✓ App metadata collected</div>}
                {progress >= 40 && <div>✓ Competitor data analyzed</div>}
                {progress >= 60 && <div>✓ Market insights generated</div>}
                {progress >= 80 && <div>✓ Recommendations optimized</div>}
                {progress === 100 && <div>✓ Analysis completed</div>}
              </div>
            )}
          </div>
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

          {data.analysis && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Analysis</h3>
              <div className="mt-2 p-4 bg-gray-100 rounded-md">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Title Analysis</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.analysis.title_analysis || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Description Analysis</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.analysis.description_analysis || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Keyword Opportunities</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.analysis.keyword_opportunities || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Recommendations</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.analysis.recommendations || 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          )}

          {data.competitor_analysis && (
            <div>
              <h3 className="text-lg font-medium text-gray-900">Competitor Analysis</h3>
              <div className="mt-2 p-4 bg-gray-100 rounded-md">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Competitive Analysis</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.competitor_analysis.competitive_analysis || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Keyword Comparison</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.competitor_analysis.keyword_comparison || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Description Comparison</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.competitor_analysis.description_comparison || 'N/A'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Market Position</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {data.competitor_analysis.market_position || 'N/A'}
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