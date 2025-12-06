import { motion } from 'framer-motion';
import { MoreVertical, Mail, Shield, User, Crown } from 'lucide-react';
import { useState } from 'react';

/**
 * TeamMemberCard - Team member display card
 *
 * Props:
 * - member: Member object
 * - currentUserRole: string - Role of current user
 * - onUpdateRole: function - Role update handler (optional)
 * - onRemove: function - Remove handler (optional)
 */

export const TeamMemberCard = ({ member, currentUserRole, onUpdateRole, onRemove }) => {
  const [showMenu, setShowMenu] = useState(false);

  const {
    id,
    name,
    email,
    role = 'member',
    avatar,
    status = 'active',
    joined_date,
  } = member;

  const roleConfig = {
    owner: {
      label: 'Owner',
      icon: Crown,
      color: 'text-purple-600 dark:text-purple-400',
      bg: 'bg-purple-100 dark:bg-purple-900/30',
      badge: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400',
    },
    admin: {
      label: 'Admin',
      icon: Shield,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-100 dark:bg-blue-900/30',
      badge: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
    },
    member: {
      label: 'Member',
      icon: User,
      color: 'text-gray-600 dark:text-gray-400',
      bg: 'bg-gray-100 dark:bg-gray-700',
      badge: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
    },
  };

  const config = roleConfig[role] || roleConfig.member;
  const RoleIcon = config.icon;

  const statusColors = {
    active: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
    invited: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
    inactive: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  };

  const canModify = () => {
    // Owner can modify anyone except other owners
    if (currentUserRole === 'owner' && role !== 'owner') return true;
    // Admin can modify members only
    if (currentUserRole === 'admin' && role === 'member') return true;
    return false;
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 transition-colors"
    >
      <div className="flex items-start gap-3">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {avatar ? (
            <img
              src={avatar}
              alt={name}
              className="w-12 h-12 rounded-full object-cover"
            />
          ) : (
            <div className={`w-12 h-12 ${config.bg} rounded-full flex items-center justify-center transition-colors`}>
              <span className={`text-sm font-semibold ${config.color}`}>
                {getInitials(name)}
              </span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-base text-gray-900 dark:text-dark-text-primary truncate transition-colors">
                {name}
              </h3>
              <div className="flex items-center gap-1.5 text-sm text-gray-600 dark:text-dark-text-secondary mt-0.5">
                <Mail size={14} />
                <span className="truncate">{email}</span>
              </div>
            </div>

            {/* Actions Menu */}
            {canModify() && (onUpdateRole || onRemove) && (
              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowMenu(!showMenu);
                  }}
                  className="p-1.5 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
                  aria-label="Member actions"
                >
                  <MoreVertical size={18} className="text-gray-600 dark:text-dark-text-secondary" />
                </button>

                {showMenu && (
                  <div className="absolute right-0 top-full mt-1 bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-lg shadow-lg z-10 min-w-[140px] transition-colors">
                    {onUpdateRole && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowMenu(false);
                          onUpdateRole(member);
                        }}
                        className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary text-gray-700 dark:text-dark-text-primary transition-colors"
                      >
                        Change Role
                      </button>
                    )}
                    {onRemove && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowMenu(false);
                          onRemove(member);
                        }}
                        className="w-full text-left px-4 py-2 text-sm hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition-colors rounded-b-lg"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Role & Status Badges */}
          <div className="flex items-center gap-2 mt-2">
            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.badge} transition-colors`}>
              <RoleIcon size={12} />
              {config.label}
            </span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status]} transition-colors`}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
          </div>

          {/* Joined Date */}
          {joined_date && (
            <p className="text-xs text-gray-500 dark:text-dark-text-tertiary mt-2 transition-colors">
              Joined {formatDate(joined_date)}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
};
