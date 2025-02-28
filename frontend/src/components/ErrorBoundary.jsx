import React from 'react';
import { HiExclamationCircle } from 'react-icons/hi';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-50 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <HiExclamationCircle className="w-6 h-6 text-red-500 mr-2" />
            <h3 className="text-lg font-medium text-red-800">
              Something went wrong
            </h3>
          </div>
          <div className="text-sm text-red-700">
            {this.state.error?.message || 'An unexpected error occurred'}
          </div>
          {this.props.showReset && (
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
            >
              Reload Page
            </button>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}