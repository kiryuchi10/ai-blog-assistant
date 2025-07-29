import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

const ProfilePage = () => {
  const { isDark } = useTheme();
  const { user } = useAuth();

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Profile</h1>
        <div className={`p-6 rounded-lg shadow ${isDark ? 'bg-gray-800' : 'bg-white'}`}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Name</label>
            <p className={`${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {user?.name || 'Not set'}
            </p>
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Email</label>
            <p className={`${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {user?.email || 'Not set'}
            </p>
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
            Edit Profile
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;