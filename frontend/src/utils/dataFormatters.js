// Format large numbers with commas
export const formatNumber = (num) => {
  if (!num) return 'N/A';
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

// Format date from timestamp
export const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  return new Date(timestamp * 1000).toLocaleDateString();
};

// Format rating to one decimal place
export const formatRating = (rating) => {
  if (!rating) return 'N/A';
  return Number(rating).toFixed(1);
};

// Format percentage
export const formatPercentage = (value, decimals = 1) => {
  if (!value && value !== 0) return 'N/A';
  return `${(value * 100).toFixed(decimals)}%`;
};

// Safe object access with default value
export const safeGet = (obj, path, defaultValue = 'N/A') => {
  try {
    const value = path.split('.').reduce((acc, part) => acc && acc[part], obj);
    return value === null || value === undefined ? defaultValue : value;
  } catch (e) {
    return defaultValue;
  }
};

// Validate app data structure
export const validateAppData = (data) => {
  if (!data) return false;
  const requiredFields = ['title', 'appId', 'score', 'reviews', 'installs'];
  return requiredFields.every(field => data.hasOwnProperty(field));
};

// Format install range
export const formatInstallRange = (installs) => {
  if (!installs) return 'N/A';
  return installs.replace(/[+]/g, '+ downloads');
};

// Calculate percentage change
export const calculatePercentageChange = (current, previous) => {
  if (!current || !previous) return null;
  return ((current - previous) / previous) * 100;
};

// Format market position
export const getMarketPosition = (metrics) => {
  if (!metrics?.rating_percentile) return 'Unknown';
  const percentile = metrics.rating_percentile;
  if (percentile > 75) return 'Market Leader';
  if (percentile > 50) return 'Strong Competitor';
  if (percentile > 25) return 'Growing';
  return 'Emerging';
};