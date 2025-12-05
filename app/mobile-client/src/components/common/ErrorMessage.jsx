import { AlertCircle, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '../Button';

/**
 * ErrorMessage - Display error messages with optional retry
 *
 * Props:
 * - title: string - Error title
 * - message: string - Error message
 * - retry: function - Optional retry callback
 * - retryText: string - Retry button text (default: 'Try Again')
 * - variant: 'default' | 'inline' | 'fullPage'
 */

export const ErrorMessage = ({
  title = 'Error',
  message = 'Something went wrong',
  retry,
  retryText = 'Try Again',
  variant = 'default',
}) => {
  const content = (
    <div className="flex flex-col items-center text-center">
      <div className="w-16 h-16 bg-danger/10 dark:bg-danger/20 rounded-full flex items-center justify-center mb-4 transition-colors">
        <AlertCircle size={32} className="text-danger dark:text-red-400" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary mb-2 transition-colors">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-dark-text-secondary mb-4 transition-colors max-w-md">
        {message}
      </p>
      {retry && (
        <Button
          variant="primary"
          icon={<RefreshCw size={18} />}
          onClick={retry}
        >
          {retryText}
        </Button>
      )}
    </div>
  );

  if (variant === 'fullPage') {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white dark:bg-dark-bg-primary p-4 transition-colors">
        {content}
      </div>
    );
  }

  if (variant === 'inline') {
    return (
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900/40 rounded-lg p-4 mb-4 transition-colors"
      >
        <div className="flex gap-3">
          <AlertCircle size={20} className="text-danger dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-red-900 dark:text-red-300 mb-1">{title}</h4>
            <p className="text-sm text-red-700 dark:text-red-400">{message}</p>
            {retry && (
              <button
                onClick={retry}
                className="mt-2 text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 flex items-center gap-1"
              >
                <RefreshCw size={14} />
                {retryText}
              </button>
            )}
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="p-8"
    >
      {content}
    </motion.div>
  );
};
