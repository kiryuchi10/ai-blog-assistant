import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';

// Context Providers
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Components
import Layout from './components/layout/Layout';

// Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ContentGenerationPage from './pages/ContentGenerationPage';
import ContentLibraryPage from './pages/ContentLibraryPage';
import TemplatesPage from './pages/TemplatesPage';
import SchedulingPage from './pages/SchedulingPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import ProfilePage from './pages/ProfilePage';

// Styles
import './App.css';

// Create a client for React Query
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
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <div className="App">
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                
                {/* Protected Routes - Demo Mode */}
                <Route path="/" element={
                  <Layout>
                    <DashboardPage />
                  </Layout>
                } />
                
                <Route path="/generate" element={
                  <Layout>
                    <ContentGenerationPage />
                  </Layout>
                } />
                
                <Route path="/library" element={
                  <Layout>
                    <ContentLibraryPage />
                  </Layout>
                } />
                
                <Route path="/templates" element={
                  <Layout>
                    <TemplatesPage />
                  </Layout>
                } />
                
                <Route path="/scheduling" element={
                  <Layout>
                    <SchedulingPage />
                  </Layout>
                } />
                
                <Route path="/analytics" element={
                  <Layout>
                    <AnalyticsPage />
                  </Layout>
                } />
                
                <Route path="/settings" element={
                  <Layout>
                    <SettingsPage />
                  </Layout>
                } />
                
                <Route path="/profile" element={
                  <Layout>
                    <ProfilePage />
                  </Layout>
                } />
                
                {/* Catch all route */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
              
              {/* Global Toast Notifications */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: 'var(--bg-secondary)',
                    color: 'var(--text-primary)',
                    border: '1px solid var(--border-color)',
                  },
                  success: {
                    iconTheme: {
                      primary: 'var(--success-color)',
                      secondary: 'var(--bg-primary)',
                    },
                  },
                  error: {
                    iconTheme: {
                      primary: 'var(--error-color)',
                      secondary: 'var(--bg-primary)',
                    },
                  },
                }}
              />
            </div>
          </Router>
        </AuthProvider>
      </ThemeProvider>
      
      {/* React Query DevTools (only in development) */}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}

export default App;