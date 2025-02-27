import React from 'react';
import { render, screen } from '@testing-library/react';
import ComparisonCharts from '../components/ComparisonCharts';

const mockData = {
  main_app: {
    app_id: 'com.test.app',
    details: {
      score: 4.5,
      minInstalls: 1000000,
      reviews: 50000,
    }
  },
  competitors: [
    {
      app_id: 'com.competitor1',
      details: {
        score: 4.2,
        minInstalls: 800000,
        reviews: 40000,
      }
    },
    {
      app_id: 'com.competitor2',
      details: {
        score: 4.7,
        minInstalls: 1200000,
        reviews: 60000,
      }
    }
  ],
  keyword_analysis: {
    keyword_trends: {
      'test': {
        difficulty_score: 65,
        search_volume: 'High'
      },
      'app': {
        difficulty_score: 85,
        search_volume: 'Very High'
      }
    }
  },
  review_analysis: {
    sentiment_trends: {
      '2024-02-26': { compound: 0.8 },
      '2024-02-27': { compound: 0.75 }
    }
  }
};

describe('ComparisonCharts Component', () => {
  it('renders without crashing', () => {
    render(<ComparisonCharts data={mockData} />);
    expect(screen.getByText('Key Metrics Comparison')).toBeInTheDocument();
  });

  it('displays all chart sections', () => {
    render(<ComparisonCharts data={mockData} />);
    expect(screen.getByText('Key Metrics Comparison')).toBeInTheDocument();
    expect(screen.getByText('Keyword Difficulty')).toBeInTheDocument();
    expect(screen.getByText('Review Sentiment Trends')).toBeInTheDocument();
  });

  it('handles missing data gracefully', () => {
    render(<ComparisonCharts data={null} />);
    // Should not crash and should show empty state
    expect(screen.getByText('Key Metrics Comparison')).toBeInTheDocument();
  });

  it('displays correct number of competitors', () => {
    render(<ComparisonCharts data={mockData} />);
    // Check if all apps are represented in the chart
    expect(screen.getByText('com.test.app')).toBeInTheDocument();
    expect(screen.getByText('com.competitor1')).toBeInTheDocument();
    expect(screen.getByText('com.competitor2')).toBeInTheDocument();
  });
});