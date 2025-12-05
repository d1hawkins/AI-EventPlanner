import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('authToken');

    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await apiClient.get('/auth/me');
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('authToken');
      localStorage.removeItem('organizationId');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await apiClient.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const { access_token } = response.data;
    localStorage.setItem('authToken', access_token);

    // Fetch user data
    const userResponse = await apiClient.get('/auth/me');
    setUser(userResponse.data);
    setIsAuthenticated(true);

    // Fetch organization
    try {
      const orgResponse = await apiClient.get('/auth/me/organization');
      if (orgResponse.data?.organization_id) {
        localStorage.setItem('organizationId', orgResponse.data.organization_id.toString());
      }
    } catch (error) {
      console.warn('Could not fetch organization:', error);
    }

    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('organizationId');
    setUser(null);
    setIsAuthenticated(false);
  };

  return {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
  };
};
