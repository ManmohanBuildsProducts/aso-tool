import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import App from '../App';
import * as api from '../services/api';

// Mock API calls
jest.mock('../services/api');

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

describe('App Component', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Mock successful API responses
    api.fetchAppAnalysis.mockResolvedValue({
      health_score: 85,
      metrics: {
        keyword_optimization: 80,
        metadata_quality: 90,
        competitive_position: 85,
        user_engagement: 85
      }
    });
  });

  it('renders without crashing', () => {
    render(<App />, { wrapper });
    expect(screen.getByTestId('app-container')).toBeInTheDocument();
  });

  it('shows loading state while fetching data', () => {
    render(<App />, { wrapper });
    expect(screen.getByTestId('loading-state')).toBeInTheDocument();
  });

  it('displays error state when API fails', async () => {
    api.fetchAppAnalysis.mockRejectedValue(new Error('API Error'));
    
    render(<App />, { wrapper });
    
    await waitFor(() => {
      expect(screen.getByTestId('error-state')).toBeInTheDocument();
    });
  });

  it('allows switching between apps', async () => {
    render(<App />, { wrapper });
    
    const appSelector = screen.getByTestId('app-selector');
    fireEvent.change(appSelector, { target: { value: 'club.kirana' } });
    
    await waitFor(() => {
      expect(api.fetchAppAnalysis).toHaveBeenCalledWith('club.kirana');
    });
  });
});