import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

/**
 * StatCard - Statistics display card
 *
 * Props:
 * - icon: React component - Icon to display
 * - label: string - Stat label
 * - value: string|number - Stat value
 * - change: number - Percentage change (optional)
 * - trend: 'up' | 'down' | 'neutral' (optional)
 * - color: string - Accent color (default: 'blue')
 */

export const StatCard = ({
  icon: Icon,
  label,
  value,
  change,
  trend,
  color = 'blue',
}) => {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-100 dark:bg-blue-900/30',
      icon: 'text-blue-600 dark:text-blue-400',
      text: 'text-blue-700 dark:text-blue-400',
    },
    green: {
      bg: 'bg-green-100 dark:bg-green-900/30',
      icon: 'text-green-600 dark:text-green-400',
      text: 'text-green-700 dark:text-green-400',
    },
    purple: {
      bg: 'bg-purple-100 dark:bg-purple-900/30',
      icon: 'text-purple-600 dark:text-purple-400',
      text: 'text-purple-700 dark:text-purple-400',
    },
    orange: {
      bg: 'bg-orange-100 dark:bg-orange-900/30',
      icon: 'text-orange-600 dark:text-orange-400',
      text: 'text-orange-700 dark:text-orange-400',
    },
  };

  const colors = colorClasses[color] || colorClasses.blue;

  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp size={16} className="text-green-600 dark:text-green-400" />;
    if (trend === 'down') return <TrendingDown size={16} className="text-red-600 dark:text-red-400" />;
    return <Minus size={16} className="text-gray-400 dark:text-gray-600" />;
  };

  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600 dark:text-green-400';
    if (trend === 'down') return 'text-red-600 dark:text-red-400';
    return 'text-gray-600 dark:text-gray-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 transition-colors"
    >
      {/* Icon */}
      <div className={`w-12 h-12 ${colors.bg} rounded-lg flex items-center justify-center mb-3 transition-colors`}>
        {Icon && <Icon size={24} className={colors.icon} />}
      </div>

      {/* Value */}
      <div className="mb-1">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary transition-colors">
          {value}
        </h3>
      </div>

      {/* Label */}
      <p className="text-sm text-gray-600 dark:text-dark-text-secondary mb-2 transition-colors">
        {label}
      </p>

      {/* Change Indicator */}
      {change !== undefined && (
        <div className="flex items-center gap-1">
          {getTrendIcon()}
          <span className={`text-xs font-medium ${getTrendColor()} transition-colors`}>
            {change > 0 ? '+' : ''}{change}%
          </span>
          <span className="text-xs text-gray-500 dark:text-dark-text-tertiary transition-colors">
            vs last month
          </span>
        </div>
      )}
    </motion.div>
  );
};
