import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import KeywordTable from '../KeywordTable';

describe('KeywordTable', () => {
  const mockData = {
    analysis: {
      variations: [
        {
          keyword: 'b2b wholesale',
          relevance: 0.9,
          competition: 'high',
          priority: 'high'
        },
        {
          keyword: 'wholesale app',
          relevance: 0.8,
          competition: 'medium',
          priority: 'medium'
        }
      ],
      long_tail: [
        {
          keyword: 'best b2b wholesale platform',
          search_intent: 'transactional',
          opportunity: 'high'
        }
      ],
      related_terms: [
        {
          term: 'supply chain',
          relevance: 0.7,
          category: 'business'
        }
      ],
      recommendations: [
        'Focus on high-priority keywords',
        'Target long-tail opportunities'
      ]
    }
  };

  it('renders without crashing', () => {
    render(<KeywordTable data={mockData} />);
    expect(screen.getByTestId('keyword-table')).toBeInTheDocument();
  });

  it('displays all keywords by default', () => {
    render(<KeywordTable data={mockData} />);
    expect(screen.getByText('b2b wholesale')).toBeInTheDocument();
    expect(screen.getByText('wholesale app')).toBeInTheDocument();
    expect(screen.getByText('best b2b wholesale platform')).toBeInTheDocument();
    expect(screen.getByText('supply chain')).toBeInTheDocument();
  });

  it('filters keywords correctly', () => {
    render(<KeywordTable data={mockData} />);
    
    // Filter by high priority
    fireEvent.change(screen.getByRole('combobox'), {
      target: { value: 'high' }
    });
    expect(screen.getByText('b2b wholesale')).toBeInTheDocument();
    expect(screen.queryByText('wholesale app')).not.toBeInTheDocument();
  });

  it('handles search functionality', () => {
    render(<KeywordTable data={mockData} />);
    
    fireEvent.change(screen.getByPlaceholderText('Search keywords...'), {
      target: { value: 'b2b' }
    });
    
    expect(screen.getByText('b2b wholesale')).toBeInTheDocument();
    expect(screen.queryByText('supply chain')).not.toBeInTheDocument();
  });

  it('shows recommendations', () => {
    render(<KeywordTable data={mockData} />);
    expect(screen.getByText('Optimization Tips')).toBeInTheDocument();
    expect(screen.getByText('Focus on high-priority keywords')).toBeInTheDocument();
  });

  it('handles missing data gracefully', () => {
    render(<KeywordTable data={{}} />);
    expect(screen.getByText('Keyword Analysis')).toBeInTheDocument();
    expect(screen.queryByRole('row')).not.toBeInTheDocument();
  });

  it('displays correct badge colors', () => {
    render(<KeywordTable data={mockData} />);
    
    // Priority badges
    expect(screen.getByText('high')).toHaveClass('bg-red-100');
    expect(screen.getByText('medium')).toHaveClass('bg-yellow-100');
    
    // Type badges
    expect(screen.getByText('variation')).toHaveClass('bg-blue-100');
    expect(screen.getByText('long_tail')).toHaveClass('bg-purple-100');
    expect(screen.getByText('related')).toHaveClass('bg-green-100');
  });
});