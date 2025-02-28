import axios from 'axios';
import * as api from '../../services/api';

jest.mock('axios');

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchAppAnalysis', () => {
    it('fetches app analysis successfully', async () => {
      const mockData = {
        health_score: 85,
        metrics: {}
      };
      
      axios.get.mockResolvedValue({ data: mockData });
      
      const result = await api.fetchAppAnalysis('test-app');
      expect(result).toEqual(mockData);
      expect(axios.get).toHaveBeenCalledWith('/ai/analyze/test-app');
    });

    it('handles errors appropriately', async () => {
      const error = new Error('API Error');
      axios.get.mockRejectedValue(error);
      
      await expect(api.fetchAppAnalysis('test-app')).rejects.toThrow('API Error');
    });
  });

  describe('implementAction', () => {
    it('implements action successfully', async () => {
      const mockData = { status: 'success' };
      axios.post.mockResolvedValue({ data: mockData });
      
      const result = await api.implementAction({
        appId: 'test-app',
        actionId: '123'
      });
      
      expect(result).toEqual(mockData);
      expect(axios.post).toHaveBeenCalledWith(
        '/actions/123/implement',
        { app_id: 'test-app' }
      );
    });
  });

  describe('fetchKeywordAnalysis', () => {
    it('fetches keyword analysis successfully', async () => {
      const mockData = {
        metrics: {},
        recommendations: []
      };
      
      axios.get.mockResolvedValue({ data: mockData });
      
      const result = await api.fetchKeywordAnalysis('test-keyword');
      expect(result).toEqual(mockData);
      expect(axios.get).toHaveBeenCalledWith('/ai/keywords/test-keyword');
    });
  });

  describe('fetchCompetitorImpact', () => {
    it('fetches competitor impact successfully', async () => {
      const mockData = {
        impact: {},
        recommendations: []
      };
      
      axios.get.mockResolvedValue({ data: mockData });
      
      const result = await api.fetchCompetitorImpact(
        'test-app',
        ['comp1', 'comp2']
      );
      
      expect(result).toEqual(mockData);
      expect(axios.get).toHaveBeenCalledWith(
        '/ai/competitors/impact/test-app',
        {
          params: {
            competitor_ids: ['comp1', 'comp2']
          }
        }
      );
    });
  });
});