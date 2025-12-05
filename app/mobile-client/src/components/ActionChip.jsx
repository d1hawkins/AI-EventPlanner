import { motion } from 'framer-motion';

export const ActionChip = ({ icon, text, onClick, variant = 'default' }) => {
  const variants = {
    default: 'border-gray-300 dark:border-dark-bg-tertiary bg-white dark:bg-dark-bg-secondary text-gray-700 dark:text-dark-text-primary hover:bg-gray-50 dark:hover:bg-dark-bg-tertiary hover:border-blue-600 dark:hover:border-blue-500',
    primary: 'border-blue-600 dark:border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/50',
    success: 'border-green-600 dark:border-green-500 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/50',
  };

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`inline-flex items-center gap-2 px-4 py-2.5 border rounded-full text-sm font-medium transition-all ${variants[variant]}`}
    >
      {icon && <span className="text-base">{icon}</span>}
      <span>{text}</span>
    </motion.button>
  );
};

export const ActionChipGroup = ({ children }) => {
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {children}
    </div>
  );
};
