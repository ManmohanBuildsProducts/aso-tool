import React, { useState, useEffect } from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

const HealthScore = ({ appId }) => {
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealthScore();
  }, [appId]);

  const fetchHealthScore = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/ai/analyze/${appId}`);
      const data = await response.json();
      
      // Calculate overall health score from various metrics
      const metrics = {
        keywordOptimization: data.keyword_score || 0,
        metadataQuality: data.metadata_score || 0,
        competitivePosition: data.competitive_score || 0,
        userEngagement: data.engagement_score || 0
      };
      
      const overallScore = Math.round(
        Object.values(metrics).reduce((a, b) => a + b, 0) / Object.keys(metrics).length
      );
      
      setScore({
        overall: overallScore,
        metrics: metrics
      });
      setLoading(false);
    } catch (err) {
      console.error('Error fetching health score:', err);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse bg-white rounded-lg shadow p-6">
        <div className="h-40 bg-gray-200 rounded-full w-40 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 text-center">
        ASO Health Score
      </h2>
      
      <div className="flex flex-col md:flex-row items-center justify-center gap-8">
        {/* Main Score */}
        <div className="w-40 h-40">
          <CircularProgressbar
            value={score?.overall || 0}
            text={`${score?.overall || 0}%`}
            styles={buildStyles({
              textSize: '16px',
              pathColor: score?.overall > 70 ? '#22c55e' : 
                        score?.overall > 40 ? '#eab308' : '#ef4444',
              textColor: '#1f2937',
              trailColor: '#f3f4f6'
            })}
          />
        </div>

        {/* Score Breakdown */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-sm text-green-600">Keyword Optimization</div>
            <div className="text-2xl font-bold text-green-700">
              {score?.metrics.keywordOptimization}%
            </div>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-sm text-blue-600">Metadata Quality</div>
            <div className="text-2xl font-bold text-blue-700">
              {score?.metrics.metadataQuality}%
            </div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-sm text-purple-600">Competitive Position</div>
            <div className="text-2xl font-bold text-purple-700">
              {score?.metrics.competitivePosition}%
            </div>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-sm text-yellow-600">User Engagement</div>
            <div className="text-2xl font-bold text-yellow-700">
              {score?.metrics.userEngagement}%
            </div>
          </div>
        </div>
      </div>

      {/* Quick Tips */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium text-gray-700 mb-2">Quick Wins</h3>
        <ul className="text-sm text-gray-600 space-y-2">
          {score?.overall < 70 && (
            <>
              {score?.metrics.keywordOptimization < 70 && (
                <li>• Add more relevant keywords to your app title and description</li>
              )}
              {score?.metrics.metadataQuality < 70 && (
                <li>• Improve your app description with more feature highlights</li>
              )}
              {score?.metrics.competitivePosition < 70 && (
                <li>• Target some less competitive keywords to improve rankings</li>
              )}
              {score?.metrics.userEngagement < 70 && (
                <li>• Encourage more user reviews and ratings</li>
              )}
            </>
          )}
          {score?.overall >= 70 && (
            <li>• Your app is performing well! Keep monitoring for new opportunities.</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default HealthScore;