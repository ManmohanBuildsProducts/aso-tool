import React from 'react';
import { ResponsiveScatterPlot } from '@nivo/scatterplot';
import { HiInformationCircle } from 'react-icons/hi';

const MarketPosition = ({ data }) => {
  // Extract insights from competitive advantages text
  const insights = React.useMemo(() => {
    if (!data) return [];
    
    return data
      .split('\n')
      .filter(line => line.trim().startsWith('-') || line.trim().startsWith('•'))
      .map(line => line.replace(/^[-•]\s*/, '').trim());
  }, [data]);

  // Generate mock position data for visualization
  const positionData = React.useMemo(() => {
    return insights.map((insight, index) => ({
      id: index,
      x: 50 + Math.random() * 30 - 15,  // Cluster around center
      y: 50 + Math.random() * 30 - 15,
      name: insight
    }));
  }, [insights]);

  if (!data) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 h-[400px] flex items-center justify-center">
        <div className="text-center text-gray-500">
          <HiInformationCircle className="w-8 h-8 mx-auto mb-2" />
          <p>No market position data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        Market Position
      </h2>
      
      <div className="h-[350px]">
        <ResponsiveScatterPlot
          data={[
            {
              id: 'competitors',
              data: position.data
            }
          ]}
          margin={{ top: 20, right: 20, bottom: 70, left: 70 }}
          xScale={{ type: 'linear', min: 0, max: 100 }}
          yScale={{ type: 'linear', min: 0, max: 100 }}
          blendMode="multiply"
          axisTop={null}
          axisRight={null}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Market Share',
            legendPosition: 'middle',
            legendOffset: 46
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Growth Rate',
            legendPosition: 'middle',
            legendOffset: -60
          }}
          colors={{ scheme: 'category10' }}
          tooltip={({ node }) => (
            <div className="bg-white p-2 shadow rounded border">
              <strong>{node.data.name}</strong>
              <div>Market Share: {node.data.x}%</div>
              <div>Growth Rate: {node.data.y}%</div>
            </div>
          )}
        />
      </div>

      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">
          Key Insights
        </h3>
        <ul className="space-y-2 text-sm text-blue-700">
          {position.insights?.map((insight, index) => (
            <li key={index} className="flex items-start gap-2">
              <span>•</span>
              <span>{insight}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default MarketPosition;