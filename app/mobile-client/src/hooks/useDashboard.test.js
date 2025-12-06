import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import {
  useDashboard,
  useDashboardStats,
  useRecentActivity,
  useUpcomingEvents,
} from './useDashboard';
import dashboardService from '../services/dashboardService';
import { mockDashboardStats, mockActivity, mockEvents } from '../test/mockData';

// Mock the dashboard service
vi.mock('../services/dashboardService', () => ({
  default: {
    getStats: vi.fn(),
    getRecentActivity: vi.fn(),
    getUpcomingEvents: vi.fn(),
    getTasksSummary: vi.fn(),
  },
}));

describe('useDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      dashboardService.getStats.mockResolvedValue(mockDashboardStats);
      dashboardService.getRecentActivity.mockResolvedValue([mockActivity]);
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);

      const { result } = renderHook(() => useDashboard());

      expect(result.current.stats).toBeNull();
      expect(result.current.activity).toEqual([]);
      expect(result.current.upcomingEvents).toEqual([]);
      expect(result.current.loading).toBe(true);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Fetching Dashboard Data', () => {
    it('should fetch all dashboard data on mount', async () => {
      dashboardService.getStats.mockResolvedValue(mockDashboardStats);
      dashboardService.getRecentActivity.mockResolvedValue([mockActivity]);
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);

      const { result } = renderHook(() => useDashboard());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getStats).toHaveBeenCalled();
      expect(dashboardService.getRecentActivity).toHaveBeenCalledWith({ limit: 10 });
      expect(dashboardService.getUpcomingEvents).toHaveBeenCalledWith({ limit: 5 });
      expect(result.current.stats).toEqual(mockDashboardStats);
      expect(result.current.activity).toEqual([mockActivity]);
      expect(result.current.upcomingEvents).toEqual(mockEvents);
    });

    it('should fetch all data in parallel', async () => {
      const statsPromise = new Promise(resolve => setTimeout(() => resolve(mockDashboardStats), 100));
      const activityPromise = new Promise(resolve => setTimeout(() => resolve([mockActivity]), 100));
      const eventsPromise = new Promise(resolve => setTimeout(() => resolve(mockEvents), 100));

      dashboardService.getStats.mockReturnValue(statsPromise);
      dashboardService.getRecentActivity.mockReturnValue(activityPromise);
      dashboardService.getUpcomingEvents.mockReturnValue(eventsPromise);

      const { result } = renderHook(() => useDashboard());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.stats).toEqual(mockDashboardStats);
      expect(result.current.activity).toEqual([mockActivity]);
      expect(result.current.upcomingEvents).toEqual(mockEvents);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch dashboard');
      dashboardService.getStats.mockRejectedValue(error);

      const { result } = renderHook(() => useDashboard());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.stats).toBeNull();
      expect(result.current.error).toBe('Failed to fetch dashboard');
    });
  });

  describe('Refetch', () => {
    it('should refetch all dashboard data', async () => {
      dashboardService.getStats.mockResolvedValue(mockDashboardStats);
      dashboardService.getRecentActivity.mockResolvedValue([mockActivity]);
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);

      const { result } = renderHook(() => useDashboard());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      vi.clearAllMocks();

      const updatedStats = { ...mockDashboardStats, total_events: 100 };
      dashboardService.getStats.mockResolvedValue(updatedStats);
      dashboardService.getRecentActivity.mockResolvedValue([mockActivity]);
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);

      await result.current.refetch();

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getStats).toHaveBeenCalled();
      expect(dashboardService.getRecentActivity).toHaveBeenCalled();
      expect(dashboardService.getUpcomingEvents).toHaveBeenCalled();
    });
  });
});

describe('useDashboardStats', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Stats', () => {
    it('should fetch dashboard stats on mount', async () => {
      dashboardService.getStats.mockResolvedValue(mockDashboardStats);
      const { result } = renderHook(() => useDashboardStats());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getStats).toHaveBeenCalled();
      expect(result.current.stats).toEqual(mockDashboardStats);
      expect(result.current.error).toBeNull();
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch stats');
      dashboardService.getStats.mockRejectedValue(error);
      const { result } = renderHook(() => useDashboardStats());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.stats).toBeNull();
      expect(result.current.error).toBe('Failed to fetch stats');
    });
  });

  describe('Refetch', () => {
    it('should refetch stats', async () => {
      dashboardService.getStats.mockResolvedValue(mockDashboardStats);
      const { result } = renderHook(() => useDashboardStats());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      vi.clearAllMocks();

      const updatedStats = { ...mockDashboardStats, total_events: 50 };
      dashboardService.getStats.mockResolvedValue(updatedStats);

      await result.current.refetch();

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getStats).toHaveBeenCalledTimes(1);
      expect(result.current.stats).toEqual(updatedStats);
    });
  });
});

describe('useRecentActivity', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Activity', () => {
    it('should fetch recent activity on mount without filters', async () => {
      dashboardService.getRecentActivity.mockResolvedValue([mockActivity]);
      const { result } = renderHook(() => useRecentActivity());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getRecentActivity).toHaveBeenCalledWith({});
      expect(result.current.activity).toEqual([mockActivity]);
    });

    it('should fetch activity with filters', async () => {
      const filters = { limit: 20, offset: 10 };
      dashboardService.getRecentActivity.mockResolvedValue([mockActivity]);
      const { result } = renderHook(() => useRecentActivity(filters));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getRecentActivity).toHaveBeenCalledWith(filters);
      expect(result.current.activity).toEqual([mockActivity]);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch activity');
      dashboardService.getRecentActivity.mockRejectedValue(error);
      const { result } = renderHook(() => useRecentActivity());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.activity).toEqual([]);
      expect(result.current.error).toBe('Failed to fetch activity');
    });
  });

  describe('Refetch', () => {
    it('should refetch activity', async () => {
      dashboardService.getRecentActivity.mockResolvedValue([mockActivity]);
      const { result } = renderHook(() => useRecentActivity({ limit: 10 }));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      vi.clearAllMocks();

      const newActivity = { ...mockActivity, id: 2 };
      dashboardService.getRecentActivity.mockResolvedValue([mockActivity, newActivity]);

      await result.current.refetch();

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getRecentActivity).toHaveBeenCalledWith({ limit: 10 });
      expect(result.current.activity).toEqual([mockActivity, newActivity]);
    });
  });
});

describe('useUpcomingEvents', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Upcoming Events', () => {
    it('should fetch upcoming events on mount without filters', async () => {
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useUpcomingEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getUpcomingEvents).toHaveBeenCalledWith({});
      expect(result.current.events).toEqual(mockEvents);
    });

    it('should fetch events with limit filter', async () => {
      const filters = { limit: 10 };
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useUpcomingEvents(filters));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getUpcomingEvents).toHaveBeenCalledWith(filters);
      expect(result.current.events).toEqual(mockEvents);
    });

    it('should fetch events with days filter', async () => {
      const filters = { days: 30 };
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useUpcomingEvents(filters));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getUpcomingEvents).toHaveBeenCalledWith(filters);
    });

    it('should fetch events with multiple filters', async () => {
      const filters = { limit: 5, days: 7 };
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useUpcomingEvents(filters));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getUpcomingEvents).toHaveBeenCalledWith(filters);
      expect(result.current.events).toEqual(mockEvents);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch events');
      dashboardService.getUpcomingEvents.mockRejectedValue(error);
      const { result } = renderHook(() => useUpcomingEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.events).toEqual([]);
      expect(result.current.error).toBe('Failed to fetch events');
    });
  });

  describe('Refetch', () => {
    it('should refetch upcoming events', async () => {
      dashboardService.getUpcomingEvents.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useUpcomingEvents({ days: 7 }));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      vi.clearAllMocks();

      const updatedEvents = [...mockEvents, { ...mockEvents[0], id: '999' }];
      dashboardService.getUpcomingEvents.mockResolvedValue(updatedEvents);

      await result.current.refetch();

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(dashboardService.getUpcomingEvents).toHaveBeenCalledWith({ days: 7 });
      expect(result.current.events).toEqual(updatedEvents);
    });
  });
});
