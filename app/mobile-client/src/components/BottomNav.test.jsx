import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BottomNav } from './BottomNav';
import { BrowserRouter } from 'react-router-dom';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Home: ({ size }) => <span data-testid="home-icon" data-size={size} aria-hidden="true" />,
  Calendar: ({ size }) => <span data-testid="calendar-icon" data-size={size} aria-hidden="true" />,
  MessageCircle: ({ size }) => <span data-testid="message-icon" data-size={size} aria-hidden="true" />,
  User: ({ size }) => <span data-testid="user-icon" data-size={size} aria-hidden="true" />,
}));

const renderWithRouter = (initialPath = '/') => {
  window.history.pushState({}, 'Test page', initialPath);

  return render(
    <BrowserRouter>
      <BottomNav />
    </BrowserRouter>
  );
};

describe('BottomNav Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render navigation bar', () => {
      renderWithRouter();

      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    it('should render all 4 navigation items', () => {
      renderWithRouter();

      expect(screen.getAllByRole('button')).toHaveLength(4);
    });

    it('should render Home button', () => {
      renderWithRouter();

      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByTestId('home-icon')).toBeInTheDocument();
    });

    it('should render Calendar button', () => {
      renderWithRouter();

      expect(screen.getByText('Calendar')).toBeInTheDocument();
      expect(screen.getByTestId('calendar-icon')).toBeInTheDocument();
    });

    it('should render Chat button', () => {
      renderWithRouter();

      expect(screen.getByText('Chat')).toBeInTheDocument();
      expect(screen.getByTestId('message-icon')).toBeInTheDocument();
    });

    it('should render Profile button', () => {
      renderWithRouter();

      expect(screen.getByText('Profile')).toBeInTheDocument();
      expect(screen.getByTestId('user-icon')).toBeInTheDocument();
    });
  });

  describe('Icon Sizes', () => {
    it('should render icons with size 24', () => {
      renderWithRouter();

      const icons = [
        screen.getByTestId('home-icon'),
        screen.getByTestId('calendar-icon'),
        screen.getByTestId('message-icon'),
        screen.getByTestId('user-icon'),
      ];

      icons.forEach((icon) => {
        expect(icon).toHaveAttribute('data-size', '24');
      });
    });
  });

  describe('Active State - Home', () => {
    it('should highlight Home when on /home', () => {
      renderWithRouter('/home');

      const homeButton = screen.getByText('Home').closest('button');
      expect(homeButton).toHaveClass('text-primary');
    });

    it('should not highlight other buttons when on /home', () => {
      renderWithRouter('/home');

      const calendarButton = screen.getByText('Calendar').closest('button');
      const chatButton = screen.getByText('Chat').closest('button');
      const profileButton = screen.getByText('Profile').closest('button');

      expect(calendarButton).toHaveClass('text-gray');
      expect(chatButton).toHaveClass('text-gray');
      expect(profileButton).toHaveClass('text-gray');
    });
  });

  describe('Active State - Calendar', () => {
    it('should highlight Calendar when on /calendar', () => {
      renderWithRouter('/calendar');

      const calendarButton = screen.getByText('Calendar').closest('button');
      expect(calendarButton).toHaveClass('text-primary');
    });
  });

  describe('Active State - Chat', () => {
    it('should highlight Chat when on /chat', () => {
      renderWithRouter('/chat');

      const chatButton = screen.getByText('Chat').closest('button');
      expect(chatButton).toHaveClass('text-primary');
    });

    it('should highlight Chat when on root path /', () => {
      renderWithRouter('/');

      const chatButton = screen.getByText('Chat').closest('button');
      expect(chatButton).toHaveClass('text-primary');
    });
  });

  describe('Active State - Profile', () => {
    it('should highlight Profile when on /profile', () => {
      renderWithRouter('/profile');

      const profileButton = screen.getByText('Profile').closest('button');
      expect(profileButton).toHaveClass('text-primary');
    });
  });

  describe('Navigation', () => {
    it('should navigate to Home when Home button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter('/chat');

      await user.click(screen.getByText('Home'));

      expect(window.location.pathname).toBe('/home');
    });

    it('should navigate to Calendar when Calendar button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter('/');

      await user.click(screen.getByText('Calendar'));

      expect(window.location.pathname).toBe('/calendar');
    });

    it('should navigate to Chat when Chat button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter('/home');

      await user.click(screen.getByText('Chat'));

      expect(window.location.pathname).toBe('/chat');
    });

    it('should navigate to Profile when Profile button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter('/');

      await user.click(screen.getByText('Profile'));

      expect(window.location.pathname).toBe('/profile');
    });
  });

  describe('Styling', () => {
    it('should be fixed at bottom', () => {
      const { container } = renderWithRouter();

      const nav = container.querySelector('nav');
      expect(nav).toHaveClass('fixed');
      expect(nav).toHaveClass('bottom-0');
      expect(nav).toHaveClass('left-0');
      expect(nav).toHaveClass('right-0');
    });

    it('should have white background', () => {
      const { container } = renderWithRouter();

      const nav = container.querySelector('nav');
      expect(nav).toHaveClass('bg-white');
    });

    it('should have border on top', () => {
      const { container } = renderWithRouter();

      const nav = container.querySelector('nav');
      expect(nav).toHaveClass('border-t');
      expect(nav).toHaveClass('border-gray-light');
    });

    it('should have shadow', () => {
      const { container } = renderWithRouter();

      const nav = container.querySelector('nav');
      expect(nav).toHaveClass('shadow-lg');
    });

    it('should have safe area bottom padding', () => {
      const { container } = renderWithRouter();

      const nav = container.querySelector('nav');
      expect(nav).toHaveClass('safe-area-bottom');
    });

    it('should have transition classes', () => {
      const { container } = renderWithRouter();

      const nav = container.querySelector('nav');
      expect(nav).toHaveClass('transition-colors');
    });
  });

  describe('Dark Mode Classes', () => {
    it('should have dark mode background class', () => {
      const { container } = renderWithRouter();

      const nav = container.querySelector('nav');
      expect(nav.className).toContain('dark:bg-dark-bg-secondary');
    });

    it('should have dark mode border class', () => {
      const { container } = renderWithRouter();

      const nav = container.querySelector('nav');
      expect(nav.className).toContain('dark:border-dark-bg-tertiary');
    });

    it('should have dark mode text colors for inactive items', () => {
      renderWithRouter('/home');

      const chatButton = screen.getByText('Chat').closest('button');
      expect(chatButton.className).toContain('dark:text-dark-text-secondary');
    });

    it('should have dark mode text colors for active items', () => {
      renderWithRouter('/home');

      const homeButton = screen.getByText('Home').closest('button');
      expect(homeButton.className).toContain('dark:text-primary-light');
    });
  });

  describe('Button Layout', () => {
    it('should have flex layout with space-around', () => {
      const { container } = renderWithRouter();

      const buttonContainer = container.querySelector('.flex.justify-around');
      expect(buttonContainer).toBeInTheDocument();
    });

    it('should have vertical flex layout for each button', () => {
      renderWithRouter();

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toHaveClass('flex');
        expect(button).toHaveClass('flex-col');
        expect(button).toHaveClass('items-center');
      });
    });

    it('should have gap between icon and label', () => {
      renderWithRouter();

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toHaveClass('gap-1');
      });
    });

    it('should have padding on buttons', () => {
      renderWithRouter();

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toHaveClass('px-4');
        expect(button).toHaveClass('py-2');
      });
    });
  });

  describe('Label Styling', () => {
    it('should have correct text size for labels', () => {
      renderWithRouter();

      const labels = ['Home', 'Calendar', 'Chat', 'Profile'];
      labels.forEach((label) => {
        const element = screen.getByText(label);
        expect(element).toHaveClass('text-xs');
        expect(element).toHaveClass('font-medium');
      });
    });
  });

  describe('Accessibility', () => {
    it('should have role navigation', () => {
      renderWithRouter();

      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    it('should have button role for each item', () => {
      renderWithRouter();

      expect(screen.getAllByRole('button')).toHaveLength(4);
    });

    it('should be keyboard navigable', async () => {
      const user = userEvent.setup();
      renderWithRouter('/');

      const homeButton = screen.getByText('Home').closest('button');
      homeButton.focus();

      expect(document.activeElement).toBe(homeButton);

      await user.keyboard('{Tab}');
      expect(document.activeElement).toBe(screen.getByText('Calendar').closest('button'));

      await user.keyboard('{Tab}');
      expect(document.activeElement).toBe(screen.getByText('Chat').closest('button'));

      await user.keyboard('{Tab}');
      expect(document.activeElement).toBe(screen.getByText('Profile').closest('button'));
    });
  });

  describe('Transition Classes', () => {
    it('should have transition on buttons', () => {
      renderWithRouter();

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toHaveClass('transition-colors');
      });
    });
  });
});
