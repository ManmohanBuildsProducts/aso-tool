import React from 'react';
import { render, screen } from '@testing-library/react';
import MetadataComparison from '../components/MetadataComparison';

const mockData = {
  main_app: {
    app_id: 'com.test.app',
    details: {
      title: 'Test App',
      description: 'Test app description',
      score: 4.5,
      reviews: 50000,
      installs: '1,000,000+',
      updated: 1645900800, // Unix timestamp
      category: 'Tools'
    }
  },
  competitors: [
    {
      app_id: 'com.competitor1',
      details: {
        title: 'Competitor 1',
        description: 'Competitor 1 description',
        score: 4.2,
        reviews: 40000,
        installs: '800,000+',
        updated: 1645814400,
        category: 'Tools'
      }
    }
  ]
};

describe('MetadataComparison Component', () => {
  it('renders without crashing', () => {
    render(<MetadataComparison data={mockData} />);
    expect(screen.getByText('Metadata Comparison')).toBeInTheDocument();
  });

  it('displays main app data correctly', () => {
    render(<MetadataComparison data={mockData} />);
    expect(screen.getByText('Your App')).toBeInTheDocument();
    expect(screen.getByText('Test App')).toBeInTheDocument();
    expect(screen.getByText('4.50')).toBeInTheDocument();
  });

  it('displays competitor data correctly', () => {
    render(<MetadataComparison data={mockData} />);
    expect(screen.getByText('Competitor')).toBeInTheDocument();
    expect(screen.getByText('Competitor 1')).toBeInTheDocument();
    expect(screen.getByText('4.20')).toBeInTheDocument();
  });

  it('handles missing data gracefully', () => {
    render(<MetadataComparison data={null} />);
    expect(screen.getByText('Metadata Comparison')).toBeInTheDocument();
    // Should show empty state or placeholder
  });

  it('displays all metadata fields', () => {
    render(<MetadataComparison data={mockData} />);
    
    // Check if all metadata fields are present
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Category')).toBeInTheDocument();
    expect(screen.getByText('Rating')).toBeInTheDocument();
    expect(screen.getByText('Reviews')).toBeInTheDocument();
    expect(screen.getByText('Installs')).toBeInTheDocument();
    expect(screen.getByText('Last Updated')).toBeInTheDocument();
  });

  it('formats numbers correctly', () => {
    render(<MetadataComparison data={mockData} />);
    expect(screen.getByText('50,000')).toBeInTheDocument();
    expect(screen.getByText('40,000')).toBeInTheDocument();
  });

  it('formats dates correctly', () => {
    render(<MetadataComparison data={mockData} />);
    // Check if dates are formatted properly
    const date = new Date(1645900800 * 1000).toLocaleDateString();
    expect(screen.getByText(date)).toBeInTheDocument();
  });
});