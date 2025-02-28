import axios from 'axios';
import toast from 'react-hot-toast';

const api = axios.create({
  baseURL: 'http://localhost:55240',  // Using the correct port
  timeout: 30000,  // 30 seconds
  headers: {
    'Content-Type': 'application/json'
  },
  // Add error handling
  validateStatus: function (status) {
    return status >= 200 && status < 500;  // Don't reject if status is 404
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any request processing here
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Handle empty responses
    if (!response.data) {
      return {
        data: {
          analysis: {},
          format: "json"
        }
      };
    }
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    const message = error.response?.data?.detail || 
                   error.message || 
                   'An error occurred';
                   
    // Show error toast only for non-404 errors
    if (error.response?.status !== 404) {
      toast.error(message);
    }
    
    // Return empty analysis for 404s
    if (error.response?.status === 404) {
      return {
        data: {
          analysis: {},
          format: "json"
        }
      };
    }
    
    return Promise.reject(error);
  }
);

export const fetchAppAnalysis = async (appId) => {
  try {
    const response = await api.get(`/ai/analyze/${appId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching app analysis:', error);
    throw error;
  }
};

export const implementAction = async ({ appId, actionId }) => {
  try {
    const response = await api.post(`/actions/${actionId}/implement`, {
      app_id: appId
    });
    return response.data;
  } catch (error) {
    console.error('Error implementing action:', error);
    throw error;
  }
};

export const fetchKeywordAnalysis = async (keyword) => {
  try {
    const response = await api.get(`/ai/keywords/${keyword}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching keyword analysis:', error);
    throw error;
  }
};

export const fetchCompetitorImpact = async (appId, competitorIds) => {
  try {
    const response = await api.get(`/ai/competitors/impact/${appId}`, {
      params: { competitor_ids: competitorIds }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching competitor impact:', error);
    throw error;
  }
};

export const optimizeMetadata = async (appId, metadata) => {
  try {
    const response = await api.post(`/ai/metadata/optimize/${appId}`, metadata);
    return response.data;
  } catch (error) {
    console.error('Error optimizing metadata:', error);
    throw error;
  }
};

export const fetchRankingHistory = async (appId, days = 30) => {
  try {
    const response = await api.get(`/rankings/history/${appId}`, {
      params: { days }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching ranking history:', error);
    throw error;
  }
};