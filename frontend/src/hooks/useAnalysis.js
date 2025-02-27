import { useState, useCallback } from 'react';

const useAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const analyzeApp = useCallback(async (mainApp, competitors) => {
    setLoading(true);
    setError(null);

    try {
      // Get main app analysis
      const appResponse = await fetch(`/api/analyze/app/${mainApp.appId}`);
      if (!appResponse.ok) {
        throw new Error(`App analysis failed: ${appResponse.statusText}`);
      }
      const appData = await appResponse.json();

      // Get competitor analysis if there are competitors
      let competitorData = null;
      if (competitors.length > 0) {
        const competitorResponse = await fetch('/api/analyze/competitors/compare', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            app_id: mainApp.appId,
            competitor_ids: competitors.map(comp => comp.appId),
          }),
        });
        if (!competitorResponse.ok) {
          throw new Error(`Competitor analysis failed: ${competitorResponse.statusText}`);
        }
        competitorData = await competitorResponse.json();
      }

      // Get keyword analysis
      const keywordResponse = await fetch('/api/analyze/keywords/discover', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          app_id: mainApp.appId,
          competitor_ids: competitors.map(comp => comp.appId),
        }),
      });
      if (!keywordResponse.ok) {
        throw new Error(`Keyword analysis failed: ${keywordResponse.statusText}`);
      }
      const keywordData = await keywordResponse.json();

      setData({
        appAnalysis: appData,
        competitorAnalysis: competitorData,
        keywordAnalysis: keywordData,
      });
    } catch (error) {
      setError(error.message);
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    loading,
    error,
    data,
    analyzeApp,
    reset,
  };
};

export default useAnalysis;