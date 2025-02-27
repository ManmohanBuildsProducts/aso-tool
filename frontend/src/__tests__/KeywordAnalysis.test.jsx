import React from 'react';
import { render, screen } from '@testing-library/react';
import KeywordAnalysis from '../components/KeywordAnalysis';

const mockData = {
  keyword_analysis: {
    keyword_trends: {
      'test': {
        difficulty_score: 65,
        search_volume: 'High',
        ranking_potential: 'Medium'
      },
      'app': {
        difficulty_score: 85,
        search_volume: 'Very High',
        ranking_potential: 'Low'
      },
      'game': {
        difficulty_score: 45,
        search_volume: 'Medium',
        ranking_potential: 'High'
      }
    }
  }
};

describe('KeywordAnalysis Component', () => {
  it('renders without crashing', () => {
    render(<KeywordAnalysis data={mockData} />);
    expect(screen.getByText('Keyword Analysis')).toBeInTheDocument();
  });

  it('displays keyword metrics correctly', () => {
    render(<KeywordAnalysis data={mockData} />);
    
    // Check if all keywords are displayed
    expect(screen.getByText('test')).toBeInTheDocument();
    expect(screen.getByText('app')).toBeInTheDocument();
    expect(screen.getByText('game')).toBeInTheDocument();
    
    // Check if metrics are displayed
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('Very High')).toBeInTheDocument();
    expect(screen.getByText('Medium')).toBeInTheDocument();
  });

  it('handles missing data gracefully', () => {
    render(<KeywordAnalysis data={null} />);
    expect(screen.getByText('Keyword Analysis')).toBeInTheDocument();
    // Should show empty state or placeholder
  });

  it('displays correct status chips', () => {
    render(<KeywordAnalysis data={mockData} />);
    
    // Check status indicators
    expect(screen.getByText('Good')).toBeInTheDocument();
    expect(screen.getByText('Poor')).toBeInTheDocument();
    expect(screen.getByText('Excellent')).toBeInTheDocument();
  });

  it('shows keyword metrics visualization', () => {
    render(<KeywordAnalysis data={mockData} />);
    expect(screen.getByText('Keyword Metrics Visualization')).toBeInTheDocument();
  });
});