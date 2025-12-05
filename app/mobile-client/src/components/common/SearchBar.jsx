import { useState, useRef, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * SearchBar - Search input with clear button
 *
 * Props:
 * - value: string - Controlled value
 * - onChange: function - Change handler
 * - placeholder: string - Placeholder text
 * - onSearch: function - Optional search callback (triggered on Enter)
 * - autoFocus: boolean - Auto focus on mount
 * - debounce: number - Debounce delay in ms (default: 300)
 */

export const SearchBar = ({
  value,
  onChange,
  placeholder = 'Search...',
  onSearch,
  autoFocus = false,
  debounce = 300,
}) => {
  const [localValue, setLocalValue] = useState(value);
  const inputRef = useRef(null);
  const debounceTimeout = useRef(null);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  const handleChange = (e) => {
    const newValue = e.target.value;
    setLocalValue(newValue);

    // Clear existing timeout
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    // Set new timeout
    debounceTimeout.current = setTimeout(() => {
      onChange(newValue);
    }, debounce);
  };

  const handleClear = () => {
    setLocalValue('');
    onChange('');
    inputRef.current?.focus();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && onSearch) {
      onSearch(localValue);
    }
  };

  return (
    <div className="relative">
      {/* Search Icon */}
      <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <Search size={18} className="text-gray-400 dark:text-dark-text-tertiary" />
      </div>

      {/* Input */}
      <input
        ref={inputRef}
        type="text"
        value={localValue}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        className="w-full pl-10 pr-10 py-2.5 bg-gray-50 dark:bg-dark-bg-tertiary border border-gray-200 dark:border-dark-bg-tertiary rounded-lg text-gray-900 dark:text-dark-text-primary placeholder:text-gray-500 dark:placeholder:text-dark-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary focus:border-transparent transition-colors"
      />

      {/* Clear Button */}
      <AnimatePresence>
        {localValue && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-200 dark:hover:bg-dark-bg-secondary rounded-full transition-colors"
            aria-label="Clear search"
          >
            <X size={16} className="text-gray-500 dark:text-dark-text-secondary" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
};
