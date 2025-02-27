import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:55240'
});

export const fetchAppAnalysis = async (appId) => {
  const response = await api.get(`/ai/analyze/${appId}`);
  return response.data;
};

export const implementAction = async ({ appId, actionId }) => {
  const response = await api.post(`/actions/${actionId}/implement`, {
    app_id: appId
  });
  return response.data;
};

export const fetchKeywordAnalysis = async (keyword) => {
  const response = await api.get(`/ai/keywords/${keyword}`);
  return response.data;
};

export const fetchCompetitorImpact = async (appId, competitorIds) => {
  const response = await api.get(`/ai/competitors/impact/${appId}`, {
    params: { competitor_ids: competitorIds }
  });
  return response.data;
};

export const optimizeMetadata = async (appId, metadata) => {
  const response = await api.post(`/ai/metadata/optimize/${appId}`, metadata);
  return response.data;
};

export const fetchRankingHistory = async (appId, days = 30) => {
  const response = await api.get(`/rankings/history/${appId}`, {
    params: { days }
  });
  return response.data;
};