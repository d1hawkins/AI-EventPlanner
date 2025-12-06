import { motion } from 'framer-motion';
import { Calendar, Users, HardDrive, AlertCircle } from 'lucide-react';

/**
 * UsageCard - Usage metrics display card
 *
 * Props:
 * - usage: Usage object with current and limit values
 * - type: 'events' | 'team_members' | 'storage'
 * - label: string - Display label
 */

export const UsageCard = ({ usage, type, label }) => {
  const { current = 0, limit = 0 } = usage;

  const icons = {
    events: Calendar,
    team_members: Users,
    storage: HardDrive,
  };

  const Icon = icons[type] || Calendar;
  const isUnlimited = limit === -1;
  const percentage = isUnlimited ? 0 : (current / limit) * 100;
  const isNearLimit = percentage >= 80 && !isUnlimited;
  const isAtLimit = percentage >= 100 && !isUnlimited;

  const getStatusColor = () => {
    if (isAtLimit) return 'text-red-600 dark:text-red-400';
    if (isNearLimit) return 'text-orange-600 dark:text-orange-400';
    return 'text-green-600 dark:text-green-400';
  };

  const getProgressColor = () => {
    if (isAtLimit) return 'bg-red-600 dark:bg-red-500';
    if (isNearLimit) return 'bg-orange-600 dark:bg-orange-500';
    return 'bg-blue-600 dark:bg-blue-500';
  };

  const formatValue = (value) => {
    if (type === 'storage') {
      return `${value}GB`;
    }
    return value;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 transition-colors"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gray-100 dark:bg-dark-bg-tertiary rounded-lg flex items-center justify-center">
            <Icon size={20} className="text-gray-600 dark:text-dark-text-secondary" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-dark-text-primary">
              {label}
            </h3>
          </div>
        </div>

        {/* Warning Icon */}
        {isNearLimit && !isAtLimit && (
          <AlertCircle size={18} className="text-orange-600 dark:text-orange-400" />
        )}
        {isAtLimit && (
          <AlertCircle size={18} className="text-red-600 dark:text-red-400" />
        )}
      </div>

      {/* Usage Stats */}
      <div className="mb-3">
        <div className="flex items-baseline gap-1">
          <span className={`text-2xl font-bold ${getStatusColor()}`}>
            {formatValue(current)}
          </span>
          <span className="text-gray-600 dark:text-dark-text-secondary text-sm">
            / {isUnlimited ? 'Unlimited' : formatValue(limit)}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      {!isUnlimited && (
        <div>
          <div className="h-2 bg-gray-100 dark:bg-dark-bg-tertiary rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(percentage, 100)}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className={`h-full ${getProgressColor()} rounded-full`}
            />
          </div>

          {/* Status Message */}
          <div className="mt-2">
            {isAtLimit && (
              <p className="text-xs text-red-600 dark:text-red-400 font-medium">
                Limit reached - Upgrade to continue
              </p>
            )}
            {isNearLimit && !isAtLimit && (
              <p className="text-xs text-orange-600 dark:text-orange-400 font-medium">
                {Math.round(100 - percentage)}% remaining
              </p>
            )}
            {!isNearLimit && (
              <p className="text-xs text-gray-500 dark:text-dark-text-tertiary">
                {Math.round(100 - percentage)}% available
              </p>
            )}
          </div>
        </div>
      )}

      {/* Unlimited Badge */}
      {isUnlimited && (
        <div className="mt-2">
          <span className="inline-flex items-center px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded">
            Unlimited
          </span>
        </div>
      )}
    </motion.div>
  );
};
