import { motion, AnimatePresence } from 'framer-motion';
import {
  Calendar,
  BarChart3,
  Settings,
  User,
  HelpCircle,
  LogOut,
  X,
  List,
} from 'lucide-react';
import { ThemeToggleButton } from './ThemeToggle';

export const SideMenu = ({ isOpen, onClose, onNavigate }) => {
  const menuItems = [
    { icon: List, label: 'All Events', action: 'events' },
    { icon: Calendar, label: 'Calendar View', action: 'calendar' },
    { icon: BarChart3, label: 'Analytics', action: 'analytics' },
    { icon: Settings, label: 'Settings', action: 'settings' },
    { icon: User, label: 'Profile', action: 'profile' },
    { icon: HelpCircle, label: 'Help', action: 'help' },
  ];

  const handleItemClick = (action) => {
    onNavigate?.(action);
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Menu */}
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ type: 'spring', damping: 25 }}
            className="fixed left-0 top-0 bottom-0 w-80 max-w-[85vw] bg-white dark:bg-dark-bg-primary z-50 shadow-2xl transition-colors"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-dark-bg-tertiary transition-colors">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary transition-colors">Menu</h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors text-gray-700 dark:text-dark-text-primary"
              >
                <X size={20} />
              </button>
            </div>

            {/* Menu Items */}
            <nav className="p-2">
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.action}
                    onClick={() => handleItemClick(item.action)}
                    className="w-full flex items-center gap-3 px-4 py-3 text-gray-700 dark:text-dark-text-primary hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </button>
                );
              })}

              {/* Theme Toggle */}
              <div className="px-2 py-2">
                <ThemeToggleButton showLabel={true} className="w-full justify-start" />
              </div>

              {/* Divider */}
              <div className="my-2 border-t border-gray-200 dark:border-dark-bg-tertiary transition-colors" />

              {/* Sign Out */}
              <button
                onClick={() => handleItemClick('logout')}
                className="w-full flex items-center gap-3 px-4 py-3 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
              >
                <LogOut size={20} />
                <span className="font-medium">Sign Out</span>
              </button>
            </nav>

            {/* Footer */}
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-dark-bg-tertiary bg-gray-50 dark:bg-dark-bg-secondary transition-colors">
              <p className="text-xs text-gray-500 dark:text-dark-text-tertiary text-center transition-colors">
                AI Event Planner v2.0
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
