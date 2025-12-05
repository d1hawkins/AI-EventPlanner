import { motion } from 'framer-motion';

export const ActionChip = ({ icon, text, onClick, variant = 'default' }) => {
  const variants = {
    default: 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-blue-600',
    primary: 'border-blue-600 bg-blue-50 text-blue-700 hover:bg-blue-100',
    success: 'border-green-600 bg-green-50 text-green-700 hover:bg-green-100',
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
