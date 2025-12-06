import { useState, useEffect, useCallback, useMemo } from 'react';
import teamsService from '../services/teamsService';
import { getErrorMessage } from '../api/client';

/**
 * useTeam - Custom hook for team data management
 *
 * Features:
 * - Fetch team members
 * - Invite new members
 * - Update member roles
 * - Remove members
 * - Get team activity
 *
 * Usage:
 * const { members, loading, error, inviteMember, updateRole, removeMember } = useTeam();
 */

export const useTeam = (orgId = null) => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMembers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await teamsService.getMembers(orgId);
      setMembers(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    fetchMembers();
  }, [fetchMembers]);

  const inviteMember = useCallback(async (email, role = 'member') => {
    try {
      const invitation = await teamsService.inviteMember(email, role, orgId);
      // Optionally refetch members to include pending invites
      await fetchMembers();
      return invitation;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [orgId, fetchMembers]);

  const updateRole = useCallback(async (userId, role) => {
    try {
      const updatedMember = await teamsService.updateRole(userId, role, orgId);
      setMembers((prev) =>
        prev.map((member) => (member.id === userId ? updatedMember : member))
      );
      return updatedMember;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [orgId]);

  const removeMember = useCallback(async (userId) => {
    try {
      await teamsService.removeMember(userId, orgId);
      setMembers((prev) => prev.filter((member) => member.id !== userId));
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [orgId]);

  return {
    members,
    loading,
    error,
    inviteMember,
    updateRole,
    removeMember,
    refetch: fetchMembers,
  };
};

/**
 * useTeamActivity - Custom hook for team activity log
 *
 * Usage:
 * const { activity, loading, error, refetch } = useTeamActivity();
 */

export const useTeamActivity = (orgId = null, filters = {}) => {
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Stabilize filters object to prevent infinite loops
  const stableFilters = useMemo(() => filters, [JSON.stringify(filters)]);

  const fetchActivity = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await teamsService.getActivity(orgId, stableFilters);
      setActivity(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [orgId, stableFilters]);

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
 * usePendingInvites - Custom hook for pending invitations
 *
 * Usage:
 * const { invites, loading, cancelInvite } = usePendingInvites();
 */

export const usePendingInvites = (orgId = null) => {
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInvites = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await teamsService.getPendingInvites(orgId);
      setInvites(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    fetchInvites();
  }, [fetchInvites]);

  const cancelInvite = useCallback(async (inviteId) => {
    try {
      await teamsService.cancelInvite(inviteId, orgId);
      setInvites((prev) => prev.filter((invite) => invite.id !== inviteId));
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [orgId]);

  return {
    invites,
    loading,
    error,
    cancelInvite,
    refetch: fetchInvites,
  };
};
