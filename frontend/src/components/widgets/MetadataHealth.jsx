import React, { useState, useEffect } from 'react';
import { HiCheck, HiX, HiPencil } from 'react-icons/hi';

const MetadataHealth = ({ appId }) => {
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSection, setSelectedSection] = useState('title');

  useEffect(() => {
    fetchMetadata();
  }, [appId]);

  const fetchMetadata = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/ai/metadata/title/${appId}`);
      const data = await response.json();
      setMetadata(data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching metadata:', err);
      setLoading(false);
    }
  };

  const getHealthIndicator = (score) => {
    if (score >= 80) {
      return (
        <div className="flex items-center text-green-600">
          <HiCheck className="w-5 h-5" />
          <span className="ml-1">Good</span>
        </div>
      );
    } else if (score >= 50) {
      return (
        <div className="flex items-center text-yellow-600">
          <HiPencil className="w-5 h-5" />
          <span className="ml-1">Needs Work</span>
        </div>
      );
    }
    return (
      <div className="flex items-center text-red-600">
        <HiX className="w-5 h-5" />
        <span className="ml-1">Poor</span>
      </div>
    );
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
      <h2 className="text-xl font-semibold text-gray-800 mb-6">
        Metadata Health
      </h2>

      <div className="flex space-x-2 mb-6">
        {['title', 'description', 'screenshots'].map(section => (
          <button
            key={section}
            onClick={() => setSelectedSection(section)}
            className={`px-4 py-2 rounded-lg ${
              selectedSection === section
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {section.charAt(0).toUpperCase() + section.slice(1)}
          </button>
        ))}
      </div>

      {selectedSection === 'title' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <div className="text-gray-600">Title Health</div>
            {getHealthIndicator(metadata?.title_score || 0)}
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="font-medium text-gray-800 mb-2">
                Current Title
              </div>
              <div className="text-gray-600">
                {metadata?.current_title || 'No title found'}
              </div>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="font-medium text-blue-800 mb-2">
                Suggested Improvements
              </div>
              <ul className="space-y-2 text-blue-600">
                {metadata?.title_suggestions?.map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span>•</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {selectedSection === 'description' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <div className="text-gray-600">Description Health</div>
            {getHealthIndicator(metadata?.description_score || 0)}
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="font-medium text-gray-800 mb-2">
                Key Points Coverage
              </div>
              <div className="grid grid-cols-2 gap-3">
                {metadata?.description_checklist?.map((item, index) => (
                  <div 
                    key={index}
                    className="flex items-center gap-2"
                  >
                    {item.covered ? (
                      <HiCheck className="text-green-500" />
                    ) : (
                      <HiX className="text-red-500" />
                    )}
                    <span className="text-sm text-gray-600">
                      {item.point}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="font-medium text-blue-800 mb-2">
                Recommended Updates
              </div>
              <ul className="space-y-2 text-blue-600">
                {metadata?.description_recommendations?.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span>•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {selectedSection === 'screenshots' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <div className="text-gray-600">Screenshots Health</div>
            {getHealthIndicator(metadata?.screenshots_score || 0)}
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="font-medium text-gray-800 mb-2">
                Screenshot Analysis
              </div>
              <div className="grid grid-cols-1 gap-3">
                {metadata?.screenshot_analysis?.map((analysis, index) => (
                  <div 
                    key={index}
                    className="flex items-start justify-between p-2 border-b"
                  >
                    <div>
                      <div className="font-medium">
                        Screenshot {index + 1}
                      </div>
                      <div className="text-sm text-gray-600">
                        {analysis.feedback}
                      </div>
                    </div>
                    <div className={`text-${
                      analysis.score >= 80 ? 'green' :
                      analysis.score >= 50 ? 'yellow' : 'red'
                    }-600 font-bold`}>
                      {analysis.score}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="font-medium text-blue-800 mb-2">
                Improvement Suggestions
              </div>
              <ul className="space-y-2 text-blue-600">
                {metadata?.screenshot_recommendations?.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span>•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MetadataHealth;