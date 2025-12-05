import apiClient from '../api/client';

/**
 * Dashboard Service
 *
 * Handles all dashboard-related API calls including:
 * - Overview statistics
 * - Recent activity
 * - Upcoming events
 */

const dashboardService = {
  /**
   * Get dashboard overview statistics
   * @returns {Promise<Object>} Overview stats
   */
  async getStats() {
    const response = await apiClient.get('/dashboard/stats');
    return response.data;
  },

  /**
   * Get recent activity
   * @param {Object} filters - Optional filters (limit, offset)
   * @returns {Promise<Array>} Recent activity items
   */
  async getRecentActivity(filters = {}) {
    const params = new URLSearchParams();
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);

    const response = await apiClient.get(`/dashboard/recent-activity?${params.toString()}`);
    return response.data;
  },

  /**
   * Get upcoming events
   * @param {Object} filters - Optional filters (limit, days)
   * @returns {Promise<Array>} Upcoming events
   */
  async getUpcomingEvents(filters = {}) {
    const params = new URLSearchParams();
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.days) params.append('days', filters.days);

    const response = await apiClient.get(`/dashboard/upcoming-events?${params.toString()}`);
    return response.data;
  },

  /**
   * Get quick stats summary
   * @returns {Promise<Object>} Quick stats
   */
  async getQuickStats() {
    const response = await apiClient.get('/dashboard/quick-stats');
    return response.data;
  },
};

export default dashboardService;
