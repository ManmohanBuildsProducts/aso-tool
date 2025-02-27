import React from 'react';
import { render, screen } from '@testing-library/react';
import HealthScore from '../../components/widgets/HealthScore';

describe('HealthScore Component', () => {
  const mockProps = {
    score: 85,
    metrics: {
      keyword_optimization: 80,
      metadata_quality: 90,
      competitive_position: 85,
      user_engagement: 85
    }
  };

  it('renders score correctly', () => {
    render(<HealthScore {...mockProps} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('shows all metrics', () => {
    render(<HealthScore {...mockProps} />);
    
    expect(screen.getByText('keyword optimization')).toBeInTheDocument();
    expect(screen.getByText('metadata quality')).toBeInTheDocument();
    expect(screen.getByText('competitive position')).toBeInTheDocument();
    expect(screen.getByText('user engagement')).toBeInTheDocument();
  });

  it('handles missing metrics gracefully', () => {
    render(<HealthScore score={85} metrics={{}} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('shows appropriate color based on score', () => {
    const { rerender } = render(<HealthScore score={85} metrics={{}} />);
    expect(screen.getByTestId('score-indicator')).toHaveClass('text-green-500');

    rerender(<HealthScore score={65} metrics={{}} />);
    expect(screen.getByTestId('score-indicator')).toHaveClass('text-yellow-500');

    rerender(<HealthScore score={35} metrics={{}} />);
    expect(screen.getByTestId('score-indicator')).toHaveClass('text-red-500');
  });
});