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
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-1">
          <Bot size={18} className="text-blue-600" />
        </div>
      )}

      <div className={`flex flex-col ${isAI ? 'items-start' : 'items-end'} max-w-[80%]`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isAI
              ? 'bg-blue-50 text-gray-900'
              : 'bg-blue-100 text-gray-900'
          }`}
        >
          <p className="text-base leading-relaxed whitespace-pre-wrap">{message}</p>
          {children}
        </div>
        {timestamp && (
          <span className="text-xs text-gray-500 mt-1 px-1">{timestamp}</span>
        )}
      </div>

      {!isAI && (
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
          <User size={18} className="text-gray-600" />
        </div>
      )}
    </motion.div>
  );
};
