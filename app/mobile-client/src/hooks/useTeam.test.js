import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useTeam, useTeamActivity, usePendingInvites } from './useTeam';
import teamsService from '../services/teamsService';
import { mockTeamMembers, mockTeamMember, mockActivity, mockInvite } from '../test/mockData';

// Mock the teams service
vi.mock('../services/teamsService');

describe('useTeam', () => {
  const mockOrgId = 'org-123';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      teamsService.getMembers.mockResolvedValue(mockTeamMembers);
      const { result } = renderHook(() => useTeam());

      expect(result.current.members).toEqual([]);
      expect(result.current.loading).toBe(true);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Fetching Members', () => {
    it('should fetch team members on mount', async () => {
      teamsService.getMembers.mockResolvedValue(mockTeamMembers);
      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getMembers).toHaveBeenCalledWith(null);
      expect(result.current.members).toEqual(mockTeamMembers);
      expect(result.current.error).toBeNull();
    });

    it('should fetch members with custom org ID', async () => {
      teamsService.getMembers.mockResolvedValue(mockTeamMembers);
      const { result } = renderHook(() => useTeam(mockOrgId));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getMembers).toHaveBeenCalledWith(mockOrgId);
      expect(result.current.members).toEqual(mockTeamMembers);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch members');
      teamsService.getMembers.mockRejectedValue(error);
      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.members).toEqual([]);
      expect(result.current.error).toBe('Failed to fetch members');
    });
  });

  describe('Inviting Members', () => {
    it('should invite a member with default role', async () => {
      teamsService.getMembers.mockResolvedValue([]);
      teamsService.inviteMember.mockResolvedValue(mockInvite);

      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      teamsService.getMembers.mockResolvedValue([mockTeamMember]);

      let invitation;
      await act(async () => {
        invitation = await result.current.inviteMember('test@example.com');
      });

      expect(teamsService.inviteMember).toHaveBeenCalledWith('test@example.com', 'member', null);
      expect(invitation).toEqual(mockInvite);
      expect(teamsService.getMembers).toHaveBeenCalledTimes(2); // Initial + after invite
    });

    it('should invite a member with custom role', async () => {
      teamsService.getMembers.mockResolvedValue([]);
      teamsService.inviteMember.mockResolvedValue(mockInvite);

      const { result } = renderHook(() => useTeam(mockOrgId));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      teamsService.getMembers.mockResolvedValue([mockTeamMember]);

      await act(async () => {
        await result.current.inviteMember('admin@example.com', 'admin');
      });

      expect(teamsService.inviteMember).toHaveBeenCalledWith(
        'admin@example.com',
        'admin',
        mockOrgId
      );
    });

    it('should throw error on invite failure', async () => {
      teamsService.getMembers.mockResolvedValue([]);
      const error = new Error('Invite failed');
      teamsService.inviteMember.mockRejectedValue(error);

      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.inviteMember('test@example.com');
        });
      }).rejects.toThrow('Invite failed');
    });
  });

  describe('Updating Member Role', () => {
    it('should update member role', async () => {
      teamsService.getMembers.mockResolvedValue(mockTeamMembers);
      const updatedMember = { ...mockTeamMember, role: 'admin' };
      teamsService.updateRole.mockResolvedValue(updatedMember);

      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.updateRole(mockTeamMember.id, 'admin');
      });

      expect(teamsService.updateRole).toHaveBeenCalledWith(mockTeamMember.id, 'admin', null);
      expect(result.current.members).toContainEqual(updatedMember);
    });

    it('should throw error on update failure', async () => {
      teamsService.getMembers.mockResolvedValue(mockTeamMembers);
      const error = new Error('Update failed');
      teamsService.updateRole.mockRejectedValue(error);

      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.updateRole(mockTeamMember.id, 'admin');
        });
      }).rejects.toThrow('Update failed');
    });
  });

  describe('Removing Members', () => {
    it('should remove a member', async () => {
      teamsService.getMembers.mockResolvedValue(mockTeamMembers);
      teamsService.removeMember.mockResolvedValue({});

      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const initialCount = result.current.members.length;

      await act(async () => {
        await result.current.removeMember(mockTeamMember.id);
      });

      expect(teamsService.removeMember).toHaveBeenCalledWith(mockTeamMember.id, null);
      expect(result.current.members).toHaveLength(initialCount - 1);
      expect(result.current.members.find(m => m.id === mockTeamMember.id)).toBeUndefined();
    });

    it('should throw error on remove failure', async () => {
      teamsService.getMembers.mockResolvedValue(mockTeamMembers);
      const error = new Error('Remove failed');
      teamsService.removeMember.mockRejectedValue(error);

      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.removeMember(mockTeamMember.id);
        });
      }).rejects.toThrow('Remove failed');
    });
  });

  describe('Refetch', () => {
    it('should refetch members', async () => {
      teamsService.getMembers.mockResolvedValue(mockTeamMembers);
      const { result } = renderHook(() => useTeam());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      teamsService.getMembers.mockClear();
      teamsService.getMembers.mockResolvedValue([...mockTeamMembers, mockTeamMember]);

      await act(async () => {
        await result.current.refetch();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getMembers).toHaveBeenCalledTimes(1);
    });
  });
});

describe('useTeamActivity', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Activity', () => {
    it('should fetch team activity on mount', async () => {
      const activityList = [mockActivity];
      teamsService.getActivity.mockResolvedValue(activityList);
      const { result } = renderHook(() => useTeamActivity());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getActivity).toHaveBeenCalledWith(null, {});
      expect(result.current.activity).toEqual(activityList);
    });

    it('should fetch activity with org ID and filters', async () => {
      const filters = { limit: 10, offset: 0 };
      const activityList = [mockActivity];
      teamsService.getActivity.mockResolvedValue(activityList);
      const { result } = renderHook(() => useTeamActivity('org-123', filters));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getActivity).toHaveBeenCalledWith('org-123', filters);
      expect(result.current.activity).toEqual(activityList);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch activity');
      teamsService.getActivity.mockRejectedValue(error);
      const { result } = renderHook(() => useTeamActivity());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.activity).toEqual([]);
      expect(result.current.error).toBe('Failed to fetch activity');
    });
  });

  describe('Refetch', () => {
    it('should refetch activity', async () => {
      teamsService.getActivity.mockResolvedValue([mockActivity]);
      const { result } = renderHook(() => useTeamActivity());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      teamsService.getActivity.mockClear();
      teamsService.getActivity.mockResolvedValue([mockActivity, mockActivity]);

      await act(async () => {
        await result.current.refetch();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getActivity).toHaveBeenCalledTimes(1);
    });
  });
});

describe('usePendingInvites', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Invites', () => {
    it('should fetch pending invites on mount', async () => {
      const invites = [mockInvite];
      teamsService.getPendingInvites.mockResolvedValue(invites);
      const { result } = renderHook(() => usePendingInvites());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getPendingInvites).toHaveBeenCalledWith(null);
      expect(result.current.invites).toEqual(invites);
    });

    it('should fetch invites with org ID', async () => {
      const invites = [mockInvite];
      teamsService.getPendingInvites.mockResolvedValue(invites);
      const { result } = renderHook(() => usePendingInvites('org-123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getPendingInvites).toHaveBeenCalledWith('org-123');
      expect(result.current.invites).toEqual(invites);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch invites');
      teamsService.getPendingInvites.mockRejectedValue(error);
      const { result } = renderHook(() => usePendingInvites());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.invites).toEqual([]);
      expect(result.current.error).toBe('Failed to fetch invites');
    });
  });

  describe('Canceling Invites', () => {
    it('should cancel an invite', async () => {
      const invites = [mockInvite];
      teamsService.getPendingInvites.mockResolvedValue(invites);
      teamsService.cancelInvite.mockResolvedValue({});

      const { result } = renderHook(() => usePendingInvites());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.cancelInvite(mockInvite.id);
      });

      expect(teamsService.cancelInvite).toHaveBeenCalledWith(mockInvite.id, null);
      expect(result.current.invites).toHaveLength(0);
      expect(result.current.invites.find(i => i.id === mockInvite.id)).toBeUndefined();
    });

    it('should throw error on cancel failure', async () => {
      teamsService.getPendingInvites.mockResolvedValue([mockInvite]);
      const error = new Error('Cancel failed');
      teamsService.cancelInvite.mockRejectedValue(error);

      const { result } = renderHook(() => usePendingInvites());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.cancelInvite(mockInvite.id);
        });
      }).rejects.toThrow('Cancel failed');
    });
  });

  describe('Refetch', () => {
    it('should refetch invites', async () => {
      teamsService.getPendingInvites.mockResolvedValue([mockInvite]);
      const { result } = renderHook(() => usePendingInvites());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      teamsService.getPendingInvites.mockClear();
      teamsService.getPendingInvites.mockResolvedValue([mockInvite, mockInvite]);

      await act(async () => {
        await result.current.refetch();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(teamsService.getPendingInvites).toHaveBeenCalledTimes(1);
    });
  });
});
