import { Menu } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ThemeToggle } from './ThemeToggle';

export const ChatHeader = ({ onMenuClick }) => {
  const [isVisible, setIsVisible] = useState(true);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.header
          initial={{ y: 0 }}
          exit={{ y: -100 }}
          className="sticky top-0 z-10 bg-white/95 dark:bg-dark-bg-primary/95 backdrop-blur-sm border-b border-gray-200 dark:border-dark-bg-tertiary px-4 py-3 transition-colors duration-200"
        >
          <div className="flex items-center justify-between">
            <button
              onClick={onMenuClick}
              className="p-2 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
              aria-label="Open menu"
            >
              <Menu size={24} className="text-gray-700 dark:text-dark-text-primary" />
            </button>

            <h1 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary transition-colors">AI Event Planner</h1>

            <div className="flex items-center gap-2">
              <ThemeToggle size="sm" variant="ghost" />

              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-sm">
                <span className="text-white text-sm font-semibold">AI</span>
              </div>
            </div>
          </div>
        </motion.header>
      )}
    </AnimatePresence>
  );
};
