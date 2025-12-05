import { motion } from 'framer-motion';
import { Calendar, Users, DollarSign, ChevronRight } from 'lucide-react';
import { formatDate } from '../utils/dateUtils';

export const InlineEventCard = ({ event, onAction }) => {
  const { id, name, date, icon, guests, budget, budgetSpent, progress } = event;

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="mt-3 mb-2 bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 shadow-sm transition-colors"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{icon || '🎉'}</span>
          <div>
            <h3 className="font-semibold text-lg text-gray-900 dark:text-dark-text-primary transition-colors">{name}</h3>
            <p className="text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">{formatDate(date)}</p>
          </div>
        </div>
      </div>

      {/* Quick Info */}
      <div className="flex gap-4 mb-3 text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">
        {guests && (
          <div className="flex items-center gap-1">
            <Users size={14} />
            <span>{guests} guests</span>
          </div>
        )}
        {budget && (
          <div className="flex items-center gap-1">
            <DollarSign size={14} />
            <span>
              ${budgetSpent?.toLocaleString() || 0} / ${budget.toLocaleString()}
            </span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {progress !== undefined && (
        <div className="mb-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-600 dark:text-dark-text-secondary transition-colors">Progress</span>
            <span className="text-xs font-medium text-gray-900 dark:text-dark-text-primary transition-colors">{progress}%</span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-dark-bg-tertiary rounded-full overflow-hidden transition-colors">
            <div
              className="h-full bg-blue-600 dark:bg-blue-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={() => onAction?.('view', event)}
          className="flex-1 py-2 px-3 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-lg text-sm font-medium hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
        >
          View Details
        </button>
        <button
          onClick={() => onAction?.('chat', event)}
          className="flex-1 py-2 px-3 border border-gray-200 dark:border-dark-bg-tertiary text-gray-700 dark:text-dark-text-primary rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-dark-bg-tertiary transition-colors"
        >
          Chat about it
        </button>
      </div>
    </motion.div>
  );
};
