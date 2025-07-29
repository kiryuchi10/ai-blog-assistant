import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ 
  size = 'medium', 
  color = 'primary', 
  text = null,
  overlay = false,
  className = '' 
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
    xlarge: 'w-16 h-16',
  };

  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    success: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600',
    white: 'text-white',
  };

  const spinnerContent = (
    <div className={`loading-spinner ${className}`}>
      <div className="flex flex-col items-center justify-center space-y-2">
        {/* Spinner */}
        <div className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]}`}>
          <svg
            className="w-full h-full"
            fill="none"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
        
        {/* Loading text */}
        {text && (
          <div className={`text-sm ${colorClasses[color]} animate-pulse`}>
            {text}
          </div>
        )}
      </div>
    </div>
  );

  // Render with overlay if requested
  if (overlay) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 shadow-xl">
          {spinnerContent}
        </div>
      </div>
    );
  }

  return spinnerContent;
};

// Preset spinner components for common use cases
export const PageLoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen">
    <LoadingSpinner size="large" text="Loading..." />
  </div>
);

export const ButtonLoadingSpinner = ({ text = "Loading..." }) => (
  <div className="flex items-center space-x-2">
    <LoadingSpinner size="small" color="white" />
    <span>{text}</span>
  </div>
);

export const InlineLoadingSpinner = ({ text = null }) => (
  <div className="flex items-center space-x-2">
    <LoadingSpinner size="small" />
    {text && <span className="text-sm text-gray-600">{text}</span>}
  </div>
);

export const OverlayLoadingSpinner = ({ text = "Processing..." }) => (
  <LoadingSpinner size="large" text={text} overlay={true} />
);

export default LoadingSpinner;