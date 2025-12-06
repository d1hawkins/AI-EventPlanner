import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ActionChip, ActionChipGroup } from './ActionChip';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    button: ({ children, ...props }) => <button {...props}>{children}</button>,
  },
}));

describe('ActionChip Component', () => {
  describe('Rendering', () => {
    it('should render with text', () => {
      render(<ActionChip text="Action" onClick={() => {}} />);

      expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
    });

    it('should render with icon and text', () => {
      render(
        <ActionChip
          icon="✓"
          text="Confirm"
          onClick={() => {}}
        />
      );

      expect(screen.getByText('✓')).toBeInTheDocument();
      expect(screen.getByText('Confirm')).toBeInTheDocument();
    });

    it('should render without icon', () => {
      render(<ActionChip text="No Icon" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('No Icon');
      expect(button.querySelector('span')).toHaveTextContent('No Icon');
    });
  });

  describe('Variants', () => {
    it('should apply default variant by default', () => {
      render(<ActionChip text="Default" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border-gray-300');
      expect(button).toHaveClass('bg-white');
      expect(button).toHaveClass('text-gray-700');
    });

    it('should apply primary variant', () => {
      render(<ActionChip text="Primary" variant="primary" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border-blue-600');
      expect(button).toHaveClass('bg-blue-50');
      expect(button).toHaveClass('text-blue-700');
    });

    it('should apply success variant', () => {
      render(<ActionChip text="Success" variant="success" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border-green-600');
      expect(button).toHaveClass('bg-green-50');
      expect(button).toHaveClass('text-green-700');
    });
  });

  describe('Dark Mode Classes', () => {
    it('should include dark mode classes for default variant', () => {
      render(<ActionChip text="Dark" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button.className).toContain('dark:border-dark-bg-tertiary');
      expect(button.className).toContain('dark:bg-dark-bg-secondary');
      expect(button.className).toContain('dark:text-dark-text-primary');
    });

    it('should include dark mode classes for primary variant', () => {
      render(<ActionChip text="Primary" variant="primary" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button.className).toContain('dark:border-blue-500');
      expect(button.className).toContain('dark:bg-blue-900/30');
      expect(button.className).toContain('dark:text-blue-400');
    });

    it('should include dark mode classes for success variant', () => {
      render(<ActionChip text="Success" variant="success" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button.className).toContain('dark:border-green-500');
      expect(button.className).toContain('dark:bg-green-900/30');
      expect(button.className).toContain('dark:text-green-400');
    });
  });

  describe('Styling', () => {
    it('should have base layout classes', () => {
      render(<ActionChip text="Test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('inline-flex');
      expect(button).toHaveClass('items-center');
      expect(button).toHaveClass('gap-2');
    });

    it('should have size classes', () => {
      render(<ActionChip text="Test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-4');
      expect(button).toHaveClass('py-2.5');
    });

    it('should have border and shape classes', () => {
      render(<ActionChip text="Test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border');
      expect(button).toHaveClass('rounded-full');
    });

    it('should have text styling classes', () => {
      render(<ActionChip text="Test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('text-sm');
      expect(button).toHaveClass('font-medium');
    });

    it('should have transition classes', () => {
      render(<ActionChip text="Test" onClick={() => {}} />);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('transition-all');
    });
  });

  describe('Click Handling', () => {
    it('should call onClick when clicked', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<ActionChip text="Click me" onClick={handleClick} />);

      await user.click(screen.getByRole('button'));

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should handle multiple clicks', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<ActionChip text="Multi click" onClick={handleClick} />);

      const button = screen.getByRole('button');
      await user.click(button);
      await user.click(button);

      expect(handleClick).toHaveBeenCalledTimes(2);
    });
  });

  describe('Icon Rendering', () => {
    it('should render icon in separate span', () => {
      const { container } = render(
        <ActionChip icon="🎯" text="Target" onClick={() => {}} />
      );

      const iconSpan = container.querySelector('span.text-base');
      expect(iconSpan).toBeInTheDocument();
      expect(iconSpan).toHaveTextContent('🎯');
    });

    it('should apply text-base class to icon', () => {
      const { container } = render(
        <ActionChip icon="✓" text="Check" onClick={() => {}} />
      );

      const iconSpan = container.querySelector('span');
      expect(iconSpan).toHaveClass('text-base');
    });

    it('should render text in separate span', () => {
      const { container } = render(
        <ActionChip text="Text Test" onClick={() => {}} />
      );

      // Text should be in a span
      const textSpans = container.querySelectorAll('span');
      const textSpan = Array.from(textSpans).find(span => span.textContent === 'Text Test');
      expect(textSpan).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should be keyboard accessible', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<ActionChip text="Keyboard" onClick={handleClick} />);

      const button = screen.getByRole('button');
      button.focus();

      await user.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should have button role', () => {
      render(<ActionChip text="Role" onClick={() => {}} />);

      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should be focusable', () => {
      render(<ActionChip text="Focus" onClick={() => {}} />);

      const button = screen.getByRole('button');
      button.focus();

      expect(document.activeElement).toBe(button);
    });
  });

  describe('Different Variants with Icons', () => {
    it('should render primary variant with icon', () => {
      render(
        <ActionChip
          icon="➜"
          text="Go"
          variant="primary"
          onClick={() => {}}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border-blue-600');
      expect(screen.getByText('➜')).toBeInTheDocument();
      expect(screen.getByText('Go')).toBeInTheDocument();
    });

    it('should render success variant with icon', () => {
      render(
        <ActionChip
          icon="✓"
          text="Done"
          variant="success"
          onClick={() => {}}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border-green-600');
      expect(screen.getByText('✓')).toBeInTheDocument();
      expect(screen.getByText('Done')).toBeInTheDocument();
    });
  });
});

describe('ActionChipGroup Component', () => {
  describe('Rendering', () => {
    it('should render children', () => {
      render(
        <ActionChipGroup>
          <ActionChip text="Chip 1" onClick={() => {}} />
          <ActionChip text="Chip 2" onClick={() => {}} />
        </ActionChipGroup>
      );

      expect(screen.getByText('Chip 1')).toBeInTheDocument();
      expect(screen.getByText('Chip 2')).toBeInTheDocument();
    });

    it('should render multiple chips', () => {
      render(
        <ActionChipGroup>
          <ActionChip text="First" onClick={() => {}} />
          <ActionChip text="Second" onClick={() => {}} />
          <ActionChip text="Third" onClick={() => {}} />
        </ActionChipGroup>
      );

      expect(screen.getAllByRole('button')).toHaveLength(3);
    });

    it('should render single chip', () => {
      render(
        <ActionChipGroup>
          <ActionChip text="Only One" onClick={() => {}} />
        </ActionChipGroup>
      );

      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should render empty group', () => {
      const { container } = render(<ActionChipGroup />);

      expect(container.firstChild).toBeInTheDocument();
      expect(container.firstChild.children).toHaveLength(0);
    });
  });

  describe('Styling', () => {
    it('should have flex layout classes', () => {
      const { container } = render(
        <ActionChipGroup>
          <ActionChip text="Test" onClick={() => {}} />
        </ActionChipGroup>
      );

      const group = container.firstChild;
      expect(group).toHaveClass('flex');
      expect(group).toHaveClass('flex-wrap');
      expect(group).toHaveClass('gap-2');
      expect(group).toHaveClass('mt-3');
    });
  });

  describe('Chip Variants in Group', () => {
    it('should render chips with different variants', () => {
      render(
        <ActionChipGroup>
          <ActionChip text="Default" onClick={() => {}} />
          <ActionChip text="Primary" variant="primary" onClick={() => {}} />
          <ActionChip text="Success" variant="success" onClick={() => {}} />
        </ActionChipGroup>
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(3);

      expect(buttons[0]).toHaveClass('border-gray-300');
      expect(buttons[1]).toHaveClass('border-blue-600');
      expect(buttons[2]).toHaveClass('border-green-600');
    });
  });

  describe('Interaction', () => {
    it('should allow clicking individual chips in group', async () => {
      const user = userEvent.setup();
      const handleClick1 = vi.fn();
      const handleClick2 = vi.fn();

      render(
        <ActionChipGroup>
          <ActionChip text="First" onClick={handleClick1} />
          <ActionChip text="Second" onClick={handleClick2} />
        </ActionChipGroup>
      );

      await user.click(screen.getByText('First'));
      expect(handleClick1).toHaveBeenCalledTimes(1);
      expect(handleClick2).not.toHaveBeenCalled();

      await user.click(screen.getByText('Second'));
      expect(handleClick1).toHaveBeenCalledTimes(1);
      expect(handleClick2).toHaveBeenCalledTimes(1);
    });
  });

  describe('Nested Content', () => {
    it('should render chips with icons in group', () => {
      render(
        <ActionChipGroup>
          <ActionChip icon="🎯" text="Target" onClick={() => {}} />
          <ActionChip icon="✓" text="Check" onClick={() => {}} />
        </ActionChipGroup>
      );

      expect(screen.getByText('🎯')).toBeInTheDocument();
      expect(screen.getByText('✓')).toBeInTheDocument();
      expect(screen.getByText('Target')).toBeInTheDocument();
      expect(screen.getByText('Check')).toBeInTheDocument();
    });
  });
});
