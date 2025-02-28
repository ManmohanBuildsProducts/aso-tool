import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { HiTrendingUp, HiTrendingDown } from 'react-icons/hi';

const ASOScoreCard = ({ data }) => {
  const titleScore = data?.analysis?.title_analysis?.current_score || 0;
  const descScore = data?.analysis?.description_analysis?.current_score || 0;
  const overallScore = Math.round((titleScore + descScore) / 2);

  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    return '#ef4444';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6" data-testid="aso-score-card">
      <div className="flex items-start">
        <div className="w-32">
          <CircularProgressbar
            value={overallScore}
            text={`${overallScore}%`}
            styles={buildStyles({
              pathColor: getScoreColor(overallScore),
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
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-500">Title Score</div>
              <div className="flex items-center mt-1">
                <span className="text-xl font-bold text-gray-900">
                  {titleScore}%
                </span>
                <span className="ml-2">
                  {titleScore >= 70 ? (
                    <HiTrendingUp className="w-5 h-5 text-green-500" />
                  ) : (
                    <HiTrendingDown className="w-5 h-5 text-red-500" />
                  )}
                </span>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-500">Description Score</div>
              <div className="flex items-center mt-1">
                <span className="text-xl font-bold text-gray-900">
                  {descScore}%
                </span>
                <span className="ml-2">
                  {descScore >= 70 ? (
                    <HiTrendingUp className="w-5 h-5 text-green-500" />
                  ) : (
                    <HiTrendingDown className="w-5 h-5 text-red-500" />
                  )}
                </span>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {data?.analysis?.recommendations && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">
                Quick Wins
              </h3>
              <ul className="space-y-2 text-sm text-blue-700">
                {data.analysis.recommendations.slice(0, 3).map((rec, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span>•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ASOScoreCard;