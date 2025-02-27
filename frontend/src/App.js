import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from './components/Dashboard';
import Navbar from './components/Navbar';
import { Toaster } from 'react-hot-toast';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const [selectedApp, setSelectedApp] = useState('com.badhobuyer');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <Navbar selectedApp={selectedApp} onAppChange={setSelectedApp} />
        <main className="container mx-auto px-4 py-8">
          <Dashboard appId={selectedApp} />
        </main>
        <Toaster position="top-right" />
      </div>
    </QueryClientProvider>
  );
}

export default App;