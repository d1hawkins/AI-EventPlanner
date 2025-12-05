import { useState, useRef, useEffect } from 'react';
import { Send, Plus, Mic } from 'lucide-react';
import { motion } from 'framer-motion';

export const ChatInput = ({ onSend, placeholder = "Type a message..." }) => {
  const [value, setValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef(null);

  const handleSubmit = () => {
    if (value.trim()) {
      onSend(value.trim());
      setValue('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [value]);

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-dark-bg-primary border-t border-gray-200 dark:border-dark-bg-tertiary p-4 shadow-lg transition-colors">
      <div className={`flex items-end gap-2 transition-all ${isFocused ? 'ring-2 ring-blue-500 dark:ring-blue-400 rounded-3xl' : ''}`}>
        <button
          className="flex-shrink-0 w-10 h-10 flex items-center justify-center text-gray-600 dark:text-dark-text-secondary hover:text-gray-900 dark:hover:text-dark-text-primary hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-full transition-colors"
          aria-label="Attach file"
        >
          <Plus size={20} />
        </button>

        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            rows={1}
            className="w-full px-4 py-3 bg-gray-50 dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-3xl resize-none focus:outline-none focus:bg-white dark:focus:bg-dark-bg-tertiary focus:border-transparent text-base dark:text-dark-text-primary placeholder:text-gray-500 dark:placeholder:text-dark-text-tertiary max-h-32 overflow-y-auto transition-colors"
            style={{ minHeight: '44px' }}
          />
        </div>

        {value.trim() ? (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            onClick={handleSubmit}
            className="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-blue-600 dark:bg-blue-500 text-white hover:bg-blue-700 dark:hover:bg-blue-600 rounded-full transition-colors"
            aria-label="Send message"
          >
            <Send size={18} />
          </motion.button>
        ) : (
          <button
            className="flex-shrink-0 w-10 h-10 flex items-center justify-center text-gray-600 dark:text-dark-text-secondary hover:text-gray-900 dark:hover:text-dark-text-primary hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-full transition-colors"
            aria-label="Voice input"
          >
            <Mic size={20} />
          </button>
        )}
      </div>
    </div>
  );
};
