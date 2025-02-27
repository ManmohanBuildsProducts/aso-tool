import React from 'react';
import { HiExclamationCircle } from 'react-icons/hi';

const ErrorState = ({ error }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] bg-white rounded-xl shadow-lg p-6">
      <HiExclamationCircle className="w-16 h-16 text-red-500 mb-4" />
      <h2 className="text-xl font-bold text-gray-900 mb-2">
        Something went wrong
      </h2>
      <p className="text-gray-600 text-center max-w-md mb-6">
        {error?.message || 'An error occurred while loading the dashboard. Please try again later.'}
      </p>
      <button
        onClick={() => window.location.reload()}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Refresh Page
      </button>
    </div>
  );
};

export default ErrorState;