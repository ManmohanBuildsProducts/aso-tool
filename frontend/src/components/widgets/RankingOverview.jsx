import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { 
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const RankingOverview = ({ appId, keywords }) => {
  const [timeRange, setTimeRange] = useState('7d');
  const [rankingData, setRankingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState(null);

  useEffect(() => {
    fetchRankingData();
  }, [appId, timeRange]);

  const fetchRankingData = async () => {
    try {
      setLoading(true);
      // Fetch historical rankings
      const rankingsResponse = await fetch(
        `/api/rankings/history/${appId}?days=${timeRange === '7d' ? 7 : 30}`
      );
      const rankingsData = await rankingsResponse.json();

      // Fetch AI predictions
      const predictionsResponse = await fetch(
        `/api/ai/rankings/predict/${appId}/${keywords[0]}`
      );
      const predictionsData = await predictionsResponse.json();

      setRankingData(rankingsData);
      setPredictions(predictionsData);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="animate-pulse bg-gray-100 rounded-lg p-4">
      <div className="h-64 bg-gray-200 rounded"></div>
    </div>
  );

  if (error) return (
    <div className="bg-red-50 text-red-600 p-4 rounded-lg">
      Error loading ranking data: {error}
    </div>
  );

  const chartData = {
    labels: rankingData?.map(r => r.date) || [],
    datasets: [
      {
        label: 'Current Rankings',
        data: rankingData?.map(r => r.rank) || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      predictions && {
        label: 'Predicted Rankings',
        data: predictions?.map(p => p.rank) || [],
        borderColor: 'rgb(139, 92, 246)',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4
      }
    ].filter(Boolean)
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Keyword Ranking Trends'
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      y: {
        reverse: true,
        beginAtZero: true,
        title: {
          display: true,
          text: 'Ranking Position'
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800">
          Ranking Overview
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setTimeRange('7d')}
            className={`px-3 py-1 rounded ${
              timeRange === '7d'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            7D
          </button>
          <button
            onClick={() => setTimeRange('30d')}
            className={`px-3 py-1 rounded ${
              timeRange === '30d'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            30D
          </button>
        </div>
      </div>

      <div className="h-64">
        <Line data={chartData} options={chartOptions} />
      </div>

      {predictions?.analysis && (
        <div className="mt-4 p-4 bg-purple-50 rounded-lg">
          <h3 className="font-semibold text-purple-800 mb-2">
            AI Insights
          </h3>
          <div className="text-sm text-purple-700">
            {predictions.analysis.summary}
          </div>
        </div>
      )}

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-sm text-blue-600">Current Rank</div>
          <div className="text-2xl font-bold text-blue-700">
            #{rankingData?.[0]?.rank || '-'}
          </div>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="text-sm text-green-600">Best Rank</div>
          <div className="text-2xl font-bold text-green-700">
            #{Math.min(...(rankingData?.map(r => r.rank) || [0]))}
          </div>
        </div>
        <div className="bg-purple-50 p-3 rounded-lg">
          <div className="text-sm text-purple-600">Predicted</div>
          <div className="text-2xl font-bold text-purple-700">
            #{predictions?.nextRank || '-'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RankingOverview;