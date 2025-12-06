import { describe, it, expect, beforeEach, vi } from 'vitest';
import subscriptionService from './subscriptionService';
import apiClient from '../api/client';
import {
  mockSubscription,
  mockPlan,
  mockPlans,
  mockUsage,
  mockBillingHistory,
} from '../test/mockData';

// Mock the API client
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('subscriptionService', () => {
  const mockOrgId = 'org-123';

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('organizationId', mockOrgId);
  });

  describe('getOrganizationId', () => {
    it('should retrieve organization ID from localStorage', () => {
      const orgId = subscriptionService.getOrganizationId();
      expect(orgId).toBe(mockOrgId);
    });

    it('should return null if no organization ID in localStorage', () => {
      localStorage.clear();
      const orgId = subscriptionService.getOrganizationId();
      expect(orgId).toBeNull();
    });
  });

  describe('getUsageLimits', () => {
    it('should fetch usage limits using stored org ID', async () => {
      apiClient.get.mockResolvedValue({ data: mockUsage });

      const result = await subscriptionService.getUsageLimits();

      expect(apiClient.get).toHaveBeenCalledWith(
        `/subscription/organizations/${mockOrgId}/usage-limits`
      );
      expect(result).toEqual(mockUsage);
    });

    it('should fetch usage limits with custom org ID', async () => {
      const customOrgId = 'custom-org';
      apiClient.get.mockResolvedValue({ data: mockUsage });

      const result = await subscriptionService.getUsageLimits(customOrgId);

      expect(apiClient.get).toHaveBeenCalledWith(
        `/subscription/organizations/${customOrgId}/usage-limits`
      );
      expect(result).toEqual(mockUsage);
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(subscriptionService.getUsageLimits()).rejects.toThrow(
        'Organization ID is required'
      );
    });
  });

  describe('getStatus', () => {
    it('should fetch subscription status', async () => {
      apiClient.get.mockResolvedValue({ data: mockSubscription });

      const result = await subscriptionService.getStatus();

      expect(apiClient.get).toHaveBeenCalledWith('/subscription/status');
      expect(result).toEqual(mockSubscription);
    });
  });

  describe('getCurrentPlan', () => {
    it('should fetch current plan details', async () => {
      apiClient.get.mockResolvedValue({ data: mockPlan });

      const result = await subscriptionService.getCurrentPlan();

      expect(apiClient.get).toHaveBeenCalledWith('/subscription/plan');
      expect(result).toEqual(mockPlan);
    });
  });

  describe('getAvailablePlans', () => {
    it('should fetch all available plans', async () => {
      apiClient.get.mockResolvedValue({ data: mockPlans });

      const result = await subscriptionService.getAvailablePlans();

      expect(apiClient.get).toHaveBeenCalledWith('/subscription/plans');
      expect(result).toEqual(mockPlans);
    });
  });

  describe('getBillingHistory', () => {
    it('should fetch billing history without filters', async () => {
      apiClient.get.mockResolvedValue({ data: mockBillingHistory });

      const result = await subscriptionService.getBillingHistory();

      expect(apiClient.get).toHaveBeenCalledWith('/subscription/billing-history?');
      expect(result).toEqual(mockBillingHistory);
    });

    it('should fetch billing history with limit filter', async () => {
      const filters = { limit: 10 };
      apiClient.get.mockResolvedValue({ data: mockBillingHistory });

      const result = await subscriptionService.getBillingHistory(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/subscription/billing-history?limit=10');
      expect(result).toEqual(mockBillingHistory);
    });

    it('should fetch billing history with offset filter', async () => {
      const filters = { offset: 20 };
      apiClient.get.mockResolvedValue({ data: mockBillingHistory });

      await subscriptionService.getBillingHistory(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/subscription/billing-history?offset=20');
    });

    it('should fetch billing history with multiple filters', async () => {
      const filters = { limit: 10, offset: 20 };
      apiClient.get.mockResolvedValue({ data: mockBillingHistory });

      await subscriptionService.getBillingHistory(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/subscription/billing-history?limit=10&offset=20');
    });
  });

  describe('upgrade', () => {
    it('should upgrade subscription to a new plan', async () => {
      const planId = 'pro-plan';
      const upgradedSubscription = { ...mockSubscription, plan_id: planId };
      apiClient.post.mockResolvedValue({ data: upgradedSubscription });

      const result = await subscriptionService.upgrade(planId);

      expect(apiClient.post).toHaveBeenCalledWith('/subscription/upgrade', { plan_id: planId });
      expect(result).toEqual(upgradedSubscription);
    });
  });

  describe('downgrade', () => {
    it('should downgrade subscription to a new plan', async () => {
      const planId = 'basic-plan';
      const downgradedSubscription = { ...mockSubscription, plan_id: planId };
      apiClient.post.mockResolvedValue({ data: downgradedSubscription });

      const result = await subscriptionService.downgrade(planId);

      expect(apiClient.post).toHaveBeenCalledWith('/subscription/downgrade', { plan_id: planId });
      expect(result).toEqual(downgradedSubscription);
    });
  });

  describe('cancel', () => {
    it('should cancel subscription', async () => {
      const cancellationData = { success: true, cancelled_at: '2024-12-31' };
      apiClient.post.mockResolvedValue({ data: cancellationData });

      const result = await subscriptionService.cancel();

      expect(apiClient.post).toHaveBeenCalledWith('/subscription/cancel');
      expect(result).toEqual(cancellationData);
    });
  });

  describe('getPaymentMethod', () => {
    it('should fetch payment method details', async () => {
      const paymentMethod = {
        type: 'card',
        last4: '4242',
        exp_month: 12,
        exp_year: 2025,
      };
      apiClient.get.mockResolvedValue({ data: paymentMethod });

      const result = await subscriptionService.getPaymentMethod();

      expect(apiClient.get).toHaveBeenCalledWith('/subscription/payment-method');
      expect(result).toEqual(paymentMethod);
    });
  });

  describe('updatePaymentMethod', () => {
    it('should update payment method', async () => {
      const paymentData = {
        token: 'tok_visa',
        type: 'card',
      };
      const updatedPaymentMethod = {
        type: 'card',
        last4: '4242',
        exp_month: 12,
        exp_year: 2025,
      };
      apiClient.put.mockResolvedValue({ data: updatedPaymentMethod });

      const result = await subscriptionService.updatePaymentMethod(paymentData);

      expect(apiClient.put).toHaveBeenCalledWith('/subscription/payment-method', paymentData);
      expect(result).toEqual(updatedPaymentMethod);
    });
  });

  describe('getUsageStats', () => {
    it('should fetch usage statistics using stored org ID', async () => {
      apiClient.get.mockResolvedValue({ data: mockUsage });

      const result = await subscriptionService.getUsageStats();

      expect(apiClient.get).toHaveBeenCalledWith(
        `/subscription/organizations/${mockOrgId}/usage`
      );
      expect(result).toEqual(mockUsage);
    });

    it('should fetch usage statistics with custom org ID', async () => {
      const customOrgId = 'custom-org';
      apiClient.get.mockResolvedValue({ data: mockUsage });

      const result = await subscriptionService.getUsageStats(customOrgId);

      expect(apiClient.get).toHaveBeenCalledWith(
        `/subscription/organizations/${customOrgId}/usage`
      );
      expect(result).toEqual(mockUsage);
    });

    it('should throw error if no organization ID available', async () => {
      localStorage.clear();

      await expect(subscriptionService.getUsageStats()).rejects.toThrow(
        'Organization ID is required'
      );
    });
  });
});
