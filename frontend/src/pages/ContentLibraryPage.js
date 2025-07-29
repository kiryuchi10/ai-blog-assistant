import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

const ContentLibraryPage = () => {
  const { isDark } = useTheme();

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Content Library</h1>
        <div className={`p-6 rounded-lg shadow ${isDark ? 'bg-gray-800' : 'bg-white'}`}>
          <p>Your content library will appear here...</p>
        </div>
      </div>
    </div>
  );
};

export default ContentLibraryPage;