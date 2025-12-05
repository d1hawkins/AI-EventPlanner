import { motion } from 'framer-motion';
import {
  Calendar,
  Users,
  DollarSign,
  CheckCircle,
  UserPlus,
  Edit,
  Trash2,
} from 'lucide-react';

/**
 * ActivityFeed - Recent activity list
 *
 * Props:
 * - activities: Array of activity objects
 * - loading: boolean
 * - limit: number - Max activities to show
 */

export const ActivityFeed = ({ activities = [], loading = false, limit }) => {
  const displayActivities = limit ? activities.slice(0, limit) : activities;

  const getActivityIcon = (type) => {
    const icons = {
      event_created: Calendar,
      event_updated: Edit,
      event_deleted: Trash2,
      task_completed: CheckCircle,
      member_joined: UserPlus,
      member_left: Users,
      budget_updated: DollarSign,
    };
    return icons[type] || Calendar;
  };

  const getActivityColor = (type) => {
    const colors = {
      event_created: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
      event_updated: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
      event_deleted: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
      task_completed: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
      member_joined: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
      member_left: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400',
      budget_updated: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
    };
    return colors[type] || colors.event_created;
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex items-start gap-3 animate-pulse">
            <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
            <div className="flex-1">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (displayActivities.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-dark-text-tertiary transition-colors">
        <p className="text-sm">No recent activity</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {displayActivities.map((activity, index) => {
        const Icon = getActivityIcon(activity.type);
        const colorClass = getActivityColor(activity.type);

        return (
          <motion.div
            key={activity.id || index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="flex items-start gap-3"
          >
            {/* Icon */}
            <div className={`w-10 h-10 ${colorClass} rounded-lg flex items-center justify-center flex-shrink-0 transition-colors`}>
              <Icon size={20} />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-900 dark:text-dark-text-primary transition-colors">
                {activity.message || activity.description}
              </p>
              <p className="text-xs text-gray-500 dark:text-dark-text-tertiary mt-1 transition-colors">
                {formatTime(activity.timestamp || activity.created_at)}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};
