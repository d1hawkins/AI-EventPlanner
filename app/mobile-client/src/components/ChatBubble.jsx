import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';

export const ChatBubble = ({ message, isAI, timestamp }) => {
  const bubbleVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={bubbleVariants}
      initial="initial"
      animate="animate"
      className={`flex gap-2 mb-4 ${isAI ? 'justify-start' : 'justify-end'}`}
    >
      {isAI && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
          <Bot size={18} className="text-white" />
        </div>
      )}

      <div className={`flex flex-col ${isAI ? 'items-start' : 'items-end'} max-w-[75%]`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isAI
              ? 'bg-gray-bg rounded-bl-sm'
              : 'bg-primary text-white rounded-br-sm'
          }`}
        >
          <p className="text-sm">{message}</p>
        </div>
        {timestamp && (
          <span className="text-xs text-gray mt-1">{timestamp}</span>
        )}
      </div>

      {!isAI && (
        <div className="w-8 h-8 rounded-full bg-gray-light flex items-center justify-center flex-shrink-0">
          <User size={18} className="text-gray" />
        </div>
      )}
    </motion.div>
  );
};
