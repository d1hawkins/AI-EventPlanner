import { describe, it, expect, beforeEach, vi } from 'vitest';
import teamsService from './teamsService';
import apiClient from '../api/client';
import { mockTeamMembers, mockTeamMember, mockInvite, mockActivity } from '../test/mockData';

// Mock the API client
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('teamsService', () => {
  const mockOrgId = 'org-123';

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('organizationId', mockOrgId);
  });

  describe('getOrganizationId', () => {
    it('should retrieve organization ID from localStorage', () => {
      const orgId = teamsService.getOrganizationId();
      expect(orgId).toBe(mockOrgId);
    });

    it('should return null if no organization ID in localStorage', () => {
      localStorage.clear();
      const orgId = teamsService.getOrganizationId();
      expect(orgId).toBeNull();
    });
  });

  describe('getMembers', () => {
    it('should fetch all team members using stored org ID', async () => {
      apiClient.get.mockResolvedValue({ data: mockTeamMembers });

      const result = await teamsService.getMembers();

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${mockOrgId}/members`);
      expect(result).toEqual(mockTeamMembers);
    });

    it('should fetch team members with custom org ID', async () => {
      const customOrgId = 'custom-org';
      apiClient.get.mockResolvedValue({ data: mockTeamMembers });

      const result = await teamsService.getMembers(customOrgId);

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${customOrgId}/members`);
      expect(result).toEqual(mockTeamMembers);
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(teamsService.getMembers()).rejects.toThrow('Organization ID is required');
    });
  });

  describe('getMember', () => {
    it('should fetch a single team member', async () => {
      const userId = 1;
      apiClient.get.mockResolvedValue({ data: mockTeamMember });

      const result = await teamsService.getMember(mockOrgId, userId);

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${mockOrgId}/members/${userId}`);
      expect(result).toEqual(mockTeamMember);
    });

    it('should use stored org ID if not provided', async () => {
      const userId = 1;
      apiClient.get.mockResolvedValue({ data: mockTeamMember });

      const result = await teamsService.getMember(null, userId);

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${mockOrgId}/members/${userId}`);
      expect(result).toEqual(mockTeamMember);
    });
  });

  describe('inviteMember', () => {
    it('should invite a new team member with default role', async () => {
      const email = 'newmember@example.com';
      apiClient.post.mockResolvedValue({ data: mockInvite });

      const result = await teamsService.inviteMember(email);

      expect(apiClient.post).toHaveBeenCalledWith(`/teams/${mockOrgId}/invite`, {
        email,
        role: 'member',
      });
      expect(result).toEqual(mockInvite);
    });

    it('should invite a team member with custom role', async () => {
      const email = 'admin@example.com';
      const role = 'admin';
      apiClient.post.mockResolvedValue({ data: mockInvite });

      const result = await teamsService.inviteMember(email, role);

      expect(apiClient.post).toHaveBeenCalledWith(`/teams/${mockOrgId}/invite`, {
        email,
        role,
      });
      expect(result).toEqual(mockInvite);
    });

    it('should invite a member with custom org ID', async () => {
      const email = 'member@example.com';
      const customOrgId = 'custom-org';
      apiClient.post.mockResolvedValue({ data: mockInvite });

      const result = await teamsService.inviteMember(email, 'member', customOrgId);

      expect(apiClient.post).toHaveBeenCalledWith(`/teams/${customOrgId}/invite`, {
        email,
        role: 'member',
      });
      expect(result).toEqual(mockInvite);
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(teamsService.inviteMember('test@example.com')).rejects.toThrow(
        'Organization ID is required'
      );
    });
  });

  describe('updateRole', () => {
    it('should update a team member role', async () => {
      const userId = 1;
      const newRole = 'admin';
      const updatedMember = { ...mockTeamMember, role: newRole };
      apiClient.put.mockResolvedValue({ data: updatedMember });

      const result = await teamsService.updateRole(userId, newRole);

      expect(apiClient.put).toHaveBeenCalledWith(`/teams/${mockOrgId}/members/${userId}/role`, {
        role: newRole,
      });
      expect(result.role).toBe(newRole);
    });

    it('should update role with custom org ID', async () => {
      const userId = 1;
      const newRole = 'owner';
      const customOrgId = 'custom-org';
      apiClient.put.mockResolvedValue({ data: mockTeamMember });

      await teamsService.updateRole(userId, newRole, customOrgId);

      expect(apiClient.put).toHaveBeenCalledWith(`/teams/${customOrgId}/members/${userId}/role`, {
        role: newRole,
      });
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(teamsService.updateRole(1, 'admin')).rejects.toThrow(
        'Organization ID is required'
      );
    });
  });

  describe('removeMember', () => {
    it('should remove a team member', async () => {
      const userId = 1;
      apiClient.delete.mockResolvedValue({ data: { success: true } });

      await teamsService.removeMember(userId);

      expect(apiClient.delete).toHaveBeenCalledWith(`/teams/${mockOrgId}/members/${userId}`);
    });

    it('should remove member with custom org ID', async () => {
      const userId = 1;
      const customOrgId = 'custom-org';
      apiClient.delete.mockResolvedValue({ data: { success: true } });

      await teamsService.removeMember(userId, customOrgId);

      expect(apiClient.delete).toHaveBeenCalledWith(`/teams/${customOrgId}/members/${userId}`);
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(teamsService.removeMember(1)).rejects.toThrow('Organization ID is required');
    });
  });

  describe('getActivity', () => {
    it('should fetch team activity without filters', async () => {
      apiClient.get.mockResolvedValue({ data: [mockActivity] });

      const result = await teamsService.getActivity();

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${mockOrgId}/activity?`);
      expect(result).toEqual([mockActivity]);
    });

    it('should fetch team activity with limit filter', async () => {
      const filters = { limit: 10 };
      apiClient.get.mockResolvedValue({ data: [mockActivity] });

      const result = await teamsService.getActivity(null, filters);

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${mockOrgId}/activity?limit=10`);
      expect(result).toEqual([mockActivity]);
    });

    it('should fetch team activity with offset filter', async () => {
      const filters = { offset: 20 };
      apiClient.get.mockResolvedValue({ data: [mockActivity] });

      await teamsService.getActivity(null, filters);

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${mockOrgId}/activity?offset=20`);
    });

    it('should fetch team activity with multiple filters', async () => {
      const filters = { limit: 10, offset: 20 };
      apiClient.get.mockResolvedValue({ data: [mockActivity] });

      await teamsService.getActivity(null, filters);

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${mockOrgId}/activity?limit=10&offset=20`);
    });

    it('should fetch activity with custom org ID', async () => {
      const customOrgId = 'custom-org';
      apiClient.get.mockResolvedValue({ data: [mockActivity] });

      await teamsService.getActivity(customOrgId);

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${customOrgId}/activity?`);
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(teamsService.getActivity()).rejects.toThrow('Organization ID is required');
    });
  });

  describe('getPendingInvites', () => {
    it('should fetch pending invitations', async () => {
      apiClient.get.mockResolvedValue({ data: [mockInvite] });

      const result = await teamsService.getPendingInvites();

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${mockOrgId}/invites/pending`);
      expect(result).toEqual([mockInvite]);
    });

    it('should fetch pending invites with custom org ID', async () => {
      const customOrgId = 'custom-org';
      apiClient.get.mockResolvedValue({ data: [mockInvite] });

      await teamsService.getPendingInvites(customOrgId);

      expect(apiClient.get).toHaveBeenCalledWith(`/teams/${customOrgId}/invites/pending`);
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(teamsService.getPendingInvites()).rejects.toThrow(
        'Organization ID is required'
      );
    });
  });

  describe('cancelInvite', () => {
    it('should cancel an invitation', async () => {
      const inviteId = 1;
      apiClient.delete.mockResolvedValue({ data: { success: true } });

      await teamsService.cancelInvite(inviteId);

      expect(apiClient.delete).toHaveBeenCalledWith(`/teams/${mockOrgId}/invites/${inviteId}`);
    });

    it('should cancel invite with custom org ID', async () => {
      const inviteId = 1;
      const customOrgId = 'custom-org';
      apiClient.delete.mockResolvedValue({ data: { success: true } });

      await teamsService.cancelInvite(inviteId, customOrgId);

      expect(apiClient.delete).toHaveBeenCalledWith(`/teams/${customOrgId}/invites/${inviteId}`);
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(teamsService.cancelInvite(1)).rejects.toThrow('Organization ID is required');
    });
  });
});
