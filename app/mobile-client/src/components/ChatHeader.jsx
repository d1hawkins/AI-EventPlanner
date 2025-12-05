import { Menu } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const ChatHeader = ({ onMenuClick }) => {
  const [isVisible, setIsVisible] = useState(true);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.header
          initial={{ y: 0 }}
          exit={{ y: -100 }}
          className="sticky top-0 z-10 bg-white/95 backdrop-blur-sm border-b border-gray-200 px-4 py-3"
        >
          <div className="flex items-center justify-between">
            <button
              onClick={onMenuClick}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Open menu"
            >
              <Menu size={24} className="text-gray-700" />
            </button>

            <h1 className="text-lg font-semibold text-gray-900">AI Event Planner</h1>

            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white text-sm font-semibold">AI</span>
            </div>
          </div>
        </motion.header>
      )}
    </AnimatePresence>
  );
};
