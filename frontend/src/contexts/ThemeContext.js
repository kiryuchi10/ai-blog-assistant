import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';

// Initial state
const initialState = {
  theme: 'light', // 'light' | 'dark' | 'system'
  isDark: false,
  primaryColor: '#2563eb',
  fontSize: 'medium', // 'small' | 'medium' | 'large'
  sidebarCollapsed: false,
  animations: true,
};

// Action types
const THEME_ACTIONS = {
  SET_THEME: 'SET_THEME',
  TOGGLE_THEME: 'TOGGLE_THEME',
  SET_PRIMARY_COLOR: 'SET_PRIMARY_COLOR',
  SET_FONT_SIZE: 'SET_FONT_SIZE',
  TOGGLE_SIDEBAR: 'TOGGLE_SIDEBAR',
  SET_ANIMATIONS: 'SET_ANIMATIONS',
  LOAD_PREFERENCES: 'LOAD_PREFERENCES',
};

// Reducer
const themeReducer = (state, action) => {
  switch (action.type) {
    case THEME_ACTIONS.SET_THEME:
      return {
        ...state,
        theme: action.payload,
        isDark: action.payload === 'dark' || 
               (action.payload === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches),
      };

    case THEME_ACTIONS.TOGGLE_THEME:
      const newTheme = state.theme === 'light' ? 'dark' : 'light';
      return {
        ...state,
        theme: newTheme,
        isDark: newTheme === 'dark',
      };

    case THEME_ACTIONS.SET_PRIMARY_COLOR:
      return {
        ...state,
        primaryColor: action.payload,
      };

    case THEME_ACTIONS.SET_FONT_SIZE:
      return {
        ...state,
        fontSize: action.payload,
      };

    case THEME_ACTIONS.TOGGLE_SIDEBAR:
      return {
        ...state,
        sidebarCollapsed: !state.sidebarCollapsed,
      };

    case THEME_ACTIONS.SET_ANIMATIONS:
      return {
        ...state,
        animations: action.payload,
      };

    case THEME_ACTIONS.LOAD_PREFERENCES:
      return {
        ...state,
        ...action.payload,
      };

    default:
      return state;
  }
};

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

// Theme Provider component
export const ThemeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(themeReducer, initialState);

  // Load preferences from localStorage
  const loadPreferences = useCallback(() => {
    try {
      const saved = localStorage.getItem('blog_assistant_theme_preferences');
      if (saved) {
        const preferences = JSON.parse(saved);
        dispatch({
          type: THEME_ACTIONS.LOAD_PREFERENCES,
          payload: preferences,
        });
      }
    } catch (error) {
      console.error('Failed to load theme preferences:', error);
    }
  }, []);

  // Save preferences to localStorage
  const savePreferences = useCallback(() => {
    try {
      localStorage.setItem('blog_assistant_theme_preferences', JSON.stringify(state));
    } catch (error) {
      console.error('Failed to save theme preferences:', error);
    }
  }, [state]);

  // Apply theme to document
  const applyTheme = useCallback(() => {
    const root = document.documentElement;
    
    // Apply theme class
    root.className = root.className.replace(/theme-\w+/g, '');
    root.classList.add(`theme-${state.isDark ? 'dark' : 'light'}`);
    
    // Apply primary color
    root.style.setProperty('--primary-color', state.primaryColor);
    
    // Apply font size
    const fontSizes = {
      small: '14px',
      medium: '16px',
      large: '18px',
    };
    root.style.setProperty('--base-font-size', fontSizes[state.fontSize]);
    
    // Apply animations
    root.style.setProperty('--animation-duration', state.animations ? '0.3s' : '0s');
    
    // Apply sidebar state
    root.classList.toggle('sidebar-collapsed', state.sidebarCollapsed);
  }, [state.isDark, state.primaryColor, state.fontSize, state.animations, state.sidebarCollapsed]);

  // Load preferences from localStorage on mount
  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  // Save preferences to localStorage whenever state changes
  useEffect(() => {
    savePreferences();
  }, [savePreferences]);

  // Apply theme to document
  useEffect(() => {
    applyTheme();
  }, [applyTheme]);

  // Listen for system theme changes
  useEffect(() => {
    if (state.theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e) => {
        dispatch({
          type: THEME_ACTIONS.SET_THEME,
          payload: 'system',
        });
      };

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [state.theme]);

  // Set theme
  const setTheme = (theme) => {
    dispatch({
      type: THEME_ACTIONS.SET_THEME,
      payload: theme,
    });
  };

  // Toggle theme
  const toggleTheme = () => {
    dispatch({ type: THEME_ACTIONS.TOGGLE_THEME });
  };

  // Set primary color
  const setPrimaryColor = (color) => {
    dispatch({
      type: THEME_ACTIONS.SET_PRIMARY_COLOR,
      payload: color,
    });
  };

  // Set font size
  const setFontSize = (size) => {
    dispatch({
      type: THEME_ACTIONS.SET_FONT_SIZE,
      payload: size,
    });
  };

  // Toggle sidebar
  const toggleSidebar = () => {
    dispatch({ type: THEME_ACTIONS.TOGGLE_SIDEBAR });
  };

  // Set animations
  const setAnimations = (enabled) => {
    dispatch({
      type: THEME_ACTIONS.SET_ANIMATIONS,
      payload: enabled,
    });
  };

  // Get CSS custom properties
  const getCSSVariables = () => {
    return {
      '--primary-color': state.primaryColor,
      '--base-font-size': {
        small: '14px',
        medium: '16px',
        large: '18px',
      }[state.fontSize],
      '--animation-duration': state.animations ? '0.3s' : '0s',
    };
  };

  // Context value
  const value = {
    // State
    theme: state.theme,
    isDark: state.isDark,
    primaryColor: state.primaryColor,
    fontSize: state.fontSize,
    sidebarCollapsed: state.sidebarCollapsed,
    animations: state.animations,
    
    // Actions
    setTheme,
    toggleTheme,
    setPrimaryColor,
    setFontSize,
    toggleSidebar,
    setAnimations,
    
    // Utilities
    getCSSVariables,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};