import { motion } from 'framer-motion';
import { Calendar, Users, DollarSign, ChevronRight, MoreVertical } from 'lucide-react';
import { useState } from 'react';

/**
 * EventListCard - Event card for list view
 *
 * Props:
 * - event: Event object
 * - onClick: Click handler
 * - onEdit: Edit handler (optional)
 * - onDelete: Delete handler (optional)
 */

export const EventListCard = ({ event, onClick, onEdit, onDelete }) => {
  const [showMenu, setShowMenu] = useState(false);

  const {
    id,
    name,
    date,
    icon = '🎉',
    status = 'draft',
    guests_count,
    budget,
    budget_spent,
    progress = 0,
  } = event;

  const statusColors = {
    draft: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
    active: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
    completed: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
    cancelled: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileTap={{ scale: 0.98 }}
      className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 mb-3 cursor-pointer transition-colors"
      onClick={() => onClick(event)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3 flex-1">
          <span className="text-3xl">{icon}</span>
          <div className="flex-1">
            <h3 className="font-semibold text-lg text-gray-900 dark:text-dark-text-primary transition-colors">
              {name}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <Calendar size={14} className="text-gray-500 dark:text-dark-text-tertiary" />
              <span className="text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">
                {formatDate(date)}
              </span>
            </div>
          </div>
        </div>

        {/* Status Badge */}
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status]} transition-colors`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Quick Info */}
      <div className="flex gap-4 mb-3 text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">
        {guests_count !== undefined && (
          <div className="flex items-center gap-1">
            <Users size={14} />
            <span>{guests_count} guests</span>
          </div>
        )}
        {budget && (
          <div className="flex items-center gap-1">
            <DollarSign size={14} />
            <span>
              {formatCurrency(budget_spent || 0)} / {formatCurrency(budget)}
            </span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {progress !== undefined && (
        <div className="mb-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-600 dark:text-dark-text-secondary transition-colors">
              Progress
            </span>
            <span className="text-xs font-medium text-gray-900 dark:text-dark-text-primary transition-colors">
              {progress}%
            </span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-dark-bg-tertiary rounded-full overflow-hidden transition-colors">
            <div
              className="h-full bg-blue-600 dark:bg-blue-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-dark-bg-tertiary transition-colors">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClick(event);
          }}
          className="text-sm font-medium text-primary dark:text-primary-light hover:underline transition-colors"
        >
          View Details
          <ChevronRight size={16} className="inline ml-1" />
        </button>

        {(onEdit || onDelete) && (
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="p-2 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
            >
              <MoreVertical size={18} className="text-gray-600 dark:text-dark-text-secondary" />
            </button>

            {showMenu && (
              <div className="absolute right-0 top-full mt-1 bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-lg shadow-lg z-10 min-w-[120px] transition-colors">
                {onEdit && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowMenu(false);
                      onEdit(event);
                    }}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary text-gray-700 dark:text-dark-text-primary transition-colors"
                  >
                    Edit
                  </button>
                )}
                {onDelete && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowMenu(false);
                      onDelete(event);
                    }}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition-colors"
                  >
                    Delete
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};
