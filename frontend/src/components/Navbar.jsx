import React from 'react';
import { HiChartBar, HiCog } from 'react-icons/hi';

const Navbar = ({ selectedApp, onAppChange }) => {
  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <HiChartBar className="w-8 h-8 text-blue-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">
              ASO Tool
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <select
              value={selectedApp}
              onChange={(e) => onAppChange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="com.badhobuyer">BadhoBuyer</option>
              <option value="club.kirana">Kirana Club</option>
              <option value="com.udaan.android">Udaan</option>
            </select>

            <button className="p-2 text-gray-500 hover:text-gray-700">
              <HiCog className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;