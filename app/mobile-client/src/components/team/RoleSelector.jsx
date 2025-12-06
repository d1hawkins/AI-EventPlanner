import { Shield, User, Crown, Info } from 'lucide-react';
import { motion } from 'framer-motion';

/**
 * RoleSelector - Role selection component
 *
 * Props:
 * - currentRole: string - Current role of the member
 * - selectedRole: string - Currently selected role
 * - onChange: function - Role change handler
 * - disabled: array - Roles that cannot be selected
 */

export const RoleSelector = ({
  currentRole,
  selectedRole,
  onChange,
  disabled = [],
}) => {
  const roles = [
    {
      value: 'owner',
      label: 'Owner',
      icon: Crown,
      color: 'purple',
      description: 'Full access to all features, billing, and team management',
      permissions: ['Manage billing', 'Delete workspace', 'Manage all members', 'Full event access'],
    },
    {
      value: 'admin',
      label: 'Admin',
      icon: Shield,
      color: 'blue',
      description: 'Can manage events, team members, and most settings',
      permissions: ['Manage events', 'Invite members', 'Manage member roles', 'View analytics'],
    },
    {
      value: 'member',
      label: 'Member',
      icon: User,
      color: 'gray',
      description: 'Can create and manage their own events',
      permissions: ['Create events', 'Edit own events', 'View team events', 'Comment and collaborate'],
    },
  ];

  const colorClasses = {
    purple: {
      border: 'border-purple-500 dark:border-purple-400',
      bg: 'bg-purple-50 dark:bg-purple-900/20',
      icon: 'text-purple-600 dark:text-purple-400',
      text: 'text-purple-700 dark:text-purple-400',
    },
    blue: {
      border: 'border-blue-500 dark:border-blue-400',
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      icon: 'text-blue-600 dark:text-blue-400',
      text: 'text-blue-700 dark:text-blue-400',
    },
    gray: {
      border: 'border-gray-300 dark:border-gray-600',
      bg: 'bg-gray-50 dark:bg-gray-800',
      icon: 'text-gray-600 dark:text-gray-400',
      text: 'text-gray-700 dark:text-gray-400',
    },
  };

  return (
    <div className="space-y-3">
      {roles.map((role) => {
        const RoleIcon = role.icon;
        const colors = colorClasses[role.color];
        const isSelected = selectedRole === role.value;
        const isDisabled = disabled.includes(role.value);
        const isCurrent = currentRole === role.value;

        return (
          <motion.button
            key={role.value}
            type="button"
            onClick={() => !isDisabled && onChange(role.value)}
            disabled={isDisabled}
            whileTap={!isDisabled ? { scale: 0.98 } : {}}
            className={`
              w-full text-left p-4 rounded-xl border-2 transition-all
              ${isSelected
                ? `${colors.border} ${colors.bg}`
                : 'border-gray-200 dark:border-dark-bg-tertiary bg-white dark:bg-dark-bg-secondary'
              }
              ${isDisabled
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:border-primary dark:hover:border-primary-light cursor-pointer'
              }
            `}
          >
            <div className="flex items-start gap-3">
              {/* Icon */}
              <div className={`
                flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center
                ${isSelected ? colors.bg : 'bg-gray-100 dark:bg-dark-bg-tertiary'}
              `}>
                <RoleIcon
                  size={20}
                  className={isSelected ? colors.icon : 'text-gray-600 dark:text-dark-text-secondary'}
                />
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className={`
                    font-semibold text-base
                    ${isSelected ? colors.text : 'text-gray-900 dark:text-dark-text-primary'}
                  `}>
                    {role.label}
                  </h4>
                  {isCurrent && (
                    <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium rounded">
                      Current
                    </span>
                  )}
                </div>

                <p className="text-sm text-gray-600 dark:text-dark-text-secondary mb-2">
                  {role.description}
                </p>

                {/* Permissions */}
                <div className="space-y-1">
                  {role.permissions.map((permission, index) => (
                    <div key={index} className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-dark-text-tertiary">
                      <div className={`w-1 h-1 rounded-full ${isSelected ? colors.icon.replace('text-', 'bg-') : 'bg-gray-400 dark:bg-gray-600'}`} />
                      <span>{permission}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Selection Indicator */}
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`flex-shrink-0 w-6 h-6 rounded-full ${colors.bg} flex items-center justify-center`}
                >
                  <div className={`w-3 h-3 rounded-full ${colors.icon.replace('text-', 'bg-')}`} />
                </motion.div>
              )}
            </div>
          </motion.button>
        );
      })}

      {/* Info Note */}
      <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-900/40 rounded-lg">
        <Info size={16} className="text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-blue-900 dark:text-blue-300">
          Changing a member's role will immediately update their permissions. This action cannot be undone automatically.
        </p>
      </div>
    </div>
  );
};
