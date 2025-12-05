import apiClient from '../api/client';

/**
 * Subscription Service
 *
 * Handles all subscription-related API calls including:
 * - Usage limits
 * - Billing status
 * - Plan upgrades/downgrades
 * - Payment history
 */

const subscriptionService = {
  /**
   * Get organization ID from localStorage
   * @returns {string|null} Organization ID
   */
  getOrganizationId() {
    return localStorage.getItem('organizationId');
  },

  /**
   * Get usage limits for organization
   * @param {string} orgId - Organization ID (optional, defaults to current org)
   * @returns {Promise<Object>} Usage limits
   */
  async getUsageLimits(orgId = null) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    const response = await apiClient.get(`/subscription/organizations/${organizationId}/usage-limits`);
    return response.data;
  },

  /**
   * Get subscription status
   * @returns {Promise<Object>} Subscription status
   */
  async getStatus() {
    const response = await apiClient.get('/subscription/status');
    return response.data;
  },

  /**
   * Get current plan details
   * @returns {Promise<Object>} Plan details
   */
  async getCurrentPlan() {
    const response = await apiClient.get('/subscription/plan');
    return response.data;
  },

  /**
   * Get available plans
   * @returns {Promise<Array>} List of available plans
   */
  async getAvailablePlans() {
    const response = await apiClient.get('/subscription/plans');
    return response.data;
  },

  /**
   * Get billing history
   * @param {Object} filters - Optional filters (limit, offset)
   * @returns {Promise<Array>} Billing history
   */
  async getBillingHistory(filters = {}) {
    const params = new URLSearchParams();
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);

    const response = await apiClient.get(`/subscription/billing-history?${params.toString()}`);
    return response.data;
  },

  /**
   * Upgrade subscription
   * @param {string} planId - Target plan ID
   * @returns {Promise<Object>} Updated subscription
   */
  async upgrade(planId) {
    const response = await apiClient.post('/subscription/upgrade', { plan_id: planId });
    return response.data;
  },

  /**
   * Downgrade subscription
   * @param {string} planId - Target plan ID
   * @returns {Promise<Object>} Updated subscription
   */
  async downgrade(planId) {
    const response = await apiClient.post('/subscription/downgrade', { plan_id: planId });
    return response.data;
  },

  /**
   * Cancel subscription
   * @returns {Promise<Object>} Cancellation details
   */
  async cancel() {
    const response = await apiClient.post('/subscription/cancel');
    return response.data;
  },

  /**
   * Get payment method
   * @returns {Promise<Object>} Payment method details
   */
  async getPaymentMethod() {
    const response = await apiClient.get('/subscription/payment-method');
    return response.data;
  },

  /**
   * Update payment method
   * @param {Object} paymentData - Payment method data
   * @returns {Promise<Object>} Updated payment method
   */
  async updatePaymentMethod(paymentData) {
    const response = await apiClient.put('/subscription/payment-method', paymentData);
    return response.data;
  },

  /**
   * Get usage statistics
   * @param {string} orgId - Organization ID (optional)
   * @returns {Promise<Object>} Usage statistics
   */
  async getUsageStats(orgId = null) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    const response = await apiClient.get(`/subscription/organizations/${organizationId}/usage`);
    return response.data;
  },
};

export default subscriptionService;
