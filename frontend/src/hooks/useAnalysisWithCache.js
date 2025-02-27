import { useCallback, useState } from 'react';
import { useCache, setCached } from './useCache';

const CACHE_KEYS = {
  app: (appId) => `app_analysis_${appId}`,
  competitors: (appId, competitorIds) => 
    `competitor_analysis_${appId}_${competitorIds.sort().join('_')}`,
  keywords: (appId, competitorIds) =>
    `keyword_analysis_${appId}_${competitorIds.sort().join('_')}`,
};

const CACHE_TTL = {
  app: 1000 * 60 * 30, // 30 minutes
  competitors: 1000 * 60 * 60, // 1 hour
  keywords: 1000 * 60 * 60 * 2, // 2 hours
};

export const useAnalysisWithCache = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState({ current: 0, total: 0 });

  const updateProgress = (current, total) => {
    setProgress({ current, total });
  };

  const fetchAppAnalysis = async (appId) => {
    const response = await fetch(`/api/analyze/app/${appId}`);
    if (!response.ok) {
      throw new Error(`App analysis failed: ${response.statusText}`);
    }
    return response.json();
  };

  const fetchCompetitorAnalysis = async (appId, competitorIds) => {
    const response = await fetch('/api/analyze/competitors/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_id: appId, competitor_ids: competitorIds }),
    });
    if (!response.ok) {
      throw new Error(`Competitor analysis failed: ${response.statusText}`);
    }
    return response.json();
  };

  const fetchKeywordAnalysis = async (appId, competitorIds) => {
    const response = await fetch('/api/analyze/keywords/discover', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_id: appId, competitor_ids: competitorIds }),
    });
    if (!response.ok) {
      throw new Error(`Keyword analysis failed: ${response.statusText}`);
    }
    return response.json();
  };

  const analyzeApp = useCallback(async (mainApp, competitors, options = {}) => {
    const { forceFresh = false } = options;
    const competitorIds = competitors.map(comp => comp.appId);
    
    try {
      setLoading(true);
      setError(null);
      setProgress({ current: 0, total: 3 });

      // 1. App Analysis
      let appAnalysis;
      const appCacheKey = CACHE_KEYS.app(mainApp.appId);
      
      if (!forceFresh) {
        appAnalysis = getCached(appCacheKey);
      }
      
      if (!appAnalysis) {
        appAnalysis = await fetchAppAnalysis(mainApp.appId);
        setCached(appCacheKey, appAnalysis, CACHE_TTL.app);
      }
      
      updateProgress(1, 3);

      // 2. Competitor Analysis
      let competitorAnalysis;
      if (competitors.length > 0) {
        const competitorCacheKey = CACHE_KEYS.competitors(mainApp.appId, competitorIds);
        
        if (!forceFresh) {
          competitorAnalysis = getCached(competitorCacheKey);
        }
        
        if (!competitorAnalysis) {
          competitorAnalysis = await fetchCompetitorAnalysis(mainApp.appId, competitorIds);
          setCached(competitorCacheKey, competitorAnalysis, CACHE_TTL.competitors);
        }
      }
      
      updateProgress(2, 3);

      // 3. Keyword Analysis
      const keywordCacheKey = CACHE_KEYS.keywords(mainApp.appId, competitorIds);
      let keywordAnalysis;
      
      if (!forceFresh) {
        keywordAnalysis = getCached(keywordCacheKey);
      }
      
      if (!keywordAnalysis) {
        keywordAnalysis = await fetchKeywordAnalysis(mainApp.appId, competitorIds);
        setCached(keywordCacheKey, keywordAnalysis, CACHE_TTL.keywords);
      }
      
      updateProgress(3, 3);

      return {
        appAnalysis,
        competitorAnalysis,
        keywordAnalysis,
      };
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
      setProgress({ current: 0, total: 0 });
    }
  }, []);

  return {
    analyzeApp,
    loading,
    error,
    progress,
  };
};

export default useAnalysisWithCache;