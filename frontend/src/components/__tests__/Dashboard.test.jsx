import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from '../Dashboard';
import { fetchAppAnalysis, fetchKeywordAnalysis, fetchCompetitorAnalysis } from '../../services/api';

// Mock API calls
jest.mock('../../services/api');

// Mock child components
jest.mock('../dashboard/ASOScoreCard', () => {
  return function DummyASOScoreCard({ data }) {
    return <div data-testid="aso-score-card">ASO Score: {data?.analysis?.title_analysis?.current_score}</div>;
  };
});

jest.mock('../dashboard/KeywordTable', () => {
  return function DummyKeywordTable({ data }) {
    return <div data-testid="keyword-table">Keywords: {data?.analysis?.variations?.length}</div>;
  };
});

jest.mock('../dashboard/CompetitorAnalysis', () => {
  return function DummyCompetitorAnalysis({ data }) {
    return <div data-testid="competitor-analysis">Competitors: {data?.competitors?.length}</div>;
  };
});

describe('Dashboard', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false
      }
    }
  });

  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Mock successful API responses
    fetchAppAnalysis.mockResolvedValue({
      analysis: {
        title_analysis: { current_score: 85 }
      }
    });

    fetchKeywordAnalysis.mockResolvedValue({
      analysis: {
        variations: ['keyword1', 'keyword2']
      }
    });

    fetchCompetitorAnalysis.mockResolvedValue({
      competitors: ['comp1', 'comp2']
    });
  });

  it('renders loading state initially', () => {
    render(<Dashboard appId="test-app" />, { wrapper });
    expect(screen.getByText('Analyzing app data...')).toBeInTheDocument();
  });

  it('renders all components when data is loaded', async () => {
    render(<Dashboard appId="test-app" />, { wrapper });

    await waitFor(() => {
      expect(screen.getByTestId('aso-score-card')).toBeInTheDocument();
      expect(screen.getByTestId('keyword-table')).toBeInTheDocument();
      expect(screen.getByTestId('competitor-analysis')).toBeInTheDocument();
    });
  });

  it('shows error state when API fails', async () => {
    fetchAppAnalysis.mockRejectedValue(new Error('API Error'));

    render(<Dashboard appId="test-app" />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('refetches data when appId changes', async () => {
    const { rerender } = render(<Dashboard appId="test-app" />, { wrapper });

    await waitFor(() => {
      expect(fetchAppAnalysis).toHaveBeenCalledWith('test-app');
    });

    rerender(<Dashboard appId="new-app" />, { wrapper });

    await waitFor(() => {
      expect(fetchAppAnalysis).toHaveBeenCalledWith('new-app');
    });
  });

  it('caches data for 5 minutes', async () => {
    render(<Dashboard appId="test-app" />, { wrapper });

    await waitFor(() => {
      expect(fetchAppAnalysis).toHaveBeenCalledTimes(1);
    });

    // Rerender shouldn't trigger new fetch due to caching
    const { rerender } = render(<Dashboard appId="test-app" />, { wrapper });
    rerender(<Dashboard appId="test-app" />, { wrapper });

    expect(fetchAppAnalysis).toHaveBeenCalledTimes(1);
  });
});