import React, { useState } from 'react';
import HealthScore from './widgets/HealthScore';
import ActionItems from './widgets/ActionItems';
import CompetitorComparison from './widgets/CompetitorComparison';
import KeywordOpportunities from './widgets/KeywordOpportunities';
import MetadataHealth from './widgets/MetadataHealth';

const Dashboard = () => {
  const [selectedApp, setSelectedApp] = useState('com.badhobuyer');
  
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      {/* Simple App Selector */}
      <div className="mb-6 bg-white rounded-lg shadow p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Your App
        </label>
        <select
          value={selectedApp}
          onChange={(e) => setSelectedApp(e.target.value)}
          className="w-full md:w-64 px-4 py-2 border rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="com.badhobuyer">BadhoBuyer</option>
          <option value="club.kirana">Kirana Club</option>
          <option value="com.udaan.android">Udaan</option>
        </select>
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Health Score - Quick Overview */}
        <div className="md:col-span-2">
          <HealthScore appId={selectedApp} />
        </div>

        {/* Priority Action Items */}
        <div className="md:col-span-2">
          <ActionItems appId={selectedApp} />
        </div>

        {/* Competitor Comparison */}
        <div className="md:col-span-2">
          <CompetitorComparison appId={selectedApp} />
        </div>

        {/* Keyword Opportunities */}
        <div>
          <KeywordOpportunities appId={selectedApp} />
        </div>

        {/* Metadata Health */}
        <div>
          <MetadataHealth appId={selectedApp} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;