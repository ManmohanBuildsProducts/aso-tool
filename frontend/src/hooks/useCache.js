import { useState, useEffect } from 'react';

const CACHE_VERSION = '1.0';
const DEFAULT_TTL = 1000 * 60 * 5; // 5 minutes

class CacheManager {
  constructor() {
    this.cache = new Map();
    this.init();
  }

  init() {
    // Load cached data from localStorage
    try {
      const savedCache = localStorage.getItem('app_cache');
      if (savedCache) {
        const { version, data } = JSON.parse(savedCache);
        if (version === CACHE_VERSION) {
          // Convert stored timestamps back to Date objects
          Object.entries(data).forEach(([key, value]) => {
            if (value.timestamp) {
              this.cache.set(key, {
                ...value,
                timestamp: new Date(value.timestamp),
              });
            }
          });
        }
      }
    } catch (error) {
      console.warn('Failed to load cache from localStorage:', error);
    }
  }

  save() {
    try {
      const cacheData = {};
      this.cache.forEach((value, key) => {
        cacheData[key] = value;
      });

      localStorage.setItem('app_cache', JSON.stringify({
        version: CACHE_VERSION,
        data: cacheData,
      }));
    } catch (error) {
      console.warn('Failed to save cache to localStorage:', error);
    }
  }

  get(key) {
    const cached = this.cache.get(key);
    if (!cached) return null;

    // Check if cached data is still valid
    if (cached.ttl && Date.now() - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      this.save();
      return null;
    }

    return cached.data;
  }

  set(key, data, ttl = DEFAULT_TTL) {
    this.cache.set(key, {
      data,
      timestamp: new Date(),
      ttl,
    });
    this.save();
  }

  invalidate(key) {
    this.cache.delete(key);
    this.save();
  }

  clear() {
    this.cache.clear();
    localStorage.removeItem('app_cache');
  }
}

const cacheManager = new CacheManager();

export const useCache = (key, fetchFn, options = {}) => {
  const {
    ttl = DEFAULT_TTL,
    enabled = true,
    deps = [],
    onSuccess,
    onError,
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async (force = false) => {
    if (!enabled) return;

    try {
      setLoading(true);
      setError(null);

      // Check cache first if not forcing refresh
      if (!force) {
        const cached = cacheManager.get(key);
        if (cached) {
          setData(cached);
          onSuccess?.(cached);
          return;
        }
      }

      // Fetch fresh data
      const result = await fetchFn();
      
      // Cache the result
      cacheManager.set(key, result, ttl);
      
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      setError(err);
      onError?.(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [key, enabled, ...deps]);

  const refresh = () => fetchData(true);
  const invalidate = () => cacheManager.invalidate(key);

  return {
    data,
    loading,
    error,
    refresh,
    invalidate,
  };
};

export const clearCache = () => cacheManager.clear();
export const getCached = (key) => cacheManager.get(key);
export const setCached = (key, data, ttl) => cacheManager.set(key, data, ttl);