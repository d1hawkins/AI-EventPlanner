import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth } from './useAuth';
import apiClient from '../api/client';

// Mock the API client
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    defaults: { headers: { common: {} } },
  },
  getErrorMessage: vi.fn((error) => error?.response?.data?.message || error?.response?.data?.detail || error?.message || 'An unexpected error occurred'),
  isErrorType: vi.fn((error, status) => error?.response?.status === status),
}));

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    console.error = vi.fn();
    console.warn = vi.fn();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      apiClient.get.mockResolvedValue({ data: null });
      const { result } = renderHook(() => useAuth());

      // Check initial state (loading state is handled by effect, checked in other tests)
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('Check Auth', () => {
    it('should set loading to false if no token exists', async () => {
      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(apiClient.get).not.toHaveBeenCalled();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('should authenticate user if token exists and is valid', async () => {
      const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };
      localStorage.setItem('authToken', 'valid-token');
      apiClient.get.mockResolvedValue({ data: mockUser });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(apiClient.get).toHaveBeenCalledWith('/auth/me');
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('should handle expired or invalid token', async () => {
      localStorage.setItem('authToken', 'invalid-token');
      localStorage.setItem('organizationId', 'org-123');
      apiClient.get.mockRejectedValue(new Error('Unauthorized'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(localStorage.getItem('authToken')).toBeNull();
      expect(localStorage.getItem('organizationId')).toBeNull();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('Login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };
      const mockAuthResponse = { access_token: 'new-token' };
      const mockOrgResponse = { organization_id: 123 };

      apiClient.post.mockResolvedValue({ data: mockAuthResponse });
      apiClient.get.mockResolvedValueOnce({ data: mockUser });
      apiClient.get.mockResolvedValueOnce({ data: mockOrgResponse });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      let loginResponse;
      await act(async () => {
        loginResponse = await result.current.login('testuser', 'password123');
      });

      expect(apiClient.post).toHaveBeenCalledWith(
        '/auth/token',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      expect(apiClient.get).toHaveBeenCalledWith('/auth/me');
      expect(apiClient.get).toHaveBeenCalledWith('/auth/me/organization');
      expect(localStorage.getItem('authToken')).toBe('new-token');
      expect(localStorage.getItem('organizationId')).toBe('123');
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
      expect(loginResponse).toEqual(mockAuthResponse);
    });

    it('should login successfully even if organization fetch fails', async () => {
      const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };
      const mockAuthResponse = { access_token: 'new-token' };

      apiClient.post.mockResolvedValue({ data: mockAuthResponse });
      apiClient.get.mockResolvedValueOnce({ data: mockUser });
      apiClient.get.mockRejectedValueOnce(new Error('Org not found'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.login('testuser', 'password123');
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
      expect(localStorage.getItem('organizationId')).toBeNull();
      expect(console.warn).toHaveBeenCalledWith('Could not fetch organization:', expect.any(Error));
    });

    it('should throw error on login failure', async () => {
      apiClient.post.mockRejectedValue(new Error('Invalid credentials'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.login('wronguser', 'wrongpass');
        });
      }).rejects.toThrow('Invalid credentials');
    });

    it('should handle user fetch failure after successful token generation', async () => {
      const mockAuthResponse = { access_token: 'new-token' };

      apiClient.post.mockResolvedValue({ data: mockAuthResponse });
      apiClient.get.mockRejectedValue(new Error('User not found'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.login('testuser', 'password123');
        });
      }).rejects.toThrow('User not found');

      expect(localStorage.getItem('authToken')).toBe('new-token');
    });

    it('should properly format FormData for login', async () => {
      const mockUser = { id: 1, username: 'testuser' };
      const mockAuthResponse = { access_token: 'token' };

      let capturedFormData;
      apiClient.post.mockImplementation((url, formData) => {
        capturedFormData = formData;
        return Promise.resolve({ data: mockAuthResponse });
      });
      apiClient.get.mockResolvedValue({ data: mockUser });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.login('testuser', 'password123');
      });

      expect(capturedFormData).toBeInstanceOf(FormData);
      expect(capturedFormData.get('username')).toBe('testuser');
      expect(capturedFormData.get('password')).toBe('password123');
    });
  });

  describe('Logout', () => {
    it('should logout user and clear localStorage', async () => {
      const mockUser = { id: 1, username: 'testuser' };
      localStorage.setItem('authToken', 'valid-token');
      localStorage.setItem('organizationId', '123');
      apiClient.get.mockResolvedValue({ data: mockUser });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.isAuthenticated).toBe(true);

      act(() => {
        result.current.logout();
      });

      expect(localStorage.getItem('authToken')).toBeNull();
      expect(localStorage.getItem('organizationId')).toBeNull();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('should logout even if not authenticated', () => {
      const { result } = renderHook(() => useAuth());

      act(() => {
        result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });
});
