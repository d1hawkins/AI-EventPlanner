import { useState } from 'react';
import { Mail, Shield, User, Crown } from 'lucide-react';
import { Button } from '../Button';

/**
 * InviteForm - Team member invitation form
 *
 * Props:
 * - onSubmit: function - Submit handler (receives { email, role })
 * - onCancel: function - Cancel handler
 * - loading: boolean - Loading state
 * - currentUserRole: string - Role of current user (to limit role options)
 */

export const InviteForm = ({ onSubmit, onCancel, loading = false, currentUserRole = 'member' }) => {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('member');
  const [error, setError] = useState('');

  const roles = [
    {
      value: 'owner',
      label: 'Owner',
      icon: Crown,
      color: 'purple',
      description: 'Full access to everything',
      availableFor: ['owner'],
    },
    {
      value: 'admin',
      label: 'Admin',
      icon: Shield,
      color: 'blue',
      description: 'Manage events and team',
      availableFor: ['owner', 'admin'],
    },
    {
      value: 'member',
      label: 'Member',
      icon: User,
      color: 'gray',
      description: 'Create and manage events',
      availableFor: ['owner', 'admin', 'member'],
    },
  ];

  const availableRoles = roles.filter((r) => r.availableFor.includes(currentUserRole));

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    onSubmit({ email: email.trim(), role });
  };

  const colorClasses = {
    purple: 'text-purple-600 dark:text-purple-400',
    blue: 'text-blue-600 dark:text-blue-400',
    gray: 'text-gray-600 dark:text-gray-400',
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Email Input */}
      <div>
        <label htmlFor="invite-email" className="block text-sm font-medium text-gray-700 dark:text-dark-text-primary mb-2">
          Email Address
        </label>
        <div className="relative">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <Mail size={18} className="text-gray-400 dark:text-dark-text-tertiary" />
          </div>
          <input
            id="invite-email"
            type="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setError('');
            }}
            placeholder="colleague@example.com"
            className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-dark-bg-tertiary border border-gray-200 dark:border-dark-bg-tertiary rounded-lg text-gray-900 dark:text-dark-text-primary placeholder:text-gray-500 dark:placeholder:text-dark-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary focus:border-transparent transition-colors"
            disabled={loading}
          />
        </div>
        {error && (
          <p className="text-sm text-red-600 dark:text-red-400 mt-1">{error}</p>
        )}
      </div>

      {/* Role Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-dark-text-primary mb-2">
          Role
        </label>
        <div className="space-y-2">
          {availableRoles.map((roleOption) => {
            const RoleIcon = roleOption.icon;
            const isSelected = role === roleOption.value;

            return (
              <button
                key={roleOption.value}
                type="button"
                onClick={() => setRole(roleOption.value)}
                className={`
                  w-full text-left p-3 rounded-lg border transition-all
                  ${isSelected
                    ? 'border-primary dark:border-primary-light bg-primary/5 dark:bg-primary/10'
                    : 'border-gray-200 dark:border-dark-bg-tertiary bg-white dark:bg-dark-bg-tertiary hover:border-gray-300 dark:hover:border-gray-600'
                  }
                `}
                disabled={loading}
              >
                <div className="flex items-center gap-3">
                  <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${isSelected ? 'bg-primary/10 dark:bg-primary/20' : 'bg-gray-100 dark:bg-dark-bg-secondary'}`}>
                    <RoleIcon
                      size={18}
                      className={isSelected ? 'text-primary dark:text-primary-light' : colorClasses[roleOption.color]}
                    />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-sm text-gray-900 dark:text-dark-text-primary">
                      {roleOption.label}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-dark-text-secondary">
                      {roleOption.description}
                    </div>
                  </div>
                  {isSelected && (
                    <div className="flex-shrink-0 w-5 h-5 rounded-full bg-primary dark:bg-primary-light flex items-center justify-center">
                      <div className="w-2 h-2 rounded-full bg-white" />
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Info Note */}
      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-900/40 rounded-lg">
        <p className="text-xs text-blue-900 dark:text-blue-300">
          An invitation email will be sent to this address. They'll need to accept the invitation to join your team.
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={loading}
          fullWidth
        >
          Cancel
        </Button>
        <Button
          type="submit"
          variant="primary"
          loading={loading}
          disabled={loading}
          fullWidth
        >
          Send Invitation
        </Button>
      </div>
    </form>
  );
};
