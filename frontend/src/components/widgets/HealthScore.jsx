import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { HiTrendingUp, HiTrendingDown } from 'react-icons/hi';

const HealthScore = ({ score, metrics }) => {
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
            {Object.entries(metrics || {}).map(([key, value]) => (
              <div 
                key={key}
                className="bg-gray-50 rounded-lg p-3"
              >
                <div className="text-sm text-gray-500 capitalize">
                  {key.replace('_', ' ')}
                </div>
                <div className="flex items-center mt-1">
                  <span className="text-xl font-bold text-gray-900">
                    {value.score}%
                  </span>
                  <span className="ml-2">
                    {getTrendIcon(value.trend)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthScore;