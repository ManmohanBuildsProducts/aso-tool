import React from 'react';
import { ResponsiveBar } from '@nivo/bar';
import { HiExclamationCircle, HiCheckCircle, HiXCircle } from 'react-icons/hi';

const CompetitorAnalysis = ({ data }) => {
  if (!data) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 h-[400px] flex items-center justify-center">
        <div className="text-center text-gray-500">
          <HiExclamationCircle className="w-8 h-8 mx-auto mb-2" />
          <p>No competitor analysis available</p>
        </div>
      </div>
    );
  }

  const analysis = data;
  
  // Prepare data for the chart based on keyword gaps
  const chartData = analysis.keyword_gaps.map(gap => ({
    name: gap.keyword,
    value: gap.importance === 'high' ? 80 : gap.importance === 'medium' ? 50 : 30,
    competitor_usage: gap.competitor_usage
  })).slice(0, 5);  // Show top 5 keyword gaps

  const getStatusIcon = (type) => {
    switch(type) {
      case 'strength':
        return <HiCheckCircle className="w-5 h-5 text-green-500" />;
      case 'weakness':
        return <HiXCircle className="w-5 h-5 text-red-500" />;
      default:
        return <HiExclamationCircle className="w-5 h-5 text-yellow-500" />;
    }
  };

  if (!analysis) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 h-[400px] flex items-center justify-center">
        <div className="text-center text-gray-500">
          <HiExclamationCircle className="w-8 h-8 mx-auto mb-2" />
          <p>No competitor analysis available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6" data-testid="competitor-analysis">
      <h2 className="text-xl font-bold text-gray-900 mb-6">
        Competitor Analysis
      </h2>

      {/* Competitive Position */}
      <div className="h-[300px] mb-6">
        <ResponsiveBar
          data={chartData}
          keys={['value']}
          indexBy="name"
          margin={{ top: 20, right: 120, bottom: 50, left: 60 }}
          padding={0.3}
          valueScale={{ type: 'linear', min: 0, max: 100 }}
          indexScale={{ type: 'band', round: true }}
          colors={{ scheme: 'category10' }}
          borderColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
          axisTop={null}
          axisRight={null}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: -45,
            legend: 'Keywords',
            legendPosition: 'middle',
            legendOffset: 40
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Importance Score',
            legendPosition: 'middle',
            legendOffset: -40
          }}
          labelSkipWidth={12}
          labelSkipHeight={12}
          labelTextColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
          legends={[
            {
              dataFrom: 'keys',
              anchor: 'bottom-right',
              direction: 'column',
              justify: false,
              translateX: 120,
              translateY: 0,
              itemsSpacing: 2,
              itemWidth: 100,
              itemHeight: 20,
              itemDirection: 'left-to-right',
              itemOpacity: 0.85,
              symbolSize: 20,
              effects: [
                {
                  on: 'hover',
                  style: {
                    itemOpacity: 1
                  }
                }
              ]
            }
          ]}
          animate={true}
          motionConfig="gentle"
        />
      </div>

      {/* SWOT Analysis */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="font-medium text-green-900 mb-2 flex items-center gap-2">
            <HiCheckCircle className="w-5 h-5" />
            Strengths
          </h3>
          <ul className="space-y-2 text-sm text-green-700">
            {analysis.competitive_analysis.strengths.map((strength, index) => (
              <li key={index} className="flex items-start gap-2">
                <span>•</span>
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-red-50 rounded-lg p-4">
          <h3 className="font-medium text-red-900 mb-2 flex items-center gap-2">
            <HiXCircle className="w-5 h-5" />
            Weaknesses
          </h3>
          <ul className="space-y-2 text-sm text-red-700">
            {analysis.competitive_analysis.weaknesses.map((weakness, index) => (
              <li key={index} className="flex items-start gap-2">
                <span>•</span>
                <span>{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Feature Gaps */}
      <div className="mb-6">
        <h3 className="font-medium text-gray-900 mb-2">
          Feature Gaps
        </h3>
        <div className="space-y-3">
          {analysis.feature_gaps.map((gap, index) => (
            <div 
              key={index}
              className="bg-gray-50 rounded-lg p-3 flex items-center justify-between"
            >
              <div>
                <div className="font-medium text-gray-900">
                  {gap.feature}
                </div>
                <div className="text-sm text-gray-500">
                  Used by: {gap.competitors.join(', ')}
                </div>
              </div>
              <span className={`
                text-xs px-2 py-1 rounded-full
                ${gap.priority === 'high' 
                  ? 'bg-red-100 text-red-700'
                  : 'bg-yellow-100 text-yellow-700'}
              `}>
                {gap.priority} priority
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-blue-50 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">
          Action Items
        </h3>
        <ul className="space-y-2 text-sm text-blue-700">
          {analysis.recommendations.map((rec, index) => (
            <li key={index} className="flex items-start gap-2">
              <span>•</span>
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default CompetitorAnalysis;