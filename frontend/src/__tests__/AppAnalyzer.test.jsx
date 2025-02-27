import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AppAnalyzer from '../components/AppAnalyzer';

// Mock the fetch function
global.fetch = jest.fn();

describe('AppAnalyzer Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders without crashing', () => {
    render(<AppAnalyzer />);
    expect(screen.getByText('ASO Analysis Tool')).toBeInTheDocument();
  });

  it('handles main app URL input', () => {
    render(<AppAnalyzer />);
    const input = screen.getByLabelText('Play Store URL');
    
    fireEvent.change(input, {
      target: { value: 'https://play.google.com/store/apps/details?id=com.test.app' }
    });
    
    expect(input.value).toBe('https://play.google.com/store/apps/details?id=com.test.app');
    expect(screen.getByText('App ID: com.test.app')).toBeInTheDocument();
  });

  it('handles adding competitors', async () => {
    render(<AppAnalyzer />);
    const input = screen.getByLabelText('Add Competitor URL');
    const addButton = screen.getByText('Add Competitor');
    
    fireEvent.change(input, {
      target: { value: 'https://play.google.com/store/apps/details?id=com.competitor.app' }
    });
    
    fireEvent.click(addButton);
    
    await waitFor(() => {
      expect(screen.getByText('com.competitor.app')).toBeInTheDocument();
    });
  });

  it('handles competitor deletion', async () => {
    render(<AppAnalyzer />);
    
    // Add a competitor first
    const input = screen.getByLabelText('Add Competitor URL');
    const addButton = screen.getByText('Add Competitor');
    
    fireEvent.change(input, {
      target: { value: 'https://play.google.com/store/apps/details?id=com.competitor.app' }
    });
    
    fireEvent.click(addButton);
    
    // Find and click delete button
    const deleteButton = screen.getByLabelText('Delete');
    fireEvent.click(deleteButton);
    
    await waitFor(() => {
      expect(screen.queryByText('com.competitor.app')).not.toBeInTheDocument();
    });
  });

  it('handles analysis request', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          status: 'success',
          analysis: {
            // Mock analysis data
          }
        })
      })
    );

    render(<AppAnalyzer />);
    
    // Add main app
    const mainAppInput = screen.getByLabelText('Play Store URL');
    fireEvent.change(mainAppInput, {
      target: { value: 'https://play.google.com/store/apps/details?id=com.test.app' }
    });
    
    // Click analyze button
    const analyzeButton = screen.getByText('Analyze');
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
  });

  it('displays error message on failed analysis', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('Analysis failed'))
    );

    render(<AppAnalyzer />);
    
    // Add main app
    const mainAppInput = screen.getByLabelText('Play Store URL');
    fireEvent.change(mainAppInput, {
      target: { value: 'https://play.google.com/store/apps/details?id=com.test.app' }
    });
    
    // Click analyze button
    const analyzeButton = screen.getByText('Analyze');
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('handles tab switching', () => {
    render(<AppAnalyzer />);
    
    const overviewTab = screen.getByText('Overview');
    const keywordsTab = screen.getByText('Keywords');
    const reviewsTab = screen.getByText('Reviews');
    
    fireEvent.click(keywordsTab);
    expect(screen.getByText('Keyword Analysis')).toBeInTheDocument();
    
    fireEvent.click(reviewsTab);
    expect(screen.getByText('Review Analysis')).toBeInTheDocument();
    
    fireEvent.click(overviewTab);
    expect(screen.getByText('Comparison Summary')).toBeInTheDocument();
  });
});