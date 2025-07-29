import { apiClient } from './apiClient';

class AuthService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';
  }

  // Login user
  async login(credentials) {
    try {
      const response = await apiClient.post('/auth/login', credentials);
      
      if (response.data.access_token) {
        // Store token in localStorage
        localStorage.setItem('token', response.data.access_token);
        
        // Set default authorization header
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      }
      
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Register user
  async register(userData) {
    try {
      const response = await apiClient.post('/auth/register', userData);
      
      if (response.data.access_token) {
        // Store token in localStorage
        localStorage.setItem('token', response.data.access_token);
        
        // Set default authorization header
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      }
      
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Logout user
  logout() {
    // Remove token from localStorage
    localStorage.removeItem('token');
    
    // Remove authorization header
    delete apiClient.defaults.headers.common['Authorization'];
    
    return Promise.resolve();
  }

  // Get user profile
  async getProfile() {
    try {
      const response = await apiClient.get('/user/profile');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Update user profile
  async updateProfile(userData) {
    try {
      const response = await apiClient.put('/user/profile', userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Change password
  async changePassword(passwordData) {
    try {
      const response = await apiClient.post('/auth/change-password', passwordData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Request password reset
  async requestPasswordReset(email) {
    try {
      const response = await apiClient.post('/auth/forgot-password', { email });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Reset password with token
  async resetPassword(token, newPassword) {
    try {
      const response = await apiClient.post('/auth/reset-password', {
        token,
        new_password: newPassword,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Refresh access token
  async refreshToken() {
    try {
      const response = await apiClient.post('/auth/refresh');
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      }
      
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Verify email
  async verifyEmail(token) {
    try {
      const response = await apiClient.post('/auth/verify-email', { token });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Resend verification email
  async resendVerification(email) {
    try {
      const response = await apiClient.post('/auth/resend-verification', { email });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    // Check if token is expired
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  // Get token from localStorage
  getToken() {
    return localStorage.getItem('token');
  }

  // Get token expiry
  getTokenExpiry(token = null) {
    const authToken = token || this.getToken();
    if (!authToken) return null;
    
    try {
      const payload = JSON.parse(atob(authToken.split('.')[1]));
      return payload.exp * 1000; // Convert to milliseconds
    } catch {
      return null;
    }
  }

  // Set up axios interceptor for token refresh
  setupInterceptors() {
    // Request interceptor to add token
    apiClient.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            await this.refreshToken();
            return apiClient(originalRequest);
          } catch (refreshError) {
            // Refresh failed, redirect to login
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Handle API errors
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || 
                     error.response.data?.detail || 
                     'An error occurred';
      return new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network error. Please check your connection.');
    } else {
      // Something else happened
      return new Error(error.message || 'An unexpected error occurred');
    }
  }

  // Validate email format
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Validate password strength
  validatePassword(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return {
      isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers,
      requirements: {
        minLength: password.length >= minLength,
        hasUpperCase,
        hasLowerCase,
        hasNumbers,
        hasSpecialChar,
      },
    };
  }

  // Generate password strength score
  getPasswordStrength(password) {
    let score = 0;
    const checks = this.validatePassword(password);

    if (checks.requirements.minLength) score += 20;
    if (checks.requirements.hasUpperCase) score += 20;
    if (checks.requirements.hasLowerCase) score += 20;
    if (checks.requirements.hasNumbers) score += 20;
    if (checks.requirements.hasSpecialChar) score += 20;

    return {
      score,
      level: score < 40 ? 'weak' : score < 80 ? 'medium' : 'strong',
    };
  }
}

// Create and export singleton instance
export const authService = new AuthService();

// Set up interceptors
authService.setupInterceptors();