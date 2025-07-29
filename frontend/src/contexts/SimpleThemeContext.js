import React, { createContext, useContext, useState } from 'react';

// Create context
const ThemeContext = createContext();

// Custom hook to use theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Simple Theme Provider component
export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(false);
  const [primaryColor, setPrimaryColor] = useState('#2563eb');
  const [fontSize, setFontSize] = useState('medium');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [animations, setAnimations] = useState(true);

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  // Context value
  const value = {
    // State
    theme: isDark ? 'dark' : 'light',
    isDark,
    primaryColor,
    fontSize,
    sidebarCollapsed,
    animations,
    
    // Actions
    setTheme: (theme) => setIsDark(theme === 'dark'),
    toggleTheme,
    setPrimaryColor,
    setFontSize,
    toggleSidebar,
    setAnimations,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};