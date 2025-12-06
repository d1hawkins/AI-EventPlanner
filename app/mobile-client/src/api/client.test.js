import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

// Mock axios before importing client
vi.mock('axios', () => {
  const mockAxiosInstance = {
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    defaults: { headers: { common: {} } },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  };

  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
    },
  };
});

// Import after mock is set up
const { getErrorMessage, isErrorType } = await import('./client');

describe('API Client', () => {
  let axios;
  let createCallConfig;

  beforeEach(async () => {
    // Import axios after mock is set up
    axios = (await import('axios')).default;

    // Save the axios.create config before clearing mocks
    if (axios.create.mock.calls.length > 0) {
      createCallConfig = axios.create.mock.calls[0][0];
    }

    // Clear localStorage but not axios.create mock
    localStorage.clear();
  });

  afterEach(() => {
    // Don't clear axios.create since we need it for config tests
  });

  describe('Configuration', () => {
    it('should create axios instance with correct baseURL from env', async () => {
      expect(axios.create).toHaveBeenCalled();

      // Should use env variable or fallback to /api
      expect(createCallConfig.baseURL).toBeDefined();
    });

    it('should set timeout to 30 seconds', () => {
      expect(createCallConfig.timeout).toBe(30000);
    });

    it('should set Content-Type header', () => {
      expect(createCallConfig.headers['Content-Type']).toBe('application/json');
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
