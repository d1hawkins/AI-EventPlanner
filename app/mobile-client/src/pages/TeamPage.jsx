import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, UserPlus, Users, Search, Mail, Clock } from 'lucide-react';
import { useTeam, usePendingInvites } from '../hooks/useTeam';
import { TeamMemberCard } from '../components/team/TeamMemberCard';
import { InviteForm } from '../components/team/InviteForm';
import { RoleSelector } from '../components/team/RoleSelector';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { EmptyState } from '../components/common/EmptyState';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { useToast } from '../hooks/useToast';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * TeamPage - Team management page
 *
 * Features:
 * - View all team members
 * - Invite new members
 * - Update member roles
 * - Remove members
 * - View pending invitations
 * - Search members
 */

export const TeamPage = () => {
  const navigate = useNavigate();
  const toast = useToast();

  const { members, currentUserRole, loading, error, inviteMember, updateRole, removeMember, refetch } = useTeam();
  const { invites, loading: invitesLoading, cancelInvite, resendInvite } = usePendingInvites();

  const [searchTerm, setSearchTerm] = useState('');
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteLoading, setInviteLoading] = useState(false);
  const [memberToRemove, setMemberToRemove] = useState(null);
  const [removeLoading, setRemoveLoading] = useState(false);
  const [memberToUpdateRole, setMemberToUpdateRole] = useState(null);
  const [selectedRole, setSelectedRole] = useState('');
  const [roleUpdateLoading, setRoleUpdateLoading] = useState(false);
  const [showInvites, setShowInvites] = useState(false);

  // Filter members by search
  const filteredMembers = members.filter((member) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      member.name.toLowerCase().includes(searchLower) ||
      member.email.toLowerCase().includes(searchLower) ||
      member.role.toLowerCase().includes(searchLower)
    );
  });

  // Group members by role
  const membersByRole = {
    owner: filteredMembers.filter((m) => m.role === 'owner'),
    admin: filteredMembers.filter((m) => m.role === 'admin'),
    member: filteredMembers.filter((m) => m.role === 'member'),
  };

  const handleInvite = async ({ email, role }) => {
    try {
      setInviteLoading(true);
      await inviteMember({ email, role });
      toast.success(`Invitation sent to ${email}`);
      setShowInviteForm(false);
    } catch (err) {
      toast.error(err.message || 'Failed to send invitation');
    } finally {
      setInviteLoading(false);
    }
  };

  const handleRemoveMember = async () => {
    if (!memberToRemove) return;

    try {
      setRemoveLoading(true);
      await removeMember(memberToRemove.id);
      toast.success(`${memberToRemove.name} has been removed from the team`);
      setMemberToRemove(null);
    } catch (err) {
      toast.error(err.message || 'Failed to remove member');
    } finally {
      setRemoveLoading(false);
    }
  };

  const handleUpdateRole = async () => {
    if (!memberToUpdateRole || !selectedRole) return;

    try {
      setRoleUpdateLoading(true);
      await updateRole(memberToUpdateRole.id, selectedRole);
      toast.success(`${memberToUpdateRole.name}'s role updated to ${selectedRole}`);
      setMemberToUpdateRole(null);
      setSelectedRole('');
    } catch (err) {
      toast.error(err.message || 'Failed to update role');
    } finally {
      setRoleUpdateLoading(false);
    }
  };

  const handleCancelInvite = async (inviteId) => {
    try {
      await cancelInvite(inviteId);
      toast.success('Invitation cancelled');
    } catch (err) {
      toast.error(err.message || 'Failed to cancel invitation');
    }
  };

  const handleResendInvite = async (inviteId) => {
    try {
      await resendInvite(inviteId);
      toast.success('Invitation resent');
    } catch (err) {
      toast.error(err.message || 'Failed to resend invitation');
    }
  };

  if (loading) {
    return <LoadingSpinner fullPage message="Loading team..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        variant="fullPage"
        title="Failed to load team"
        message={error}
        retry={refetch}
      />
    );
  }

  const canInvite = currentUserRole === 'owner' || currentUserRole === 'admin';

  return (
    <div className="min-h-screen bg-gray-bg dark:bg-dark-bg-primary pb-20 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-dark-bg-secondary border-b border-gray-200 dark:border-dark-bg-tertiary px-4 py-4 sticky top-0 z-10 transition-colors">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft size={24} className="text-gray-700 dark:text-dark-text-primary" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary transition-colors">
                Team
              </h1>
              <p className="text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">
                {members.length} {members.length === 1 ? 'member' : 'members'}
              </p>
            </div>
          </div>

          {canInvite && (
            <button
              onClick={() => setShowInviteForm(true)}
              className="p-2 bg-primary hover:bg-primary-dark text-white rounded-lg transition-colors"
              aria-label="Invite member"
            >
              <UserPlus size={20} />
            </button>
          )}
        </div>

        {/* Search */}
        <div className="relative">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <Search size={18} className="text-gray-400 dark:text-dark-text-tertiary" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search members..."
            className="w-full pl-10 pr-4 py-2.5 bg-gray-50 dark:bg-dark-bg-tertiary border border-gray-200 dark:border-dark-bg-tertiary rounded-lg text-gray-900 dark:text-dark-text-primary placeholder:text-gray-500 dark:placeholder:text-dark-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary focus:border-transparent transition-colors"
          />
        </div>

        {/* Pending Invites Toggle */}
        {invites.length > 0 && (
          <button
            onClick={() => setShowInvites(!showInvites)}
            className="w-full mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-900/40 rounded-lg flex items-center justify-between transition-colors"
          >
            <div className="flex items-center gap-2">
              <Mail size={18} className="text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-blue-900 dark:text-blue-300">
                {invites.length} pending {invites.length === 1 ? 'invitation' : 'invitations'}
              </span>
            </div>
            <span className="text-blue-600 dark:text-blue-400 text-xs">
              {showInvites ? 'Hide' : 'Show'}
            </span>
          </button>
        )}
      </header>

      {/* Content */}
      <div className="px-4 py-6 space-y-6">
        {/* Pending Invitations */}
        <AnimatePresence>
          {showInvites && invites.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary">
                Pending Invitations
              </h2>
              {invites.map((invite) => (
                <div
                  key={invite.id}
                  className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Mail size={16} className="text-gray-400 dark:text-dark-text-tertiary" />
                        <span className="font-medium text-gray-900 dark:text-dark-text-primary">
                          {invite.email}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-600 dark:text-dark-text-secondary">
                        <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">
                          {invite.role}
                        </span>
                        <div className="flex items-center gap-1">
                          <Clock size={12} />
                          <span>Invited {new Date(invite.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleResendInvite(invite.id)}
                        className="text-xs text-primary dark:text-primary-light hover:underline"
                      >
                        Resend
                      </button>
                      <button
                        onClick={() => handleCancelInvite(invite.id)}
                        className="text-xs text-red-600 dark:text-red-400 hover:underline"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Members List */}
        {filteredMembers.length === 0 ? (
          <EmptyState
            icon="👥"
            title={searchTerm ? 'No members found' : 'No team members yet'}
            message={
              searchTerm
                ? 'Try adjusting your search terms'
                : 'Invite team members to start collaborating'
            }
            action={canInvite && !searchTerm ? 'Invite Member' : null}
            onAction={() => setShowInviteForm(true)}
          />
        ) : (
          <div className="space-y-6">
            {/* Owners */}
            {membersByRole.owner.length > 0 && (
              <div>
                <h2 className="text-sm font-semibold text-gray-500 dark:text-dark-text-tertiary uppercase tracking-wide mb-3">
                  Owners ({membersByRole.owner.length})
                </h2>
                <div className="space-y-3">
                  {membersByRole.owner.map((member) => (
                    <TeamMemberCard
                      key={member.id}
                      member={member}
                      currentUserRole={currentUserRole}
                      onUpdateRole={(m) => {
                        setMemberToUpdateRole(m);
                        setSelectedRole(m.role);
                      }}
                      onRemove={(m) => setMemberToRemove(m)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Admins */}
            {membersByRole.admin.length > 0 && (
              <div>
                <h2 className="text-sm font-semibold text-gray-500 dark:text-dark-text-tertiary uppercase tracking-wide mb-3">
                  Admins ({membersByRole.admin.length})
                </h2>
                <div className="space-y-3">
                  {membersByRole.admin.map((member) => (
                    <TeamMemberCard
                      key={member.id}
                      member={member}
                      currentUserRole={currentUserRole}
                      onUpdateRole={(m) => {
                        setMemberToUpdateRole(m);
                        setSelectedRole(m.role);
                      }}
                      onRemove={(m) => setMemberToRemove(m)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Members */}
            {membersByRole.member.length > 0 && (
              <div>
                <h2 className="text-sm font-semibold text-gray-500 dark:text-dark-text-tertiary uppercase tracking-wide mb-3">
                  Members ({membersByRole.member.length})
                </h2>
                <div className="space-y-3">
                  {membersByRole.member.map((member) => (
                    <TeamMemberCard
                      key={member.id}
                      member={member}
                      currentUserRole={currentUserRole}
                      onUpdateRole={(m) => {
                        setMemberToUpdateRole(m);
                        setSelectedRole(m.role);
                      }}
                      onRemove={(m) => setMemberToRemove(m)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Invite Form Modal */}
      <AnimatePresence>
        {showInviteForm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-4"
            onClick={() => !inviteLoading && setShowInviteForm(false)}
          >
            <motion.div
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              className="bg-white dark:bg-dark-bg-secondary rounded-t-2xl sm:rounded-2xl p-6 w-full max-w-md transition-colors"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-xl font-bold text-gray-900 dark:text-dark-text-primary mb-4">
                Invite Team Member
              </h2>
              <InviteForm
                onSubmit={handleInvite}
                onCancel={() => setShowInviteForm(false)}
                loading={inviteLoading}
                currentUserRole={currentUserRole}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Role Update Modal */}
      <AnimatePresence>
        {memberToUpdateRole && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-4"
            onClick={() => !roleUpdateLoading && setMemberToUpdateRole(null)}
          >
            <motion.div
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              className="bg-white dark:bg-dark-bg-secondary rounded-t-2xl sm:rounded-2xl p-6 w-full max-w-lg transition-colors max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
                Change Role
              </h2>
              <p className="text-sm text-gray-600 dark:text-dark-text-secondary mb-4">
                Update role for {memberToUpdateRole.name}
              </p>

              <RoleSelector
                currentRole={memberToUpdateRole.role}
                selectedRole={selectedRole}
                onChange={setSelectedRole}
                disabled={currentUserRole === 'admin' ? ['owner'] : []}
              />

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setMemberToUpdateRole(null)}
                  disabled={roleUpdateLoading}
                  className="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-dark-bg-tertiary text-gray-700 dark:text-dark-text-primary rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateRole}
                  disabled={roleUpdateLoading || selectedRole === memberToUpdateRole.role}
                  className="flex-1 px-4 py-2.5 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {roleUpdateLoading ? 'Updating...' : 'Update Role'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Remove Confirmation */}
      <ConfirmDialog
        open={!!memberToRemove}
        onClose={() => !removeLoading && setMemberToRemove(null)}
        onConfirm={handleRemoveMember}
        title="Remove Team Member"
        message={
          memberToRemove
            ? `Are you sure you want to remove ${memberToRemove.name} from the team? They will lose access to all events and data.`
            : ''
        }
        confirmText="Remove"
        confirmVariant="danger"
        loading={removeLoading}
      />
    </div>
  );
};
