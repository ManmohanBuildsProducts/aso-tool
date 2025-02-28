import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import ActionCenter from '../../components/widgets/ActionCenter';
import * as api from '../../services/api';

jest.mock('../../services/api');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false }
  }
});

const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('ActionCenter Component', () => {
  const mockActions = [
    {
      id: '1',
      title: 'Optimize Title',
      description: 'Add keywords to title',
      priority: 'high',
      effort: 'low',
      status: 'pending',
      steps: [
        { action: 'Review current title', status: 'done' },
        { action: 'Add keywords', status: 'pending' }
      ]
    },
    {
      id: '2',
      title: 'Update Screenshots',
      description: 'Add new screenshots',
      priority: 'medium',
      effort: 'medium',
      status: 'pending',
      steps: [
        { action: 'Create screenshots', status: 'pending' }
      ]
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    api.implementAction.mockResolvedValue({ status: 'success' });
  });

  it('renders all actions', () => {
    render(
      <ActionCenter actions={mockActions} appId="test-app" />,
      { wrapper }
    );
    
    expect(screen.getByText('Optimize Title')).toBeInTheDocument();
    expect(screen.getByText('Update Screenshots')).toBeInTheDocument();
  });

  it('filters actions correctly', () => {
    render(
      <ActionCenter actions={mockActions} appId="test-app" />,
      { wrapper }
    );
    
    const filter = screen.getByTestId('action-filter');
    fireEvent.change(filter, { target: { value: 'quick' } });
    
    expect(screen.getByText('Optimize Title')).toBeInTheDocument();
    expect(screen.queryByText('Update Screenshots')).not.toBeInTheDocument();
  });

  it('implements actions successfully', async () => {
    render(
      <ActionCenter actions={mockActions} appId="test-app" />,
      { wrapper }
    );
    
    const implementButton = screen.getAllByText('Implement')[0];
    fireEvent.click(implementButton);
    
    await waitFor(() => {
      expect(api.implementAction).toHaveBeenCalledWith({
        appId: 'test-app',
        actionId: '1'
      });
    });
  });

  it('shows error when action implementation fails', async () => {
    api.implementAction.mockRejectedValue(new Error('Implementation failed'));
    
    render(
      <ActionCenter actions={mockActions} appId="test-app" />,
      { wrapper }
    );
    
    const implementButton = screen.getAllByText('Implement')[0];
    fireEvent.click(implementButton);
    
    await waitFor(() => {
      expect(screen.getByText('Implementation failed')).toBeInTheDocument();
    });
  });
});