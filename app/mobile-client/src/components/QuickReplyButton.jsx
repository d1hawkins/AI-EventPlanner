import { motion } from 'framer-motion';

export const QuickReplyButton = ({ text, icon, onClick }) => {
  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className="w-full px-4 py-3 bg-white border-2 border-primary text-primary rounded-lg text-left font-medium text-sm flex items-center gap-2 hover:bg-gray-50 transition-colors"
    >
      {icon && <span>{icon}</span>}
      {text}
    </motion.button>
  );
};
