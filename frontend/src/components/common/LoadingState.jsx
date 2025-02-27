import React from 'react';

const LoadingState = () => {
  return (
    <div className="space-y-6">
      {/* Health Score Skeleton */}
      <div className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
        <div className="flex items-start">
          <div className="w-32 h-32 bg-gray-200 rounded-full"></div>
          <div className="ml-8 flex-1">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="grid grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-gray-100 rounded-lg p-3">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-6 bg-gray-200 rounded w-1/3"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Action Center Skeleton */}
      <div className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LoadingState;