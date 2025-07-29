import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

const DashboardPage = () => {
  const { isDark } = useTheme();
  const { user } = useAuth();

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Welcome back, {user?.name || 'User'}!
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className={`p-6 rounded-lg shadow ${isDark ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className="text-lg font-semibold mb-2">Content Generation</h3>
            <p className={`${isDark ? 'text-gray-400' : 'text-gray-600'} mb-4`}>
              Create AI-powered blog content
            </p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
              Start Writing
            </button>
          </div>

          <div className={`p-6 rounded-lg shadow ${isDark ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className="text-lg font-semibold mb-2">Content Library</h3>
            <p className={`${isDark ? 'text-gray-400' : 'text-gray-600'} mb-4`}>
              Manage your blog posts
            </p>
            <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors">
              View Library
            </button>
          </div>

          <div className={`p-6 rounded-lg shadow ${isDark ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className="text-lg font-semibold mb-2">Analytics</h3>
            <p className={`${isDark ? 'text-gray-400' : 'text-gray-600'} mb-4`}>
              Track your performance
            </p>
            <button className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-colors">
              View Analytics
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;