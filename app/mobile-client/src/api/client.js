import axios from 'axios';

/**
 * API Client Configuration
 *
 * Features:
 * - Automatic auth token injection
 * - Tenant ID header management
 * - Centralized error handling
 * - Request/response logging (dev mode)
 * - Token refresh handling
 * - Environment-based API URL configuration
 */

// Get API base URL from environment variable
// In development, can use local proxy or point to Azure
// In production, points to Azure backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

console.log('🔗 API Base URL:', API_BASE_URL);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Development logging
const isDev = import.meta.env.DEV;

// Request interceptor to add auth token and tenant ID
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    const orgId = localStorage.getItem('organizationId');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    if (orgId) {
      config.headers['X-Tenant-ID'] = orgId;
    }

    // Log requests in development
    if (isDev) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }

    return config;
  },
  (error) => {
    if (isDev) {
      console.error('[API Request Error]', error);
    }
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
apiClient.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (isDev) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    }
    return response;
  },
  (error) => {
    // Log errors in development
    if (isDev) {
      console.error('[API Error]', error.response?.status, error.message, error.response?.data);
    }

    // Handle specific error cases
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // Unauthorized - clear auth and redirect to login
          localStorage.removeItem('authToken');
          localStorage.removeItem('organizationId');
          localStorage.removeItem('user');
          window.location.href = '/login';
          break;

        case 403:
          // Forbidden - permission denied
          console.error('Permission denied:', data.message || 'You do not have permission to perform this action');
          break;

        case 404:
          // Not found
          console.error('Resource not found:', data.message || 'The requested resource was not found');
          break;

        case 429:
          // Rate limited
          console.error('Rate limit exceeded:', data.message || 'Too many requests. Please try again later');
          break;

        case 500:
        case 502:
        case 503:
        case 504:
          // Server errors
          console.error('Server error:', data.message || 'An error occurred on the server. Please try again');
          break;

        default:
          console.error('API error:', data.message || 'An unexpected error occurred');
      }
    } else if (error.request) {
      // Network error - no response received
      console.error('Network error: Could not connect to server');
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }

    return Promise.reject(error);
  }
);

/**
 * Helper function to extract error message from API error
 */
export const getErrorMessage = (error) => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

/**
 * Helper function to check if error is a specific type
 */
export const isErrorType = (error, statusCode) => {
  return error.response?.status === statusCode;
};

export default apiClient;
