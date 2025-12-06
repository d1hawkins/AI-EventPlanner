import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ChatBubble } from './ChatBubble';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Bot: ({ size, className }) => (
    <span data-testid="bot-icon" data-size={size} className={className}>
      Bot
    </span>
  ),
  User: ({ size, className }) => (
    <span data-testid="user-icon" data-size={size} className={className}>
      User
    </span>
  ),
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
}));

describe('ChatBubble Component', () => {
  describe('Message Display', () => {
    it('should render message text', () => {
      render(<ChatBubble message="Hello, world!" isAI={false} />);

      expect(screen.getByText('Hello, world!')).toBeInTheDocument();
    });

    it('should render AI message', () => {
      render(<ChatBubble message="I am an AI response" isAI={true} />);

      expect(screen.getByText('I am an AI response')).toBeInTheDocument();
    });

    it('should render user message', () => {
      render(<ChatBubble message="User's message" isAI={false} />);

      expect(screen.getByText("User's message")).toBeInTheDocument();
    });
  });

  describe('Icon Display', () => {
    it('should show Bot icon for AI messages', () => {
      render(<ChatBubble message="AI message" isAI={true} />);

      const botIcon = screen.getByTestId('bot-icon');
      expect(botIcon).toBeInTheDocument();
      expect(botIcon).toHaveAttribute('data-size', '18');
    });

    it('should show User icon for user messages', () => {
      render(<ChatBubble message="User message" isAI={false} />);

      const userIcon = screen.getByTestId('user-icon');
      expect(userIcon).toBeInTheDocument();
      expect(userIcon).toHaveAttribute('data-size', '18');
    });

    it('should not show User icon for AI messages', () => {
      render(<ChatBubble message="AI message" isAI={true} />);

      expect(screen.queryByTestId('user-icon')).not.toBeInTheDocument();
    });

    it('should not show Bot icon for user messages', () => {
      render(<ChatBubble message="User message" isAI={false} />);

      expect(screen.queryByTestId('bot-icon')).not.toBeInTheDocument();
    });
  });

  describe('Styling - AI Messages', () => {
    it('should have left-aligned layout for AI messages', () => {
      const { container } = render(<ChatBubble message="AI message" isAI={true} />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('justify-start');
    });

    it('should have gray background for AI messages', () => {
      const { container } = render(<ChatBubble message="AI message" isAI={true} />);

      const bubble = container.querySelector('.rounded-2xl');
      expect(bubble).toHaveClass('bg-gray-bg');
      expect(bubble).toHaveClass('rounded-bl-sm');
    });

    it('should show primary background for Bot icon', () => {
      const { container } = render(<ChatBubble message="AI message" isAI={true} />);

      const iconWrapper = container.querySelector('.bg-primary');
      expect(iconWrapper).toBeInTheDocument();
      expect(iconWrapper).toHaveClass('rounded-full');
      expect(iconWrapper).toHaveClass('w-8');
      expect(iconWrapper).toHaveClass('h-8');
    });

    it('should align items to start for AI messages', () => {
      const { container } = render(<ChatBubble message="AI message" isAI={true} />);

      const messageWrapper = container.querySelector('.items-start');
      expect(messageWrapper).toBeInTheDocument();
    });
  });

  describe('Styling - User Messages', () => {
    it('should have right-aligned layout for user messages', () => {
      const { container } = render(<ChatBubble message="User message" isAI={false} />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('justify-end');
    });

    it('should have primary background with white text for user messages', () => {
      const { container } = render(<ChatBubble message="User message" isAI={false} />);

      const bubble = container.querySelector('.rounded-2xl');
      expect(bubble).toHaveClass('bg-primary');
      expect(bubble).toHaveClass('text-white');
      expect(bubble).toHaveClass('rounded-br-sm');
    });

    it('should show gray background for User icon', () => {
      const { container } = render(<ChatBubble message="User message" isAI={false} />);

      const iconWrapper = container.querySelector('.bg-gray-light');
      expect(iconWrapper).toBeInTheDocument();
      expect(iconWrapper).toHaveClass('rounded-full');
    });

    it('should align items to end for user messages', () => {
      const { container } = render(<ChatBubble message="User message" isAI={false} />);

      const messageWrapper = container.querySelector('.items-end');
      expect(messageWrapper).toBeInTheDocument();
    });
  });

  describe('Timestamp', () => {
    it('should render timestamp when provided', () => {
      render(<ChatBubble message="Message" isAI={true} timestamp="2:30 PM" />);

      expect(screen.getByText('2:30 PM')).toBeInTheDocument();
    });

    it('should not render timestamp when not provided', () => {
      const { container } = render(<ChatBubble message="Message" isAI={true} />);

      const timestamp = container.querySelector('.text-xs.text-gray');
      expect(timestamp).not.toBeInTheDocument();
    });

    it('should style timestamp correctly', () => {
      const { container } = render(
        <ChatBubble message="Message" isAI={true} timestamp="3:45 PM" />
      );

      const timestamp = screen.getByText('3:45 PM');
      expect(timestamp).toHaveClass('text-xs');
      expect(timestamp).toHaveClass('text-gray');
      expect(timestamp).toHaveClass('mt-1');
    });

    it('should render timestamp for user messages', () => {
      render(<ChatBubble message="Message" isAI={false} timestamp="4:00 PM" />);

      expect(screen.getByText('4:00 PM')).toBeInTheDocument();
    });
  });

  describe('Layout and Sizing', () => {
    it('should have max-width constraint', () => {
      const { container } = render(<ChatBubble message="Message" isAI={true} />);

      const messageWrapper = container.querySelector('.max-w-\\[75\\%\\]');
      expect(messageWrapper).toBeInTheDocument();
    });

    it('should have proper gap between icon and message', () => {
      const { container } = render(<ChatBubble message="Message" isAI={true} />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('gap-2');
      expect(wrapper).toHaveClass('mb-4');
    });

    it('should have rounded corners on bubble', () => {
      const { container } = render(<ChatBubble message="Message" isAI={true} />);

      const bubble = container.querySelector('.rounded-2xl');
      expect(bubble).toBeInTheDocument();
      expect(bubble).toHaveClass('px-4');
      expect(bubble).toHaveClass('py-3');
    });

    it('should have flex-shrink-0 on icon wrapper', () => {
      const { container } = render(<ChatBubble message="Message" isAI={true} />);

      const iconWrapper = container.querySelector('.flex-shrink-0');
      expect(iconWrapper).toBeInTheDocument();
    });
  });

  describe('Message Content', () => {
    it('should render short messages', () => {
      render(<ChatBubble message="Hi!" isAI={true} />);

      expect(screen.getByText('Hi!')).toBeInTheDocument();
    });

    it('should render long messages', () => {
      const longMessage =
        'This is a very long message that should still be displayed correctly within the chat bubble component regardless of its length.';
      render(<ChatBubble message={longMessage} isAI={true} />);

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should render messages with special characters', () => {
      const message = "Hello & welcome! What's up?";
      render(<ChatBubble message={message} isAI={false} />);

      expect(screen.getByText(message)).toBeInTheDocument();
    });

    it('should render messages with line breaks', () => {
      const message = 'Line 1\nLine 2';
      render(<ChatBubble message={message} isAI={true} />);

      // Check using a custom matcher since newlines don't create visual breaks
      expect(screen.getByText((content, element) => {
        return element.tagName.toLowerCase() === 'p' && element.textContent === message;
      })).toBeInTheDocument();
    });
  });

  describe('Icon Styling', () => {
    it('should center icons within wrapper', () => {
      const { container } = render(<ChatBubble message="Message" isAI={true} />);

      const iconWrapper = container.querySelector('.bg-primary');
      expect(iconWrapper).toHaveClass('flex');
      expect(iconWrapper).toHaveClass('items-center');
      expect(iconWrapper).toHaveClass('justify-center');
    });

    it('should apply white color to Bot icon', () => {
      const { container } = render(<ChatBubble message="Message" isAI={true} />);

      const botIcon = container.querySelector('[data-testid="bot-icon"]');
      expect(botIcon).toHaveClass('text-white');
    });

    it('should apply gray color to User icon', () => {
      const { container } = render(<ChatBubble message="Message" isAI={false} />);

      const userIcon = container.querySelector('[data-testid="user-icon"]');
      expect(userIcon).toHaveClass('text-gray');
    });
  });

  describe('Different Message Combinations', () => {
    it('should render AI message with timestamp', () => {
      render(<ChatBubble message="AI says hello" isAI={true} timestamp="10:15 AM" />);

      expect(screen.getByText('AI says hello')).toBeInTheDocument();
      expect(screen.getByText('10:15 AM')).toBeInTheDocument();
      expect(screen.getByTestId('bot-icon')).toBeInTheDocument();
    });

    it('should render user message with timestamp', () => {
      render(<ChatBubble message="User says hi" isAI={false} timestamp="10:16 AM" />);

      expect(screen.getByText('User says hi')).toBeInTheDocument();
      expect(screen.getByText('10:16 AM')).toBeInTheDocument();
      expect(screen.getByTestId('user-icon')).toBeInTheDocument();
    });
  });

  describe('Text Size', () => {
    it('should use small text for message content', () => {
      const { container } = render(<ChatBubble message="Message" isAI={true} />);

      const messageText = screen.getByText('Message');
      expect(messageText).toHaveClass('text-sm');
    });
  });
});
