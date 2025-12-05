import { motion } from 'framer-motion';
import { Calendar, Users, DollarSign, ChevronRight } from 'lucide-react';
import { formatDate } from '../utils/dateUtils';

export const InlineEventCard = ({ event, onAction }) => {
  const { id, name, date, icon, guests, budget, budgetSpent, progress } = event;

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="mt-3 mb-2 bg-white border border-gray-200 rounded-xl p-4 shadow-sm"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{icon || '🎉'}</span>
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{name}</h3>
            <p className="text-sm text-gray-600">{formatDate(date)}</p>
          </div>
        </div>
      </div>

      {/* Quick Info */}
      <div className="flex gap-4 mb-3 text-sm text-gray-600">
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
            <span className="text-xs text-gray-600">Progress</span>
            <span className="text-xs font-medium text-gray-900">{progress}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={() => onAction?.('view', event)}
          className="flex-1 py-2 px-3 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors"
        >
          View Details
        </button>
        <button
          onClick={() => onAction?.('chat', event)}
          className="flex-1 py-2 px-3 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
        >
          Chat about it
        </button>
      </div>
    </motion.div>
  );
};
