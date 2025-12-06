import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EventCard } from './EventCard';
import * as dateUtils from '../utils/dateUtils';

// Mock the dateUtils module
vi.mock('../utils/dateUtils', () => ({
  formatDate: vi.fn((date) => 'Mocked Date'),
}));

// Mock framer-motion for Card component
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
}));

describe('EventCard Component', () => {
  const mockEvent = {
    id: '1',
    name: 'Birthday Party',
    date: '2024-06-15',
    icon: '🎂',
    progress: 60,
    status: 'active',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render event name', () => {
      render(<EventCard event={mockEvent} />);

      expect(screen.getByText('Birthday Party')).toBeInTheDocument();
    });

    it('should render event icon', () => {
      render(<EventCard event={mockEvent} />);

      expect(screen.getByText('🎂')).toBeInTheDocument();
    });

    it('should render default icon when no icon provided', () => {
      const eventWithoutIcon = { ...mockEvent, icon: null };
      render(<EventCard event={eventWithoutIcon} />);

      expect(screen.getByText('🎉')).toBeInTheDocument();
    });

    it('should call formatDate with event date', () => {
      render(<EventCard event={mockEvent} />);

      expect(dateUtils.formatDate).toHaveBeenCalledWith('2024-06-15');
      expect(screen.getByText('Mocked Date')).toBeInTheDocument();
    });

    it('should render progress percentage', () => {
      render(<EventCard event={mockEvent} />);

      expect(screen.getByText('60% done')).toBeInTheDocument();
    });
  });

  describe('Progress Visualization', () => {
    it('should render progress bar', () => {
      const { container } = render(<EventCard event={mockEvent} />);

      // ProgressBar component should be rendered
      const progressBar = container.querySelector('.h-2');
      expect(progressBar).toBeInTheDocument();
    });

    it('should render 5 progress dots', () => {
      const { container } = render(<EventCard event={mockEvent} />);

      const dots = container.querySelectorAll('.w-2.h-2.rounded-full');
      expect(dots).toHaveLength(5);
    });

    it('should fill correct number of dots based on progress (60%)', () => {
      const { container } = render(<EventCard event={mockEvent} />);

      const filledDots = container.querySelectorAll('.bg-success');
      const emptyDots = container.querySelectorAll('.bg-gray-light');

      // 60% = 3 filled dots (60/20 = 3)
      expect(filledDots.length).toBeGreaterThanOrEqual(3);
    });

    it('should fill 0 dots for 0% progress', () => {
      const event = { ...mockEvent, progress: 0 };
      const { container } = render(<EventCard event={event} />);

      const filledDots = container.querySelectorAll('.w-2.h-2.rounded-full.bg-success');
      expect(filledDots).toHaveLength(0);
    });

    it('should fill all 5 dots for 100% progress', () => {
      const event = { ...mockEvent, progress: 100 };
      const { container } = render(<EventCard event={event} />);

      const filledDots = container.querySelectorAll('.w-2.h-2.rounded-full.bg-success');
      expect(filledDots).toHaveLength(5);
    });

    it('should fill 2 dots for 40% progress', () => {
      const event = { ...mockEvent, progress: 40 };
      const { container } = render(<EventCard event={event} />);

      const filledDots = container.querySelectorAll('.w-2.h-2.rounded-full.bg-success');
      expect(filledDots).toHaveLength(2); // 40/20 = 2
    });
  });

  describe('Status Colors', () => {
    it('should apply primary color for active status', () => {
      const { container } = render(<EventCard event={{ ...mockEvent, status: 'active' }} />);

      const statusText = container.querySelector('.text-primary');
      expect(statusText).toBeInTheDocument();
      expect(statusText).toHaveTextContent('60% done');
    });

    it('should apply success color for completed status', () => {
      const { container } = render(<EventCard event={{ ...mockEvent, status: 'completed' }} />);

      const statusText = container.querySelector('.text-success');
      expect(statusText).toBeInTheDocument();
    });

    it('should apply gray color for cancelled status', () => {
      const { container } = render(<EventCard event={{ ...mockEvent, status: 'cancelled' }} />);

      const statusText = container.querySelector('.text-gray');
      expect(statusText).toBeInTheDocument();
    });
  });

  describe('Click Handling', () => {
    it('should call onClick with event data when clicked', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<EventCard event={mockEvent} onClick={handleClick} />);

      await user.click(screen.getByText('Birthday Party'));

      expect(handleClick).toHaveBeenCalledTimes(1);
      expect(handleClick).toHaveBeenCalledWith(mockEvent);
    });

    it('should not throw error when onClick is not provided', async () => {
      const user = userEvent.setup();

      render(<EventCard event={mockEvent} />);

      await expect(async () => {
        await user.click(screen.getByText('Birthday Party'));
      }).not.toThrow();
    });

    it('should be interactive (use Card with interactive prop)', () => {
      const { container } = render(<EventCard event={mockEvent} onClick={() => {}} />);

      // Card component should have interactive class
      const card = container.firstChild;
      expect(card).toHaveClass('cursor-pointer');
    });
  });

  describe('Layout', () => {
    it('should have proper structure', () => {
      const { container } = render(<EventCard event={mockEvent} />);

      const flexCol = container.querySelector('.flex.flex-col');
      expect(flexCol).toBeInTheDocument();
    });

    it('should have bottom section with dots and progress', () => {
      const { container } = render(<EventCard event={mockEvent} />);

      const bottomSection = container.querySelector('.flex.items-center.justify-between');
      expect(bottomSection).toBeInTheDocument();
    });

    it('should have margin bottom on card', () => {
      const { container } = render(<EventCard event={mockEvent} />);

      const card = container.firstChild;
      expect(card).toHaveClass('mb-3');
    });
  });

  describe('Different Event Scenarios', () => {
    it('should render event with 0% progress', () => {
      const event = { ...mockEvent, progress: 0 };
      render(<EventCard event={event} />);

      expect(screen.getByText('0% done')).toBeInTheDocument();
    });

    it('should render event with 100% progress', () => {
      const event = { ...mockEvent, progress: 100 };
      render(<EventCard event={event} />);

      expect(screen.getByText('100% done')).toBeInTheDocument();
    });

    it('should render different event names', () => {
      const event = { ...mockEvent, name: 'Wedding Ceremony' };
      render(<EventCard event={event} />);

      expect(screen.getByText('Wedding Ceremony')).toBeInTheDocument();
    });

    it('should render different icons', () => {
      const event = { ...mockEvent, icon: '🎨' };
      render(<EventCard event={event} />);

      expect(screen.getByText('🎨')).toBeInTheDocument();
    });
  });

  describe('Text Styling', () => {
    it('should have correct heading styles', () => {
      render(<EventCard event={mockEvent} />);

      const heading = screen.getByText('Birthday Party');
      expect(heading).toHaveClass('font-semibold');
      expect(heading).toHaveClass('text-lg');
      expect(heading).toHaveClass('mb-1');
    });

    it('should have correct date text styles', () => {
      render(<EventCard event={mockEvent} />);

      const dateText = screen.getByText('Mocked Date');
      expect(dateText).toHaveClass('text-sm');
      expect(dateText).toHaveClass('text-gray');
      expect(dateText).toHaveClass('mb-3');
    });

    it('should have correct icon size', () => {
      const { container } = render(<EventCard event={mockEvent} />);

      const icon = container.querySelector('.text-2xl');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveTextContent('🎂');
    });
  });

  describe('Edge Cases', () => {
    it('should handle missing event properties gracefully', () => {
      const minimalEvent = {
        id: '1',
        name: 'Minimal Event',
        date: '2024-06-15',
        progress: 50,
        status: 'active',
      };

      render(<EventCard event={minimalEvent} />);

      expect(screen.getByText('Minimal Event')).toBeInTheDocument();
      expect(screen.getByText('🎉')).toBeInTheDocument(); // Default icon
    });

    it('should handle progress at boundaries (20, 40, 60, 80, 100)', () => {
      const boundaries = [20, 40, 60, 80, 100];

      boundaries.forEach((progress) => {
        const event = { ...mockEvent, progress };
        const { container, unmount } = render(<EventCard event={event} />);

        const expectedDots = Math.floor(progress / 20);
        const filledDots = container.querySelectorAll('.w-2.h-2.rounded-full.bg-success');

        expect(filledDots).toHaveLength(expectedDots);
        unmount();
      });
    });
  });
});
