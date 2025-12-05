import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

/**
 * ThemeToggle - Button component for switching between light and dark themes
 *
 * Features:
 * - Animated sun/moon icon transition
 * - Smooth color transitions
 * - Touch-optimized for mobile
 * - Accessible with ARIA labels
 * - Multiple size variants
 */

export const ThemeToggle = ({ size = 'md', variant = 'default', className = '' }) => {
  const { theme, toggleTheme, isDark } = useTheme();

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24,
  };

  const variantClasses = {
    default: 'bg-gray-100 dark:bg-dark-bg-tertiary hover:bg-gray-200 dark:hover:bg-dark-bg-secondary',
    primary: 'bg-primary/10 dark:bg-primary/20 hover:bg-primary/20 dark:hover:bg-primary/30',
    ghost: 'bg-transparent hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary',
  };

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={toggleTheme}
      className={`
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        rounded-full
        flex items-center justify-center
        transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
        dark:focus:ring-offset-dark-bg-primary
        ${className}
      `}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <motion.div
        initial={false}
        animate={{
          scale: [0.8, 1.2, 1],
          rotate: isDark ? 180 : 0,
        }}
        transition={{ duration: 0.3 }}
      >
        {isDark ? (
          <Moon
            size={iconSizes[size]}
            className="text-yellow-300"
          />
        ) : (
          <Sun
            size={iconSizes[size]}
            className="text-yellow-500"
          />
        )}
      </motion.div>
    </motion.button>
  );
};

/**
 * ThemeToggleSwitch - Alternative switch-style theme toggle
 *
 * Features:
 * - iOS-style toggle switch
 * - Smooth sliding animation
 * - Shows both sun and moon icons
 */

export const ThemeToggleSwitch = ({ className = '' }) => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`
        relative w-16 h-8 rounded-full
        bg-gray-200 dark:bg-dark-bg-tertiary
        transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
        dark:focus:ring-offset-dark-bg-primary
        ${className}
      `}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {/* Background icons */}
      <div className="absolute inset-0 flex items-center justify-between px-2">
        <Sun size={14} className="text-yellow-500 opacity-50" />
        <Moon size={14} className="text-blue-300 opacity-50" />
      </div>

      {/* Sliding button */}
      <motion.div
        className="absolute top-1 left-1 w-6 h-6 bg-white dark:bg-dark-bg-primary rounded-full shadow-md flex items-center justify-center"
        animate={{
          x: isDark ? 32 : 0,
        }}
        transition={{
          type: 'spring',
          stiffness: 500,
          damping: 30,
        }}
      >
        {isDark ? (
          <Moon size={14} className="text-blue-400" />
        ) : (
          <Sun size={14} className="text-yellow-500" />
        )}
      </motion.div>
    </button>
  );
};

/**
 * ThemeToggleButton - Text button with icon
 */

export const ThemeToggleButton = ({ showLabel = true, className = '' }) => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`
        flex items-center gap-2 px-4 py-2 rounded-lg
        bg-gray-100 dark:bg-dark-bg-tertiary
        hover:bg-gray-200 dark:hover:bg-dark-bg-secondary
        text-gray-900 dark:text-dark-text-primary
        transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-primary
        ${className}
      `}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {isDark ? (
        <>
          <Moon size={18} className="text-blue-400" />
          {showLabel && <span className="text-sm font-medium">Dark Mode</span>}
        </>
      ) : (
        <>
          <Sun size={18} className="text-yellow-500" />
          {showLabel && <span className="text-sm font-medium">Light Mode</span>}
        </>
      )}
    </button>
  );
};
