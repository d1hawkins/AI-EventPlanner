import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';

export const ChatMessage = ({ message, isAI, timestamp, children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 mb-4 ${isAI ? 'justify-start' : 'justify-end'}`}
    >
      {isAI && (
        <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center flex-shrink-0 mt-1 transition-colors">
          <Bot size={18} className="text-blue-600 dark:text-blue-400" />
        </div>
      )}

      <div className={`flex flex-col ${isAI ? 'items-start' : 'items-end'} max-w-[80%]`}>
        <div
          className={`rounded-2xl px-4 py-3 transition-colors ${
            isAI
              ? 'bg-blue-50 dark:bg-dark-bg-tertiary text-gray-900 dark:text-dark-text-primary'
              : 'bg-blue-100 dark:bg-blue-900/30 text-gray-900 dark:text-dark-text-primary'
          }`}
        >
          <p className="text-base leading-relaxed whitespace-pre-wrap">{message}</p>
          {children}
        </div>
        {timestamp && (
          <span className="text-xs text-gray-500 dark:text-dark-text-tertiary mt-1 px-1 transition-colors">{timestamp}</span>
        )}
      </div>

      {!isAI && (
        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-dark-bg-tertiary flex items-center justify-center flex-shrink-0 mt-1 transition-colors">
          <User size={18} className="text-gray-600 dark:text-dark-text-secondary" />
        </div>
      )}
    </motion.div>
  );
};
