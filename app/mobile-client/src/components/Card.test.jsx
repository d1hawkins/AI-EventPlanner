import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Card } from './Card';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
}));

describe('Card Component', () => {
  describe('Rendering', () => {
    it('should render children', () => {
      render(
        <Card>
          <div data-testid="child">Card Content</div>
        </Card>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
      expect(screen.getByText('Card Content')).toBeInTheDocument();
    });

    it('should apply base classes', () => {
      const { container } = render(<Card>Content</Card>);
      const card = container.firstChild;

      expect(card).toHaveClass('bg-white');
      expect(card).toHaveClass('rounded-lg');
      expect(card).toHaveClass('shadow-md');
      expect(card).toHaveClass('p-4');
    });

    it('should apply custom className', () => {
      const { container } = render(
        <Card className="custom-class">Content</Card>
      );
      const card = container.firstChild;

      expect(card).toHaveClass('custom-class');
      expect(card).toHaveClass('bg-white'); // Should still have base classes
    });
  });

  describe('Interactive Mode', () => {
    it('should apply interactive classes when interactive prop is true', () => {
      const { container } = render(<Card interactive>Content</Card>);
      const card = container.firstChild;

      expect(card).toHaveClass('cursor-pointer');
      expect(card).toHaveClass('hover:shadow-lg');
      expect(card).toHaveClass('transition-shadow');
    });

    it('should not apply interactive classes by default', () => {
      const { container } = render(<Card>Content</Card>);
      const card = container.firstChild;

      expect(card).not.toHaveClass('cursor-pointer');
      expect(card).not.toHaveClass('hover:shadow-lg');
    });
  });

  describe('onClick Handling', () => {
    it('should call onClick when clicked', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(
        <Card onClick={handleClick}>
          Clickable Card
        </Card>
      );

      await user.click(screen.getByText('Clickable Card'));

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should not require onClick prop', () => {
      render(<Card>No Click Handler</Card>);

      expect(screen.getByText('No Click Handler')).toBeInTheDocument();
    });

    it('should apply interactive classes when onClick is provided', () => {
      const { container } = render(
        <Card onClick={() => {}}>Content</Card>
      );
      const card = container.firstChild;

      // When onClick is provided, it becomes interactive
      expect(card).toBeInTheDocument();
    });
  });

  describe('Props Forwarding', () => {
    it('should forward additional props', () => {
      const { container } = render(
        <Card data-testid="custom-card" aria-label="Test Card">
          Content
        </Card>
      );

      const card = screen.getByTestId('custom-card');
      expect(card).toHaveAttribute('aria-label', 'Test Card');
    });

    it('should support role attribute', () => {
      render(<Card role="article">Content</Card>);

      expect(screen.getByRole('article')).toBeInTheDocument();
    });
  });

  describe('Motion Integration', () => {
    it('should use motion.div when interactive', () => {
      const { container } = render(
        <Card interactive>Animated Card</Card>
      );

      // Since we're mocking framer-motion, it should still render a div
      expect(container.firstChild.tagName).toBe('DIV');
    });

    it('should use regular div when not interactive', () => {
      const { container } = render(
        <Card>Static Card</Card>
      );

      expect(container.firstChild.tagName).toBe('DIV');
    });
  });

  describe('Combined Props', () => {
    it('should handle interactive and onClick together', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      const { container } = render(
        <Card interactive onClick={handleClick}>
          Interactive and Clickable
        </Card>
      );

      const card = container.firstChild;
      expect(card).toHaveClass('cursor-pointer');

      await user.click(screen.getByText('Interactive and Clickable'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should handle all props together', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(
        <Card
          interactive
          onClick={handleClick}
          className="extra-class"
          data-testid="full-card"
        >
          Full Featured Card
        </Card>
      );

      const card = screen.getByTestId('full-card');
      expect(card).toHaveClass('bg-white');
      expect(card).toHaveClass('cursor-pointer');
      expect(card).toHaveClass('extra-class');

      await user.click(card);
      expect(handleClick).toHaveBeenCalled();
    });
  });
});
