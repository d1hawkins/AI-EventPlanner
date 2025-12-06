import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import {
  useSubscription,
  useUsageLimits,
  useBillingHistory,
  useAvailablePlans,
  useUsageStats,
} from './useSubscription';
import subscriptionService from '../services/subscriptionService';
import {
  mockSubscription,
  mockPlan,
  mockPlans,
  mockUsage,
  mockBillingHistory,
} from '../test/mockData';

// Mock the subscription service
vi.mock('../services/subscriptionService', () => ({
  default: {
    getStatus: vi.fn(),
    getCurrentPlan: vi.fn(),
    upgrade: vi.fn(),
    downgrade: vi.fn(),
    cancel: vi.fn(),
    getUsageLimits: vi.fn(),
    getBillingHistory: vi.fn(),
    getAvailablePlans: vi.fn(),
    getUsageStats: vi.fn(),
    updatePaymentMethod: vi.fn(),
    processPayment: vi.fn(),
  },
}));

describe('useSubscription', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(mockPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);

      const { result } = renderHook(() => useSubscription());

      expect(result.current.subscription).toBeNull();
      expect(result.current.loading).toBe(true);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Fetching Subscription', () => {
    it('should fetch subscription data on mount', async () => {
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(mockPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);

      const { result } = renderHook(() => useSubscription());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(subscriptionService.getStatus).toHaveBeenCalled();
      expect(subscriptionService.getCurrentPlan).toHaveBeenCalled();
      expect(subscriptionService.getUsageLimits).toHaveBeenCalled();
      expect(result.current.subscription).toEqual({
        status: mockSubscription,
        plan: mockPlan,
        limits: mockUsage,
      });
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch subscription');
      subscriptionService.getStatus.mockRejectedValue(error);

      const { result } = renderHook(() => useSubscription());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.subscription).toBeNull();
      expect(result.current.error).toBe('Failed to fetch subscription');
    });
  });

  describe('Upgrading Subscription', () => {
    it('should upgrade subscription and refetch', async () => {
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(mockPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);
      subscriptionService.upgrade.mockResolvedValue({ plan_id: 'pro' });

      const { result } = renderHook(() => useSubscription());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      vi.clearAllMocks();

      const upgradedPlan = { ...mockPlan, name: 'Pro' };
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(upgradedPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);

      await act(async () => {
        await result.current.upgrade('pro');
      });

      expect(subscriptionService.upgrade).toHaveBeenCalledWith('pro');
      expect(subscriptionService.getStatus).toHaveBeenCalled();
      expect(subscriptionService.getCurrentPlan).toHaveBeenCalled();
      expect(subscriptionService.getUsageLimits).toHaveBeenCalled();
    });

    it('should throw error on upgrade failure', async () => {
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(mockPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);
      const error = new Error('Upgrade failed');
      subscriptionService.upgrade.mockRejectedValue(error);

      const { result } = renderHook(() => useSubscription());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.upgrade('pro');
        });
      }).rejects.toThrow('Upgrade failed');
    });
  });

  describe('Downgrading Subscription', () => {
    it('should downgrade subscription and refetch', async () => {
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(mockPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);
      subscriptionService.downgrade.mockResolvedValue({ plan_id: 'basic' });

      const { result } = renderHook(() => useSubscription());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      vi.clearAllMocks();

      const downgradedPlan = { ...mockPlan, name: 'Basic' };
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(downgradedPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);

      await act(async () => {
        await result.current.downgrade('basic');
      });

      expect(subscriptionService.downgrade).toHaveBeenCalledWith('basic');
    });

    it('should throw error on downgrade failure', async () => {
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(mockPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);
      const error = new Error('Downgrade failed');
      subscriptionService.downgrade.mockRejectedValue(error);

      const { result } = renderHook(() => useSubscription());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.downgrade('basic');
        });
      }).rejects.toThrow('Downgrade failed');
    });
  });

  describe('Canceling Subscription', () => {
    it('should cancel subscription and refetch', async () => {
      subscriptionService.getStatus.mockResolvedValue(mockSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(mockPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);
      subscriptionService.cancel.mockResolvedValue({ cancelled: true });

      const { result } = renderHook(() => useSubscription());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      vi.clearAllMocks();

      const cancelledSubscription = { ...mockSubscription, status: 'cancelled' };
      subscriptionService.getStatus.mockResolvedValue(cancelledSubscription);
      subscriptionService.getCurrentPlan.mockResolvedValue(mockPlan);
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);

      await act(async () => {
        await result.current.cancel();
      });

      expect(subscriptionService.cancel).toHaveBeenCalled();
    });
  });
});

describe('useUsageLimits', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Usage Limits', () => {
    it('should fetch usage limits on mount', async () => {
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);
      const { result } = renderHook(() => useUsageLimits());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(subscriptionService.getUsageLimits).toHaveBeenCalledWith(null);
      expect(result.current.limits).toEqual(mockUsage);
    });

    it('should fetch limits with org ID', async () => {
      subscriptionService.getUsageLimits.mockResolvedValue(mockUsage);
      const { result } = renderHook(() => useUsageLimits('org-123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(subscriptionService.getUsageLimits).toHaveBeenCalledWith('org-123');
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch limits');
      subscriptionService.getUsageLimits.mockRejectedValue(error);
      const { result } = renderHook(() => useUsageLimits());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.limits).toBeNull();
      expect(result.current.error).toBe('Failed to fetch limits');
    });
  });
});

describe('useBillingHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Billing History', () => {
    it('should fetch billing history on mount', async () => {
      subscriptionService.getBillingHistory.mockResolvedValue(mockBillingHistory);
      const { result } = renderHook(() => useBillingHistory());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(subscriptionService.getBillingHistory).toHaveBeenCalledWith({});
      expect(result.current.history).toEqual(mockBillingHistory);
    });

    it('should fetch history with filters', async () => {
      const filters = { limit: 10, offset: 0 };
      subscriptionService.getBillingHistory.mockResolvedValue(mockBillingHistory);
      const { result } = renderHook(() => useBillingHistory(filters));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(subscriptionService.getBillingHistory).toHaveBeenCalledWith(filters);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch history');
      subscriptionService.getBillingHistory.mockRejectedValue(error);
      const { result } = renderHook(() => useBillingHistory());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.history).toEqual([]);
      expect(result.current.error).toBe('Failed to fetch history');
    });
  });
});

describe('useAvailablePlans', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Available Plans', () => {
    it('should fetch available plans on mount', async () => {
      subscriptionService.getAvailablePlans.mockResolvedValue(mockPlans);
      const { result } = renderHook(() => useAvailablePlans());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(subscriptionService.getAvailablePlans).toHaveBeenCalled();
      expect(result.current.plans).toEqual(mockPlans);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch plans');
      subscriptionService.getAvailablePlans.mockRejectedValue(error);
      const { result } = renderHook(() => useAvailablePlans());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.plans).toEqual([]);
      expect(result.current.error).toBe('Failed to fetch plans');
    });
  });
});

describe('useUsageStats', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Usage Stats', () => {
    it('should fetch usage stats on mount', async () => {
      subscriptionService.getUsageStats.mockResolvedValue(mockUsage);
      const { result } = renderHook(() => useUsageStats());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(subscriptionService.getUsageStats).toHaveBeenCalledWith(null);
      expect(result.current.stats).toEqual(mockUsage);
    });

    it('should fetch stats with org ID', async () => {
      subscriptionService.getUsageStats.mockResolvedValue(mockUsage);
      const { result } = renderHook(() => useUsageStats('org-123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(subscriptionService.getUsageStats).toHaveBeenCalledWith('org-123');
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch stats');
      subscriptionService.getUsageStats.mockRejectedValue(error);
      const { result } = renderHook(() => useUsageStats());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.stats).toBeNull();
      expect(result.current.error).toBe('Failed to fetch stats');
    });
  });
});
