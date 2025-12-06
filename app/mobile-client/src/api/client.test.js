import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import axios from 'axios';
import apiClient, { getErrorMessage, isErrorType } from './client';

// Mock axios
vi.mock('axios');

describe('API Client', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
    localStorage.clear();

    // Mock axios.create to return a mock axios instance
    axios.create.mockReturnValue({
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
      defaults: { headers: { common: {} } },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Configuration', () => {
    it('should create axios instance with correct baseURL from env', () => {
      expect(axios.create).toHaveBeenCalled();
      const createConfig = axios.create.mock.calls[0][0];

      // Should use env variable or fallback to /api
      expect(createConfig.baseURL).toBeDefined();
    });

    it('should set timeout to 30 seconds', () => {
      const createConfig = axios.create.mock.calls[0][0];
      expect(createConfig.timeout).toBe(30000);
    });

    it('should set Content-Type header', () => {
      const createConfig = axios.create.mock.calls[0][0];
      expect(createConfig.headers['Content-Type']).toBe('application/json');
    });
  });

  describe('getErrorMessage', () => {
    it('should return message from response.data.message', () => {
      const error = {
        response: {
          data: {
            message: 'Test error message',
          },
        },
      };
      expect(getErrorMessage(error)).toBe('Test error message');
    });

    it('should return detail from response.data.detail', () => {
      const error = {
        response: {
          data: {
            detail: 'Test error detail',
          },
        },
      };
      expect(getErrorMessage(error)).toBe('Test error detail');
    });

    it('should return error.message if no response data', () => {
      const error = {
        message: 'Network error',
      };
      expect(getErrorMessage(error)).toBe('Network error');
    });

    it('should return default message if no message found', () => {
      const error = {};
      expect(getErrorMessage(error)).toBe('An unexpected error occurred');
    });
  });

  describe('isErrorType', () => {
    it('should return true if error status matches', () => {
      const error = {
        response: {
          status: 404,
        },
      };
      expect(isErrorType(error, 404)).toBe(true);
    });

    it('should return false if error status does not match', () => {
      const error = {
        response: {
          status: 404,
        },
      };
      expect(isErrorType(error, 500)).toBe(false);
    });

    it('should return false if no response', () => {
      const error = {};
      expect(isErrorType(error, 404)).toBe(false);
    });
  });
});
