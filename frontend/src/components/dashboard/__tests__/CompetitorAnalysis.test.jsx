import React from 'react';
import { render, screen } from '@testing-library/react';
import CompetitorAnalysis from '../CompetitorAnalysis';

// Mock Nivo bar chart
jest.mock('@nivo/bar', () => ({
  ResponsiveBar: () => <div data-testid="bar-chart" />
}));

describe('CompetitorAnalysis', () => {
  const mockData = {
    metadata_analysis: {
      analysis: {
        competitive_analysis: {
          strengths: ['Strong feature set', 'Good user experience'],
          weaknesses: ['Limited market reach', 'Missing key features']
        },
        feature_gaps: [
          {
            feature: 'Bulk ordering',
            priority: 'high',
            competitors: ['Competitor A', 'Competitor B']
          }
        ],
        recommendations: [
          'Implement bulk ordering',
          'Expand market reach'
        ]
      }
    },
    competitors: [
      {
        name: 'Competitor A',
        metrics: {
          market_share: 30,
          growth_rate: 15
        }
      },
      {
        name: 'Competitor B',
        metrics: {
          market_share: 25,
          growth_rate: 20
        }
      }
    ]
  };

  it('renders without crashing', () => {
    render(<CompetitorAnalysis data={mockData} />);
    expect(screen.getByTestId('competitor-analysis')).toBeInTheDocument();
  });

  it('displays competitor chart', () => {
    render(<CompetitorAnalysis data={mockData} />);
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('shows strengths and weaknesses', () => {
    render(<CompetitorAnalysis data={mockData} />);
    expect(screen.getByText('Strong feature set')).toBeInTheDocument();
    expect(screen.getByText('Limited market reach')).toBeInTheDocument();
  });

  it('displays feature gaps', () => {
    render(<CompetitorAnalysis data={mockData} />);
    expect(screen.getByText('Bulk ordering')).toBeInTheDocument();
    expect(screen.getByText('high priority')).toBeInTheDocument();
  });

  it('shows recommendations', () => {
    render(<CompetitorAnalysis data={mockData} />);
    expect(screen.getByText('Implement bulk ordering')).toBeInTheDocument();
    expect(screen.getByText('Expand market reach')).toBeInTheDocument();
  });

  it('handles missing data gracefully', () => {
    render(<CompetitorAnalysis data={{}} />);
    expect(screen.getByText('No competitor analysis available')).toBeInTheDocument();
  });

  it('shows correct status icons', () => {
    render(<CompetitorAnalysis data={mockData} />);
    const strengthsIcon = screen.getByText('Strengths').previousSibling;
    const weaknessesIcon = screen.getByText('Weaknesses').previousSibling;
    
    expect(strengthsIcon).toHaveClass('text-green-500');
    expect(weaknessesIcon).toHaveClass('text-red-500');
  });
});