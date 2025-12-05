import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Mic, Paperclip } from 'lucide-react';
import { ChatBubble } from '../components/ChatBubble';
import { QuickReplyButton } from '../components/QuickReplyButton';
import { BottomNav } from '../components/BottomNav';
import { getRelativeTime } from '../utils/dateUtils';

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

  return (
    <div className="flex flex-col h-screen bg-gray-bg">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="p-1">
          <ArrowLeft size={24} />
        </button>
        <div className="flex-1">
          <h2 className="font-semibold">AI Assistant</h2>
          <p className="text-xs text-success">Online</p>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
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
              text="When is the party?"
              icon="📅"
              onClick={() => handleQuickReply("When is the party?")}
            />
            <QuickReplyButton
              text="How many guests?"
              icon="👥"
              onClick={() => handleQuickReply("How many guests?")}
            />
            <QuickReplyButton
              text="What's your budget?"
              icon="💰"
              onClick={() => handleQuickReply("What's your budget?")}
            />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-light p-3 flex items-center gap-2">
        <button className="p-2 text-gray">
          <Paperclip size={20} />
        </button>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
          className="flex-1 bg-gray-bg rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button className="p-2 text-gray">
          <Mic size={20} />
        </button>
        <button
          onClick={handleSend}
          className="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center"
        >
          <Send size={18} />
        </button>
      </div>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  );
};
