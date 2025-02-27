import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from './components/Dashboard';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import { Toaster } from 'react-hot-toast';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5 * 60 * 1000,
      cacheTime: 30 * 60 * 1000,
      onError: (error) => {
        console.error('Query error:', error);
      }
    },
    mutations: {
      retry: 1,
      onError: (error) => {
        console.error('Mutation error:', error);
      }
    }
  }
});

function App() {
  const [selectedApp, setSelectedApp] = useState('com.badhobuyer');

  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <div className="min-h-screen bg-gray-50" data-testid="app-container">
          <Navbar 
            selectedApp={selectedApp} 
            onAppChange={setSelectedApp}
            data-testid="navbar"
          />
          <main className="container mx-auto px-4 py-8">
            <Dashboard 
              appId={selectedApp}
              data-testid="dashboard"
            />
          </main>
          <Toaster position="top-right" />
        </div>
      </ErrorBoundary>
    </QueryClientProvider>
  );
}

export default App;