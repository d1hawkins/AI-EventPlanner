import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react';
import { ToastProvider, useToast } from './useToast';

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

describe('ToastProvider', () => {
  beforeEach(() => {
    vi.clearAllTimers();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('should render children', () => {
      render(
        <ToastProvider>
          <div data-testid="child">Child Component</div>
        </ToastProvider>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
    });
  });

  describe('useToast Hook', () => {
    it('should throw error when used outside provider', () => {
      const consoleError = console.error;
      console.error = vi.fn();

      expect(() => {
        renderHook(() => useToast());
      }).toThrow('useToast must be used within ToastProvider');

      console.error = consoleError;
    });

    it('should provide toast methods within provider', () => {
      const { result } = renderHook(() => useToast(), {
        wrapper: ToastProvider,
      });

      expect(result.current).toHaveProperty('success');
      expect(result.current).toHaveProperty('error');
      expect(result.current).toHaveProperty('info');
      expect(result.current).toHaveProperty('warning');
      expect(result.current).toHaveProperty('dismiss');
    });
  });

  describe('Toast Notifications', () => {
    it('should show success toast', () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.success('Success message')}>
            Show Success
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByText('Show Success').click();
      });

      expect(screen.getByText('Success message')).toBeInTheDocument();
    });

    it('should show error toast', () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.error('Error message')}>
            Show Error
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByText('Show Error').click();
      });

      expect(screen.getByText('Error message')).toBeInTheDocument();
    });

    it('should show info toast', () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.info('Info message')}>
            Show Info
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByText('Show Info').click();
      });

      expect(screen.getByText('Info message')).toBeInTheDocument();
    });

    it('should show warning toast', () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.warning('Warning message')}>
            Show Warning
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByText('Show Warning').click();
      });

      expect(screen.getByText('Warning message')).toBeInTheDocument();
    });

    it('should show multiple toasts', () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button
            onClick={() => {
              toast.success('First');
              toast.error('Second');
              toast.info('Third');
            }}
          >
            Show Multiple
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByText('Show Multiple').click();
      });

      expect(screen.getByText('First')).toBeInTheDocument();
      expect(screen.getByText('Second')).toBeInTheDocument();
      expect(screen.getByText('Third')).toBeInTheDocument();
    });
  });

  describe('Auto Dismiss', () => {
    it('should auto dismiss toast after default duration', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.success('Auto dismiss')}>
            Show Toast
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      const button = screen.getByText('Show Toast');
      await act(async () => {
        button.click();
      });

      expect(screen.getByText('Auto dismiss')).toBeInTheDocument();

      await act(async () => {
        vi.advanceTimersByTime(3000);
      });

      expect(screen.queryByText('Auto dismiss')).not.toBeInTheDocument();
    });

    it('should auto dismiss toast after custom duration', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.success('Custom duration', 5000)}>
            Show Toast
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      const button = screen.getByText('Show Toast');
      await act(async () => {
        button.click();
      });

      expect(screen.getByText('Custom duration')).toBeInTheDocument();

      await act(async () => {
        vi.advanceTimersByTime(3000);
      });

      expect(screen.getByText('Custom duration')).toBeInTheDocument();

      await act(async () => {
        vi.advanceTimersByTime(2000);
      });

      expect(screen.queryByText('Custom duration')).not.toBeInTheDocument();
    });

    it('should not auto dismiss if duration is 0', () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.success('No auto dismiss', 0)}>
            Show Toast
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      act(() => {
        screen.getByText('Show Toast').click();
      });

      expect(screen.getByText('No auto dismiss')).toBeInTheDocument();

      act(() => {
        vi.advanceTimersByTime(10000);
      });

      expect(screen.getByText('No auto dismiss')).toBeInTheDocument();
    });
  });

  describe('Manual Dismiss', () => {
    it('should dismiss toast when dismiss button is clicked', async () => {
      const TestComponent = () => {
        const toast = useToast();
        return (
          <button onClick={() => toast.success('Dismissible')}>
            Show Toast
          </button>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      const showButton = screen.getByText('Show Toast');
      await act(async () => {
        showButton.click();
      });

      expect(screen.getByText('Dismissible')).toBeInTheDocument();

      const dismissButton = screen.getByLabelText('Dismiss');
      await act(async () => {
        dismissButton.click();
      });

      expect(screen.queryByText('Dismissible')).not.toBeInTheDocument();
    });

    it('should dismiss specific toast by ID', async () => {
      let capturedId;
      const TestComponent = () => {
        const toast = useToast();
        return (
          <div>
            <button
              onClick={() => {
                capturedId = toast.success('Specific toast', 0);
              }}
            >
              Show Toast
            </button>
            <button onClick={() => toast.dismiss(capturedId)}>
              Dismiss
            </button>
          </div>
        );
      };

      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      const showButton = screen.getByText('Show Toast');
      await act(async () => {
        showButton.click();
      });

      expect(screen.getByText('Specific toast')).toBeInTheDocument();

      const dismissButton = screen.getByText('Dismiss');
      await act(async () => {
        dismissButton.click();
      });

      expect(screen.queryByText('Specific toast')).not.toBeInTheDocument();
    });
  });

  describe('Toast Return Value', () => {
    it('should return toast ID', () => {
      const { result } = renderHook(() => useToast(), {
        wrapper: ToastProvider,
      });

      let toastId;
      act(() => {
        toastId = result.current.success('Test');
      });

      expect(typeof toastId).toBe('number');
    });

    it('should return unique IDs for different toasts', () => {
      const { result } = renderHook(() => useToast(), {
        wrapper: ToastProvider,
      });

      let id1, id2, id3;
      act(() => {
        id1 = result.current.success('First');
        id2 = result.current.error('Second');
        id3 = result.current.info('Third');
      });

      expect(id1).not.toBe(id2);
      expect(id2).not.toBe(id3);
      expect(id1).not.toBe(id3);
    });
  });
});
