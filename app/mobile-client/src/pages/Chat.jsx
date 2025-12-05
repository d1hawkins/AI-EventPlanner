import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Mic, Paperclip, LayoutDashboard, Calendar, Users, CreditCard, ChevronRight } from 'lucide-react';
import { ChatBubble } from '../components/ChatBubble';
import { QuickReplyButton } from '../components/QuickReplyButton';
import { BottomNav } from '../components/BottomNav';
import { getRelativeTime } from '../utils/dateUtils';
import { motion } from 'framer-motion';

export const Chat = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "Hi! I'm your event planning AI assistant. What would you like to plan today?",
      isAI: true,
      timestamp: new Date(Date.now() - 120000),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const newMessage = {
      id: messages.length + 1,
      content: inputValue,
      isAI: false,
      timestamp: new Date(),
    };

    setMessages([...messages, newMessage]);
    setInputValue('');
    setShowQuickReplies(false);
    setShowQuickActions(false);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        content: "Great! I can help you with that. Let me gather some details...",
        isAI: true,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  const handleQuickReply = (text) => {
    const newMessage = {
      id: messages.length + 1,
      content: text,
      isAI: false,
      timestamp: new Date(),
    };

    setMessages([...messages, newMessage]);
    setShowQuickReplies(false);
    setShowQuickActions(false);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        content: "Perfect! Tell me more about that...",
        isAI: true,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  const quickActions = [
    {
      icon: LayoutDashboard,
      label: 'Dashboard',
      description: 'View overview',
      path: '/dashboard',
      color: 'blue',
    },
    {
      icon: Calendar,
      label: 'Events',
      description: 'Manage events',
      path: '/events',
      color: 'green',
    },
    {
      icon: Users,
      label: 'Team',
      description: 'Manage team',
      path: '/team',
      color: 'purple',
    },
    {
      icon: CreditCard,
      label: 'Subscription',
      description: 'View plan',
      path: '/subscription',
      color: 'orange',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
    purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
    orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
  };

  return (
    <div className="flex flex-col h-screen bg-gray-bg dark:bg-dark-bg-primary transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-dark-bg-secondary shadow-sm p-4 flex items-center gap-3 transition-colors">
        <button
          onClick={() => navigate(-1)}
          className="p-1 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
        >
          <ArrowLeft size={24} className="text-gray-700 dark:text-dark-text-primary" />
        </button>
        <div className="flex-1">
          <h2 className="font-semibold text-gray-900 dark:text-dark-text-primary transition-colors">
            AI Assistant
          </h2>
          <p className="text-xs text-success dark:text-green-400">Online</p>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Quick Action Cards - Show at the start */}
        {showQuickActions && messages.length === 1 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <p className="text-sm text-gray-600 dark:text-dark-text-secondary mb-3 transition-colors">
              Quick actions:
            </p>
            <div className="grid grid-cols-2 gap-3">
              {quickActions.map((action) => {
                const Icon = action.icon;
                return (
                  <motion.button
                    key={action.path}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => navigate(action.path)}
                    className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 text-left hover:border-primary dark:hover:border-primary-light transition-all"
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-2 ${colorClasses[action.color]}`}>
                      <Icon size={20} />
                    </div>
                    <h3 className="font-medium text-gray-900 dark:text-dark-text-primary text-sm mb-1">
                      {action.label}
                    </h3>
                    <p className="text-xs text-gray-600 dark:text-dark-text-secondary">
                      {action.description}
                    </p>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        )}

        {messages.map((message) => (
          <ChatBubble
            key={message.id}
            message={message.content}
            isAI={message.isAI}
            timestamp={getRelativeTime(message.timestamp)}
          />
        ))}

        {/* Quick Replies */}
        {showQuickReplies && (
          <div className="mt-4 space-y-2">
            <QuickReplyButton
              text="Plan a new event"
              icon="🎉"
              onClick={() => handleQuickReply("I want to plan a new event")}
            />
            <QuickReplyButton
              text="View my events"
              icon="📅"
              onClick={() => navigate('/events')}
            />
            <QuickReplyButton
              text="Check my dashboard"
              icon="📊"
              onClick={() => navigate('/dashboard')}
            />
            <QuickReplyButton
              text="Manage my team"
              icon="👥"
              onClick={() => navigate('/team')}
            />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white dark:bg-dark-bg-secondary border-t border-gray-light dark:border-dark-bg-tertiary p-3 flex items-center gap-2 transition-colors">
        <button className="p-2 text-gray-600 dark:text-dark-text-secondary hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors">
          <Paperclip size={20} />
        </button>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
          className="flex-1 bg-gray-bg dark:bg-dark-bg-tertiary rounded-full px-4 py-2 text-sm text-gray-900 dark:text-dark-text-primary placeholder:text-gray-500 dark:placeholder:text-dark-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary-light transition-colors"
        />
        <button className="p-2 text-gray-600 dark:text-dark-text-secondary hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors">
          <Mic size={20} />
        </button>
        <button
          onClick={handleSend}
          className="w-10 h-10 bg-primary hover:bg-primary-dark dark:bg-primary-light dark:hover:bg-primary text-white rounded-full flex items-center justify-center transition-colors"
        >
          <Send size={18} />
        </button>
      </div>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  );
};
