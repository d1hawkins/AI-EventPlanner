import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QuickReplyButton } from './QuickReplyButton';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    button: ({ children, ...props }) => <button {...props}>{children}</button>,
  },
}));

describe('QuickReplyButton Component', () => {
  describe('Rendering', () => {
    it('should render button with text', () => {
      render(<QuickReplyButton text="Quick Reply" onClick={() => {}} />);

      expect(screen.getByRole('button', { name: 'Quick Reply' })).toBeInTheDocument();
    });

    it('should render button with icon and text', () => {
      render(
        <QuickReplyButton
          text="Yes, please"
          icon="✓"
          onClick={() => {}}
        />
      );

      expect(screen.getByRole('button')).toBeInTheDocument();
      expect(screen.getByText('✓')).toBeInTheDocument();
      expect(screen.getByText('Yes, please')).toBeInTheDocument();
    });

    it('should render without icon', () => {
      render(<QuickReplyButton text="No icon" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('No icon');
      expect(button.querySelector('span')).not.toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('should have correct base classes', () => {
      render(<QuickReplyButton text="Test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-full');
      expect(button).toHaveClass('px-4');
      expect(button).toHaveClass('py-3');
      expect(button).toHaveClass('bg-white');
      expect(button).toHaveClass('border-2');
      expect(button).toHaveClass('border-primary');
      expect(button).toHaveClass('text-primary');
      expect(button).toHaveClass('rounded-lg');
      expect(button).toHaveClass('text-left');
      expect(button).toHaveClass('font-medium');
      expect(button).toHaveClass('text-sm');
    });

    it('should have flex layout classes', () => {
      render(<QuickReplyButton text="Test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('flex');
      expect(button).toHaveClass('items-center');
      expect(button).toHaveClass('gap-2');
    });

    it('should have hover transition classes', () => {
      render(<QuickReplyButton text="Test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('hover:bg-gray-50');
      expect(button).toHaveClass('transition-colors');
    });
  });

  describe('Click Handling', () => {
    it('should call onClick when clicked', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<QuickReplyButton text="Click me" onClick={handleClick} />);

      await user.click(screen.getByRole('button'));

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should call onClick with correct context', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<QuickReplyButton text="Context test" onClick={handleClick} />);

      const button = screen.getByRole('button');
      await user.click(button);

      expect(handleClick).toHaveBeenCalledWith(expect.any(Object)); // Click event
    });

    it('should handle multiple clicks', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<QuickReplyButton text="Multiple clicks" onClick={handleClick} />);

      const button = screen.getByRole('button');
      await user.click(button);
      await user.click(button);
      await user.click(button);

      expect(handleClick).toHaveBeenCalledTimes(3);
    });
  });

  describe('Icon Rendering', () => {
    it('should render text icon', () => {
      render(
        <QuickReplyButton
          text="With emoji"
          icon="🎉"
          onClick={() => {}}
        />
      );

      expect(screen.getByText('🎉')).toBeInTheDocument();
    });

    it('should render icon in span element', () => {
      const { container } = render(
        <QuickReplyButton
          text="Icon test"
          icon="→"
          onClick={() => {}}
        />
      );

      const iconSpan = container.querySelector('span');
      expect(iconSpan).toBeInTheDocument();
      expect(iconSpan).toHaveTextContent('→');
    });

    it('should position icon before text', () => {
      const { container } = render(
        <QuickReplyButton
          text="Order test"
          icon="►"
          onClick={() => {}}
        />
      );

      const button = container.querySelector('button');
      const children = Array.from(button.childNodes);

      // First child should be the icon span
      expect(children[0].textContent).toBe('►');
      // Second child should be the text
      expect(children[1].textContent).toBe('Order test');
    });
  });

  describe('Text Content', () => {
    it('should render short text', () => {
      render(<QuickReplyButton text="Yes" onClick={() => {}} />);

      expect(screen.getByText('Yes')).toBeInTheDocument();
    });

    it('should render long text', () => {
      const longText = 'This is a very long quick reply button text that should still work';
      render(<QuickReplyButton text={longText} onClick={() => {}} />);

      expect(screen.getByText(longText)).toBeInTheDocument();
    });

    it('should handle special characters in text', () => {
      render(<QuickReplyButton text="Yes & No?" onClick={() => {}} />);

      expect(screen.getByText('Yes & No?')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should be keyboard accessible', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<QuickReplyButton text="Keyboard test" onClick={handleClick} />);

      const button = screen.getByRole('button');
      button.focus();

      await user.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalledTimes(1);

      await user.keyboard(' ');
      expect(handleClick).toHaveBeenCalledTimes(2);
    });

    it('should have button role', () => {
      render(<QuickReplyButton text="Role test" onClick={() => {}} />);

      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should be focusable', () => {
      render(<QuickReplyButton text="Focus test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      button.focus();

      expect(document.activeElement).toBe(button);
    });
  });

  describe('Motion Integration', () => {
    it('should render as motion.button', () => {
      const { container } = render(
        <QuickReplyButton text="Motion test" onClick={() => {}} />
      );

      // Should be a button element (even though mocked)
      expect(container.querySelector('button')).toBeInTheDocument();
    });
  });
});
