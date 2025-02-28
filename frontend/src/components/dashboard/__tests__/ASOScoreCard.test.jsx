import React from 'react';
import { render, screen } from '@testing-library/react';
import ASOScoreCard from '../ASOScoreCard';

describe('ASOScoreCard', () => {
  const mockData = {
    analysis: {
      title_analysis: {
        current_score: 85
      },
      description_analysis: {
        current_score: 75
      },
      recommendations: [
        'Improve title keywords',
        'Add more features to description',
        'Optimize screenshots'
      ]
    }
  };

  it('renders without crashing', () => {
    render(<ASOScoreCard data={mockData} />);
    expect(screen.getByTestId('aso-score-card')).toBeInTheDocument();
  });

  it('displays correct scores', () => {
    render(<ASOScoreCard data={mockData} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('shows recommendations', () => {
    render(<ASOScoreCard data={mockData} />);
    expect(screen.getByText('Quick Wins')).toBeInTheDocument();
    expect(screen.getByText('Improve title keywords')).toBeInTheDocument();
  });

  it('handles missing data gracefully', () => {
    render(<ASOScoreCard data={{}} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('shows correct score colors', () => {
    const { rerender } = render(<ASOScoreCard data={mockData} />);
    
    // High score
    expect(screen.getByTestId('aso-score-card')).toHaveStyle({
      '--score-color': '#22c55e'
    });

    // Medium score
    rerender(<ASOScoreCard data={{
      analysis: {
        title_analysis: { current_score: 65 },
        description_analysis: { current_score: 65 }
      }
    }} />);
    expect(screen.getByTestId('aso-score-card')).toHaveStyle({
      '--score-color': '#eab308'
    });

    // Low score
    rerender(<ASOScoreCard data={{
      analysis: {
        title_analysis: { current_score: 45 },
        description_analysis: { current_score: 45 }
      }
    }} />);
    expect(screen.getByTestId('aso-score-card')).toHaveStyle({
      '--score-color': '#ef4444'
    });
  });
});