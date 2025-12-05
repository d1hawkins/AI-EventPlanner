import { useState, useEffect, useCallback } from 'react';
import dashboardService from '../services/dashboardService';
import { getErrorMessage } from '../api/client';

/**
 * useDashboard - Custom hook for dashboard data
 *
 * Features:
 * - Get overview statistics
 * - Fetch recent activity
 * - Get upcoming events
 *
 * Usage:
 * const { stats, activity, upcomingEvents, loading, error, refetch } = useDashboard();
 */

export const useDashboard = () => {
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, activityData, eventsData] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getRecentActivity({ limit: 10 }),
        dashboardService.getUpcomingEvents({ limit: 5 }),
      ]);

      setStats(statsData);
      setActivity(activityData);
      setUpcomingEvents(eventsData);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return {
    stats,
    activity,
    upcomingEvents,
    loading,
    error,
    refetch: fetchDashboard,
  };
};

/**
 * useDashboardStats - Custom hook specifically for stats
 *
 * Usage:
 * const { stats, loading, error, refetch } = useDashboardStats();
 */

export const useDashboardStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardService.getStats();
      setStats(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
};

/**
 * useRecentActivity - Custom hook for recent activity
 *
 * Usage:
 * const { activity, loading, error, refetch } = useRecentActivity({ limit: 10 });
 */

export const useRecentActivity = (filters = {}) => {
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchActivity = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardService.getRecentActivity(filters);
      setActivity(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchActivity();
  }, [fetchActivity]);

  return {
    activity,
    loading,
    error,
    refetch: fetchActivity,
  };
};

/**
 * useUpcomingEvents - Custom hook for upcoming events
 *
 * Usage:
 * const { events, loading, error, refetch } = useUpcomingEvents({ limit: 5, days: 30 });
 */

export const useUpcomingEvents = (filters = {}) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardService.getUpcomingEvents(filters);
      setEvents(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  return {
    events,
    loading,
    error,
    refetch: fetchEvents,
  };
};
