import { describe, it, expect, beforeEach, vi } from 'vitest';
import dashboardService from './dashboardService';
import apiClient from '../api/client';
import { mockDashboardStats, mockActivity, mockEvents } from '../test/mockData';

// Mock the API client
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('dashboardService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getStats', () => {
    it('should fetch dashboard statistics', async () => {
      apiClient.get.mockResolvedValue({ data: mockDashboardStats });

      const result = await dashboardService.getStats();

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/stats');
      expect(result).toEqual(mockDashboardStats);
    });
  });

  describe('getRecentActivity', () => {
    it('should fetch recent activity without filters', async () => {
      const activityList = [mockActivity];
      apiClient.get.mockResolvedValue({ data: activityList });

      const result = await dashboardService.getRecentActivity();

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/recent-activity?');
      expect(result).toEqual(activityList);
    });

    it('should fetch recent activity with limit filter', async () => {
      const filters = { limit: 10 };
      const activityList = [mockActivity];
      apiClient.get.mockResolvedValue({ data: activityList });

      const result = await dashboardService.getRecentActivity(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/recent-activity?limit=10');
      expect(result).toEqual(activityList);
    });

    it('should fetch recent activity with offset filter', async () => {
      const filters = { offset: 5 };
      const activityList = [mockActivity];
      apiClient.get.mockResolvedValue({ data: activityList });

      await dashboardService.getRecentActivity(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/recent-activity?offset=5');
    });

    it('should fetch recent activity with multiple filters', async () => {
      const filters = { limit: 10, offset: 5 };
      const activityList = [mockActivity];
      apiClient.get.mockResolvedValue({ data: activityList });

      await dashboardService.getRecentActivity(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/recent-activity?limit=10&offset=5');
    });
  });

  describe('getUpcomingEvents', () => {
    it('should fetch upcoming events without filters', async () => {
      apiClient.get.mockResolvedValue({ data: mockEvents });

      const result = await dashboardService.getUpcomingEvents();

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/upcoming-events?');
      expect(result).toEqual(mockEvents);
    });

    it('should fetch upcoming events with limit filter', async () => {
      const filters = { limit: 5 };
      apiClient.get.mockResolvedValue({ data: mockEvents });

      const result = await dashboardService.getUpcomingEvents(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/upcoming-events?limit=5');
      expect(result).toEqual(mockEvents);
    });

    it('should fetch upcoming events with days filter', async () => {
      const filters = { days: 7 };
      apiClient.get.mockResolvedValue({ data: mockEvents });

      await dashboardService.getUpcomingEvents(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/upcoming-events?days=7');
    });

    it('should fetch upcoming events with multiple filters', async () => {
      const filters = { limit: 5, days: 7 };
      apiClient.get.mockResolvedValue({ data: mockEvents });

      await dashboardService.getUpcomingEvents(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/upcoming-events?limit=5&days=7');
    });
  });

  describe('getQuickStats', () => {
    it('should fetch quick stats summary', async () => {
      const quickStats = {
        total_events: 10,
        upcoming_events: 5,
        completed_events: 3,
        active_tasks: 15,
      };
      apiClient.get.mockResolvedValue({ data: quickStats });

      const result = await dashboardService.getQuickStats();

      expect(apiClient.get).toHaveBeenCalledWith('/dashboard/quick-stats');
      expect(result).toEqual(quickStats);
    });
  });
});
