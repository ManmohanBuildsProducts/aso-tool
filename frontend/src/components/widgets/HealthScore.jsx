import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { HiTrendingUp, HiTrendingDown } from 'react-icons/hi';

const calculateMetricScore = (...sections) => {
  // Count recommendations and issues
  let recommendations = 0;
  let issues = 0;
  
  sections.forEach(section => {
    if (!section) return;
    
    // Count positive indicators
    recommendations += (section.match(/recommend|suggest|consider|improve|optimize/gi) || []).length;
    
    // Count negative indicators
    issues += (section.match(/lack|miss|need|should|could|better|problem/gi) || []).length;
  });
  
  // Calculate score based on ratio of recommendations to issues
  const total = recommendations + issues;
  if (total === 0) return 50;  // Default score
  
  const score = Math.round((recommendations / total) * 100);
  return Math.min(Math.max(score, 0), 100);  // Clamp between 0-100
};

const HealthScore = ({ data }) => {
  // Extract metrics from sections
  const metrics = {
    keyword_optimization: calculateMetricScore(data?.sections?.['keyword opportunities']),
    metadata_quality: calculateMetricScore(data?.sections?.['title optimization'], data?.sections?.['description analysis']),
    competitive_position: calculateMetricScore(data?.sections?.['competitive advantages']),
    feature_coverage: calculateMetricScore(data?.sections?.['feature recommendations'])
  };
  
  // Calculate overall score
  const score = Math.round(
    Object.values(metrics).reduce((a, b) => a + b, 0) / Object.keys(metrics).length
  );
  const getScoreColor = (value) => {
    if (value >= 80) return '#22c55e';
    if (value >= 60) return '#eab308';
    return '#ef4444';
  };

  const getTrendIcon = (trend) => {
    if (trend > 0) {
      return <HiTrendingUp className="w-5 h-5 text-green-500" />;
    }
    return <HiTrendingDown className="w-5 h-5 text-red-500" />;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-start">
        <div className="w-32">
          <CircularProgressbar
            value={score}
            text={`${score}%`}
            styles={buildStyles({
              pathColor: getScoreColor(score),
              textColor: '#1f2937',
              trailColor: '#f3f4f6'
            })}
          />
        </div>
        
        <div className="ml-8 flex-1">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            ASO Health Score
          </h2>
          
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(metrics).map(([key, value]) => (
              <div 
                key={key}
                className="bg-gray-50 rounded-lg p-3"
              >
                <div className="text-sm text-gray-500 capitalize">
                  {key.replace(/_/g, ' ')}
                </div>
                <div className="flex items-center mt-1">
                  <span className="text-xl font-bold text-gray-900">
                    {value}%
                  </span>
                  <span className="ml-2">
                    {getTrendIcon(value > 70 ? 'up' : value > 50 ? 'stable' : 'down')}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Recommendations */}
          {data?.sections?.['recommendations'] && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">
                Recommendations
              </h3>
              <ul className="space-y-2 text-sm text-blue-700">
                {data.sections['recommendations']
                  .split('\n')
                  .filter(line => line.trim().startsWith('-') || line.trim().startsWith('•'))
                  .map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span>•</span>
                      <span>{rec.replace(/^[-•]\s*/, '').trim()}</span>
                    </li>
                  ))
                }
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HealthScore;