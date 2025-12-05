import { useState, useEffect, useRef } from 'react';
import { ChatHeader } from '../components/ChatHeader';
import { ChatMessage } from '../components/ChatMessage';
import { InlineEventCard } from '../components/InlineEventCard';
import { ActionChip, ActionChipGroup } from '../components/ActionChip';
import { ChatInput } from '../components/ChatInput';
import { SideMenu } from '../components/SideMenu';
import { getRelativeTime } from '../utils/dateUtils';

export const ChatScreen = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "Hi! I'm your AI event planning assistant. I can help you plan amazing events from start to finish. What would you like to plan today?",
      timestamp: new Date(Date.now() - 60000),
    },
  ]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  // Sample event data
  const sampleEvent = {
    id: 1,
    name: 'Summer BBQ Party',
    date: '2024-06-15',
    icon: '🎉',
    guests: 50,
    budget: 3000,
    budgetSpent: 2500,
    progress: 60,
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (content) => {
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);

    // Simulate AI typing
    setIsTyping(true);

    // Simulate AI response after delay
    setTimeout(() => {
      setIsTyping(false);

      let aiResponse;

      // Simple response logic based on user input
      const lowerContent = content.toLowerCase();

      if (lowerContent.includes('event') || lowerContent.includes('party') || lowerContent.includes('plan')) {
        aiResponse = {
          id: messages.length + 2,
          type: 'ai',
          content: "Great! I'd love to help you plan an event. To get started, I need a few details:",
          timestamp: new Date(),
          actions: [
            { icon: '📅', text: 'When is it?', action: 'date' },
            { icon: '👥', text: 'How many guests?', action: 'guests' },
            { icon: '💰', text: 'What\'s your budget?', action: 'budget' },
            { icon: '📍', text: 'Where will it be?', action: 'location' },
          ],
        };
      } else if (lowerContent.includes('show') || lowerContent.includes('my events') || lowerContent.includes('list')) {
        aiResponse = {
          id: messages.length + 2,
          type: 'ai',
          content: "Here are your upcoming events:",
          timestamp: new Date(),
          event: sampleEvent,
          actions: [
            { icon: '🎯', text: 'Add tasks', action: 'tasks' },
            { icon: '📧', text: 'Invite guests', action: 'invites' },
            { icon: '📊', text: 'View analytics', action: 'analytics' },
          ],
        };
      } else if (lowerContent.includes('help')) {
        aiResponse = {
          id: messages.length + 2,
          type: 'ai',
          content: "I can help you with:\n\n• Planning new events\n• Managing existing events\n• Sending invitations\n• Tracking budgets\n• Finding vendors\n• And much more!\n\nJust tell me what you need!",
          timestamp: new Date(),
          actions: [
            { icon: '🎉', text: 'New Event', action: 'new' },
            { icon: '📋', text: 'My Events', action: 'list' },
            { icon: '💡', text: 'Get Ideas', action: 'ideas' },
          ],
        };
      } else {
        aiResponse = {
          id: messages.length + 2,
          type: 'ai',
          content: "I understand you're interested in that! Let me help you. Could you tell me more about what you'd like to do?",
          timestamp: new Date(),
          actions: [
            { icon: '🎉', text: 'Plan an event', action: 'plan' },
            { icon: '📋', text: 'See my events', action: 'events' },
            { icon: '💡', text: 'Get suggestions', action: 'suggest' },
          ],
        };
      }

      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  const handleActionClick = (action) => {
    const actionMessages = {
      date: "When would you like to have your event? You can tell me a specific date like 'June 15th' or 'next Saturday'.",
      guests: "How many people will you be inviting to your event?",
      budget: "What's your budget for this event? I'll help you make the most of it!",
      location: "Where would you like to host your event? Indoor venue, outdoor space, or somewhere specific?",
      tasks: "I can help you create tasks for your event. What do you need to get done?",
      invites: "Let's send out invitations! Do you want to use email, text, or printed invitations?",
      plan: "Great! Let's plan an amazing event. What kind of event are you thinking of?",
      events: "Here are your events!",
      suggest: "I have some great ideas for you! What type of event interests you?",
    };

    handleSendMessage(actionMessages[action] || "Tell me more about that!");
  };

  const handleEventAction = (action, event) => {
    if (action === 'view') {
      handleSendMessage(`Tell me more about ${event.name}`);
    } else if (action === 'chat') {
      handleSendMessage(`I'd like to discuss ${event.name}`);
    }
  };

  const handleMenuNavigate = (action) => {
    if (action === 'events') {
      handleSendMessage('Show me all my events');
    } else if (action === 'calendar') {
      handleSendMessage('Show me my calendar');
    } else if (action === 'analytics') {
      handleSendMessage('Show me event analytics');
    } else if (action === 'help') {
      handleSendMessage('Help');
    } else if (action === 'logout') {
      // Handle logout
      console.log('Logout');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white dark:bg-dark-bg-primary transition-colors">
      {/* Header */}
      <ChatHeader onMenuClick={() => setIsMenuOpen(true)} />

      {/* Side Menu */}
      <SideMenu
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        onNavigate={handleMenuNavigate}
      />

      {/* Chat Messages */}
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto px-4 pb-24 pt-4"
      >
        {messages.map((message) => (
          <div key={message.id}>
            <ChatMessage
              message={message.content}
              isAI={message.type === 'ai'}
              timestamp={getRelativeTime(message.timestamp)}
            >
              {/* Inline Event Card */}
              {message.event && (
                <InlineEventCard
                  event={message.event}
                  onAction={handleEventAction}
                />
              )}

              {/* Action Chips */}
              {message.actions && (
                <ActionChipGroup>
                  {message.actions.map((action, index) => (
                    <ActionChip
                      key={index}
                      icon={action.icon}
                      text={action.text}
                      onClick={() => handleActionClick(action.action)}
                    />
                  ))}
                </ActionChipGroup>
              )}
            </ChatMessage>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center transition-colors">
              <span className="text-blue-600 dark:text-blue-400 text-sm">AI</span>
            </div>
            <div className="bg-blue-50 dark:bg-dark-bg-tertiary rounded-2xl px-4 py-3 transition-colors">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 dark:bg-dark-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 dark:bg-dark-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 dark:bg-dark-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <ChatInput onSend={handleSendMessage} />
    </div>
  );
};
