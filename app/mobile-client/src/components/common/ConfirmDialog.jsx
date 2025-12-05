import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X } from 'lucide-react';
import { Button } from '../Button';

/**
 * ConfirmDialog - Confirmation modal dialog
 *
 * Props:
 * - open: boolean - Dialog open state
 * - onClose: function - Close handler
 * - onConfirm: function - Confirm handler
 * - title: string - Dialog title
 * - message: string - Dialog message
 * - confirmText: string - Confirm button text (default: 'Confirm')
 * - cancelText: string - Cancel button text (default: 'Cancel')
 * - confirmVariant: 'primary' | 'danger' (default: 'primary')
 * - icon: ReactNode - Optional custom icon
 * - loading: boolean - Show loading state on confirm button
 */

export const ConfirmDialog = ({
  open,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'primary',
  icon,
  loading = false,
}) => {
  const handleConfirm = async () => {
    await onConfirm();
    if (!loading) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-50"
          />

          {/* Dialog */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white dark:bg-dark-bg-secondary rounded-xl shadow-2xl max-w-md w-full p-6 transition-colors"
            >
              {/* Close Button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-1 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
              >
                <X size={20} className="text-gray-500 dark:text-dark-text-secondary" />
              </button>

              {/* Icon */}
              {icon !== undefined ? (
                icon
              ) : confirmVariant === 'danger' ? (
                <div className="w-12 h-12 bg-danger/10 dark:bg-danger/20 rounded-full flex items-center justify-center mb-4">
                  <AlertTriangle size={24} className="text-danger dark:text-red-400" />
                </div>
              ) : null}

              {/* Title */}
              <h3 className="text-xl font-semibold text-gray-900 dark:text-dark-text-primary mb-2 transition-colors">
                {title}
              </h3>

              {/* Message */}
              <p className="text-gray-600 dark:text-dark-text-secondary mb-6 transition-colors">
                {message}
              </p>

              {/* Actions */}
              <div className="flex gap-3">
                <Button
                  variant="secondary"
                  fullWidth
                  onClick={onClose}
                  disabled={loading}
                >
                  {cancelText}
                </Button>
                <Button
                  variant={confirmVariant}
                  fullWidth
                  onClick={handleConfirm}
                  disabled={loading}
                  loading={loading}
                >
                  {confirmText}
                </Button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
