import { useState, useEffect, useCallback, useMemo } from 'react';
import subscriptionService from '../services/subscriptionService';
import { getErrorMessage } from '../api/client';

/**
 * useSubscription - Custom hook for subscription data management
 *
 * Features:
 * - Get current plan and usage limits
 * - View billing history
 * - Upgrade/downgrade plans
 * - Manage payment methods
 *
 * Usage:
 * const { subscription, loading, error, upgrade, downgrade } = useSubscription();
 */

export const useSubscription = () => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSubscription = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [status, plan, limits] = await Promise.all([
        subscriptionService.getStatus(),
        subscriptionService.getCurrentPlan(),
        subscriptionService.getUsageLimits(),
      ]);
      setSubscription({
        status,
        plan,
        limits,
      });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSubscription();
  }, [fetchSubscription]);

  const upgrade = useCallback(async (planId) => {
    try {
      const result = await subscriptionService.upgrade(planId);
      await fetchSubscription(); // Refetch to get updated data
      return result;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [fetchSubscription]);

  const downgrade = useCallback(async (planId) => {
    try {
      const result = await subscriptionService.downgrade(planId);
      await fetchSubscription(); // Refetch to get updated data
      return result;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [fetchSubscription]);

  const cancel = useCallback(async () => {
    try {
      const result = await subscriptionService.cancel();
      await fetchSubscription(); // Refetch to get updated data
      return result;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [fetchSubscription]);

  return {
    subscription,
    loading,
    error,
    upgrade,
    downgrade,
    cancel,
    refetch: fetchSubscription,
  };
};

/**
 * useUsageLimits - Custom hook specifically for usage limits
 *
 * Usage:
 * const { limits, loading, error, refetch } = useUsageLimits();
 */

export const useUsageLimits = (orgId = null) => {
  const [limits, setLimits] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLimits = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await subscriptionService.getUsageLimits(orgId);
      setLimits(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    fetchLimits();
  }, [fetchLimits]);

  return {
    limits,
    loading,
    error,
    refetch: fetchLimits,
  };
};

/**
 * useBillingHistory - Custom hook for billing history
 *
 * Usage:
 * const { history, loading, error, refetch } = useBillingHistory();
 */

export const useBillingHistory = (filters = {}) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Stabilize filters object to prevent infinite loops
  const stableFilters = useMemo(() => filters, [JSON.stringify(filters)]);

  const fetchHistory = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await subscriptionService.getBillingHistory(stableFilters);
      setHistory(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [stableFilters]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    history,
    loading,
    error,
    refetch: fetchHistory,
  };
};

/**
 * useAvailablePlans - Custom hook for available subscription plans
 *
 * Usage:
 * const { plans, loading, error } = useAvailablePlans();
 */

export const useAvailablePlans = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await subscriptionService.getAvailablePlans();
        setPlans(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  return {
    plans,
    loading,
    error,
  };
};

/**
 * useUsageStats - Custom hook for usage statistics
 *
 * Usage:
 * const { stats, loading, error, refetch } = useUsageStats();
 */

export const useUsageStats = (orgId = null) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await subscriptionService.getUsageStats(orgId);
      setStats(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
};
