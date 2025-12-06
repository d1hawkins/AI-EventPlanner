import { motion } from 'framer-motion';
import { Button } from '../Button';

/**
 * EmptyState - Display when no data is available
 *
 * Props:
 * - icon: string | ReactNode - Icon or emoji to display
 * - title: string - Empty state title
 * - message: string - Empty state message
 * - action: string - Action button text (optional)
 * - onAction: function - Action button callback (optional)
 * - variant: 'default' | 'compact'
 */

export const EmptyState = ({
  icon = '📭',
  title = 'No data',
  message = 'There is nothing to show here yet',
  action,
  onAction,
  variant = 'default',
}) => {
  const isCompact = variant === 'compact';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex flex-col items-center text-center ${isCompact ? 'p-6' : 'p-12'}`}
    >
      {/* Icon */}
      <div className={`${isCompact ? 'text-4xl mb-3' : 'text-6xl mb-6'}`}>
        {typeof icon === 'string' ? icon : icon}
      </div>

      {/* Title */}
      <h3
        className={`font-semibold text-gray-900 dark:text-dark-text-primary mb-2 transition-colors ${
          isCompact ? 'text-base' : 'text-lg'
        }`}
      >
        {title}
      </h3>

      {/* Message */}
      <p
        className={`text-gray-600 dark:text-dark-text-secondary transition-colors max-w-md ${
          isCompact ? 'text-sm mb-3' : 'text-base mb-6'
        }`}
      >
        {message}
      </p>

      {/* Action Button */}
      {action && onAction && (
        <Button
          variant="primary"
          size={isCompact ? 'sm' : 'md'}
          onClick={onAction}
        >
          {action}
        </Button>
      )}
    </motion.div>
  );
};

/**
 * EmptySearchState - Empty state specifically for search results
 */
export const EmptySearchState = ({ searchTerm, onClear }) => {
  return (
    <EmptyState
      icon="🔍"
      title="No results found"
      message={`No results found for "${searchTerm}". Try a different search term.`}
      action="Clear Search"
      onAction={onClear}
    />
  );
};

/**
 * EmptyFilterState - Empty state for filtered results
 */
export const EmptyFilterState = ({ onClear }) => {
  return (
    <EmptyState
      icon="🎯"
      title="No matches"
      message="No items match your current filters. Try adjusting your filters."
      action="Clear Filters"
      onAction={onClear}
    />
  );
};
