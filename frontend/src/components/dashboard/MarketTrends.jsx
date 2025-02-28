import React from 'react';
import { 
  TrendingUpIcon, 
  UserGroupIcon, 
  CurrencyDollarIcon 
} from '@heroicons/react/outline';

const MarketTrends = ({ data }) => {
  if (!data) {
    return (
      <div className="text-gray-500 text-center py-4">
        No market trend data available
      </div>
    );
  }

  const { market_trends, user_preferences, monetization_insights } = data;

  return (
    <div className="space-y-6">
      {/* Market Trends */}
      <div>
        <h3 className="text-lg font-medium mb-3 flex items-center">
          <TrendingUpIcon className="h-5 w-5 mr-2 text-blue-500" />
          Market Trends
        </h3>
        <div className="space-y-3">
          {market_trends.map((trend, index) => (
            <div 
              key={index}
              className="bg-gray-50 p-3 rounded-lg"
            >
              <div className="font-medium">{trend.trend}</div>
              <div className="flex justify-between text-sm mt-2">
                <span className={`px-2 py-1 rounded ${
                  trend.impact === 'high' ? 'bg-red-100 text-red-700' :
                  trend.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {trend.impact} impact
                </span>
                <span className="text-gray-500">{trend.timeframe}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* User Preferences */}
      <div>
        <h3 className="text-lg font-medium mb-3 flex items-center">
          <UserGroupIcon className="h-5 w-5 mr-2 text-green-500" />
          User Preferences
        </h3>
        <div className="space-y-3">
          {user_preferences.map((pref, index) => (
            <div 
              key={index}
              className="flex justify-between items-center bg-gray-50 p-3 rounded-lg"
            >
              <div>
                <div className="font-medium">{pref.feature}</div>
                <div className="text-sm text-gray-500">
                  {pref.importance} importance
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold">{pref.adoption_rate}</div>
                <div className="text-sm text-gray-500">adoption rate</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Monetization Insights */}
      <div>
        <h3 className="text-lg font-medium mb-3 flex items-center">
          <CurrencyDollarIcon className="h-5 w-5 mr-2 text-yellow-500" />
          Monetization Insights
        </h3>
        <div className="space-y-3">
          {monetization_insights.map((insight, index) => (
            <div 
              key={index}
              className="bg-gray-50 p-3 rounded-lg"
            >
              <div className="font-medium">{insight.strategy}</div>
              <div className="flex justify-between text-sm mt-2">
                <span className={`px-2 py-1 rounded ${
                  insight.effectiveness === 'high' ? 'bg-green-100 text-green-700' :
                  insight.effectiveness === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {insight.effectiveness} effectiveness
                </span>
                <span className="font-medium">{insight.market_share} market share</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarketTrends;