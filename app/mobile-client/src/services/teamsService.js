import apiClient from '../api/client';

/**
 * Teams Service
 *
 * Handles all team-related API calls including:
 * - Team member management
 * - Invitations
 * - Role management
 * - Activity tracking
 */

const teamsService = {
  /**
   * Get organization ID from localStorage
   * @returns {string|null} Organization ID
   */
  getOrganizationId() {
    return localStorage.getItem('organizationId');
  },

  /**
   * Get all team members
   * @param {string} orgId - Organization ID (optional, defaults to current org)
   * @returns {Promise<Array>} List of team members
   */
  async getMembers(orgId = null) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    const response = await apiClient.get(`/teams/${organizationId}/members`);
    return response.data;
  },

  /**
   * Get team member by ID
   * @param {string} orgId - Organization ID
   * @param {number} userId - User ID
   * @returns {Promise<Object>} Team member details
   */
  async getMember(orgId, userId) {
    const organizationId = orgId || this.getOrganizationId();
    const response = await apiClient.get(`/teams/${organizationId}/members/${userId}`);
    return response.data;
  },

  /**
   * Invite new team member
   * @param {string} email - Member email
   * @param {string} role - Member role (owner, admin, member)
   * @param {string} orgId - Organization ID (optional)
   * @returns {Promise<Object>} Invitation details
   */
  async inviteMember(email, role = 'member', orgId = null) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    const response = await apiClient.post(`/teams/${organizationId}/invite`, {
      email,
      role,
    });
    return response.data;
  },

  /**
   * Update team member role
   * @param {number} userId - User ID
   * @param {string} role - New role (owner, admin, member)
   * @param {string} orgId - Organization ID (optional)
   * @returns {Promise<Object>} Updated member
   */
  async updateRole(userId, role, orgId = null) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    const response = await apiClient.put(`/teams/${organizationId}/members/${userId}/role`, {
      role,
    });
    return response.data;
  },

  /**
   * Remove team member
   * @param {number} userId - User ID
   * @param {string} orgId - Organization ID (optional)
   * @returns {Promise<void>}
   */
  async removeMember(userId, orgId = null) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    await apiClient.delete(`/teams/${organizationId}/members/${userId}`);
  },

  /**
   * Get team activity log
   * @param {string} orgId - Organization ID (optional)
   * @param {Object} filters - Optional filters (limit, offset)
   * @returns {Promise<Array>} Activity log
   */
  async getActivity(orgId = null, filters = {}) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    const params = new URLSearchParams();
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);

    const response = await apiClient.get(`/teams/${organizationId}/activity?${params.toString()}`);
    return response.data;
  },

  /**
   * Get pending invitations
   * @param {string} orgId - Organization ID (optional)
   * @returns {Promise<Array>} Pending invitations
   */
  async getPendingInvites(orgId = null) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    const response = await apiClient.get(`/teams/${organizationId}/invites/pending`);
    return response.data;
  },

  /**
   * Cancel invitation
   * @param {number} inviteId - Invitation ID
   * @param {string} orgId - Organization ID (optional)
   * @returns {Promise<void>}
   */
  async cancelInvite(inviteId, orgId = null) {
    const organizationId = orgId || this.getOrganizationId();
    if (!organizationId) {
      throw new Error('Organization ID is required');
    }

    await apiClient.delete(`/teams/${organizationId}/invites/${inviteId}`);
  },
};

export default teamsService;
