import React from 'react';

const LoadingState = ({ message = 'Loading...' }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6"></div>
        </div>
        <div className="text-sm text-gray-500 text-center mt-4">
          {message}
        </div>
      </div>
    </div>
  );
};

export default LoadingState;