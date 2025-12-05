import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CreditCard, Download, Receipt, Calendar, AlertCircle } from 'lucide-react';
import { useSubscription, useUsageLimits, useBillingHistory, useAvailablePlans } from '../hooks/useSubscription';
import { PlanCard } from '../components/subscription/PlanCard';
import { UsageCard } from '../components/subscription/UsageCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { useToast } from '../hooks/useToast';
import { motion } from 'framer-motion';

/**
 * SubscriptionPage - Subscription management page
 *
 * Features:
 * - View current plan
 * - Usage metrics and limits
 * - Available plans
 * - Plan upgrade/downgrade
 * - Billing history
 * - Payment method management
 */

export const SubscriptionPage = () => {
  const navigate = useNavigate();
  const toast = useToast();

  const { subscription, loading: subLoading, error: subError, upgrade, downgrade, cancelSubscription, refetch } = useSubscription();
  const { usage, loading: usageLoading } = useUsageLimits();
  const { history, loading: historyLoading } = useBillingHistory();
  const { plans, loading: plansLoading } = useAvailablePlans();

  const [selectedPlan, setSelectedPlan] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [cancelLoading, setCancelLoading] = useState(false);
  const [showPlans, setShowPlans] = useState(false);

  const handlePlanSelect = async (plan) => {
    if (!subscription) return;

    const currentPlanName = subscription.plan_name?.toLowerCase();
    const newPlanName = plan.name.toLowerCase();

    // Don't proceed if selecting current plan
    if (currentPlanName === newPlanName) return;

    setSelectedPlan(plan);

    try {
      setActionLoading(true);

      // Determine if upgrade or downgrade
      const planOrder = { free: 0, pro: 1, enterprise: 2 };
      const currentOrder = planOrder[currentPlanName] || 0;
      const newOrder = planOrder[newPlanName] || 0;

      if (newOrder > currentOrder) {
        await upgrade(plan.id);
        toast.success(`Successfully upgraded to ${plan.name}!`);
      } else {
        await downgrade(plan.id);
        toast.success(`Successfully changed to ${plan.name}`);
      }

      setShowPlans(false);
    } catch (err) {
      toast.error(err.message || 'Failed to change plan');
    } finally {
      setActionLoading(false);
      setSelectedPlan(null);
    }
  };

  const handleCancelSubscription = async () => {
    try {
      setCancelLoading(true);
      await cancelSubscription();
      toast.success('Subscription cancelled successfully');
      setShowCancelDialog(false);
    } catch (err) {
      toast.error(err.message || 'Failed to cancel subscription');
    } finally {
      setCancelLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  if (subLoading || plansLoading) {
    return <LoadingSpinner fullPage message="Loading subscription..." />;
  }

  if (subError) {
    return (
      <ErrorMessage
        variant="fullPage"
        title="Failed to load subscription"
        message={subError}
        retry={refetch}
      />
    );
  }

  const currentPlanName = subscription?.plan_name?.toLowerCase();
  const isOnFreePlan = currentPlanName === 'free';
  const canCancel = subscription?.status === 'active' && !isOnFreePlan;

  return (
    <div className="min-h-screen bg-gray-bg dark:bg-dark-bg-primary pb-20 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-dark-bg-secondary border-b border-gray-200 dark:border-dark-bg-tertiary px-4 py-4 sticky top-0 z-10 transition-colors">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft size={24} className="text-gray-700 dark:text-dark-text-primary" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary transition-colors">
                Subscription
              </h1>
              <p className="text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">
                Manage your plan and billing
              </p>
            </div>
          </div>

          {canCancel && (
            <button
              onClick={() => setShowCancelDialog(true)}
              className="text-sm text-red-600 dark:text-red-400 hover:underline"
            >
              Cancel
            </button>
          )}
        </div>
      </header>

      {/* Content */}
      <div className="px-4 py-6 space-y-6">
        {/* Current Plan */}
        <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-6 transition-colors">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary mb-1">
                Current Plan
              </h2>
              <p className="text-sm text-gray-600 dark:text-dark-text-secondary">
                {subscription?.plan_name || 'Free'}
              </p>
            </div>

            <div className={`
              px-3 py-1 rounded-full text-xs font-medium
              ${subscription?.status === 'active'
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                : subscription?.status === 'cancelled'
                ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }
            `}>
              {subscription?.status || 'Active'}
            </div>
          </div>

          {/* Plan Details */}
          <div className="space-y-2 mb-4">
            {subscription?.billing_cycle && (
              <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-dark-text-secondary">
                <Calendar size={16} />
                <span>Billed {subscription.billing_cycle}</span>
              </div>
            )}
            {subscription?.next_billing_date && (
              <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-dark-text-secondary">
                <Receipt size={16} />
                <span>Next billing: {formatDate(subscription.next_billing_date)}</span>
              </div>
            )}
            {subscription?.current_period_end && subscription?.status === 'cancelled' && (
              <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
                <AlertCircle size={16} />
                <span>Access until: {formatDate(subscription.current_period_end)}</span>
              </div>
            )}
          </div>

          {/* Change Plan Button */}
          {!showPlans && (
            <button
              onClick={() => setShowPlans(true)}
              className="w-full px-4 py-2.5 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors"
            >
              View Available Plans
            </button>
          )}
        </div>

        {/* Usage Metrics */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary mb-3">
            Usage & Limits
          </h2>

          {usageLoading ? (
            <LoadingSpinner message="Loading usage..." />
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {usage?.events && (
                <UsageCard
                  usage={usage.events}
                  type="events"
                  label="Events"
                />
              )}
              {usage?.team_members && (
                <UsageCard
                  usage={usage.team_members}
                  type="team_members"
                  label="Team Members"
                />
              )}
              {usage?.storage && (
                <UsageCard
                  usage={usage.storage}
                  type="storage"
                  label="Storage"
                />
              )}
            </div>
          )}
        </div>

        {/* Available Plans */}
        {showPlans && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary">
                Available Plans
              </h2>
              <button
                onClick={() => setShowPlans(false)}
                className="text-sm text-primary dark:text-primary-light hover:underline"
              >
                Hide
              </button>
            </div>

            <div className="grid grid-cols-1 gap-6">
              {plans.map((plan) => {
                const isCurrentPlan = plan.name.toLowerCase() === currentPlanName;
                const isPopular = plan.name.toLowerCase() === 'pro';

                return (
                  <PlanCard
                    key={plan.id}
                    plan={plan}
                    currentPlan={isCurrentPlan}
                    onSelect={handlePlanSelect}
                    loading={actionLoading && selectedPlan?.id === plan.id}
                    popular={isPopular}
                  />
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Billing History */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary">
              Billing History
            </h2>
          </div>

          {historyLoading ? (
            <LoadingSpinner message="Loading history..." />
          ) : history && history.length > 0 ? (
            <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl overflow-hidden transition-colors">
              {history.map((invoice, index) => (
                <div
                  key={invoice.id}
                  className={`
                    p-4 flex items-center justify-between
                    ${index !== history.length - 1 ? 'border-b border-gray-200 dark:border-dark-bg-tertiary' : ''}
                  `}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gray-100 dark:bg-dark-bg-tertiary rounded-lg flex items-center justify-center flex-shrink-0">
                      <Receipt size={20} className="text-gray-600 dark:text-dark-text-secondary" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-dark-text-primary">
                        {formatCurrency(invoice.amount)}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-dark-text-secondary">
                        {formatDate(invoice.date)}
                      </p>
                      {invoice.description && (
                        <p className="text-xs text-gray-500 dark:text-dark-text-tertiary mt-1">
                          {invoice.description}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`
                      px-2 py-1 rounded text-xs font-medium
                      ${invoice.status === 'paid'
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                        : invoice.status === 'pending'
                        ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                        : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                      }
                    `}>
                      {invoice.status}
                    </span>

                    {invoice.invoice_url && (
                      <a
                        href={invoice.invoice_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
                        aria-label="Download invoice"
                      >
                        <Download size={18} className="text-gray-600 dark:text-dark-text-secondary" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-8 text-center transition-colors">
              <Receipt size={48} className="text-gray-400 dark:text-dark-text-tertiary mx-auto mb-3" />
              <p className="text-gray-600 dark:text-dark-text-secondary">
                No billing history yet
              </p>
            </div>
          )}
        </div>

        {/* Payment Method */}
        <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-6 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary">
              Payment Method
            </h2>
            <button className="text-sm text-primary dark:text-primary-light hover:underline">
              Update
            </button>
          </div>

          {subscription?.payment_method ? (
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gray-100 dark:bg-dark-bg-tertiary rounded-lg flex items-center justify-center">
                <CreditCard size={24} className="text-gray-600 dark:text-dark-text-secondary" />
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-dark-text-primary">
                  •••• {subscription.payment_method.last4}
                </p>
                <p className="text-sm text-gray-600 dark:text-dark-text-secondary">
                  Expires {subscription.payment_method.exp_month}/{subscription.payment_method.exp_year}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <CreditCard size={48} className="text-gray-400 dark:text-dark-text-tertiary mx-auto mb-3" />
              <p className="text-gray-600 dark:text-dark-text-secondary mb-3">
                No payment method on file
              </p>
              <button className="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors">
                Add Payment Method
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Cancel Subscription Dialog */}
      <ConfirmDialog
        open={showCancelDialog}
        onClose={() => !cancelLoading && setShowCancelDialog(false)}
        onConfirm={handleCancelSubscription}
        title="Cancel Subscription"
        message="Are you sure you want to cancel your subscription? You will continue to have access until the end of your current billing period."
        confirmText="Cancel Subscription"
        confirmVariant="danger"
        loading={cancelLoading}
      />
    </div>
  );
};
