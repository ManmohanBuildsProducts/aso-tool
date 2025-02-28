import axios from 'axios';
import toast from 'react-hot-toast';

const baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: `${baseURL}/api`,  // Always add /api prefix
  timeout: 60000,  // 60 seconds for AI operations
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

export const fetchAppAnalysis = async (appId, metadata) => {
  try {
    const response = await api.post(`/analyze/app/${appId}`, metadata);
    return response.data;
  } catch (error) {
    console.error('Error fetching app analysis:', error);
    throw error;
  }
};

export const fetchKeywordAnalysis = async (keyword, industry = "B2B wholesale") => {
  try {
    const response = await api.post(`/analyze/keywords`, {
      base_keyword: keyword,
      industry: industry
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching keyword analysis:', error);
    throw error;
  }
};

export const fetchCompetitorAnalysis = async (appMetadata, competitorMetadata) => {
  try {
    const response = await api.post(`/analyze/competitors`, {
      app_metadata: appMetadata,
      competitor_metadata: competitorMetadata
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching competitor analysis:', error);
    throw error;
  }
};

export const optimizeMetadata = async (metadata, keywords) => {
  try {
    const response = await api.post(`/optimize/description`, {
      current_description: metadata.description,
      keywords: keywords
    });
    return response.data;
  } catch (error) {
    console.error('Error optimizing metadata:', error);
    throw error;
  }
};

export const fetchMarketTrends = async (category = "B2B wholesale") => {
  try {
    const response = await api.post(`/analyze/trends`, {
      category: category
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching market trends:', error);
    throw error;
  }
};

// Utility function to format app metadata
export const formatAppMetadata = (appData) => {
  return {
    title: appData.title || "",
    description: appData.description || "",
    category: appData.category || "Business",
    keywords: appData.keywords || [],
    package_name: appData.package_name || "",
    ratings: appData.ratings || {
      average: 0,
      count: 0
    },
    installs: appData.installs || "0+"
  };
};