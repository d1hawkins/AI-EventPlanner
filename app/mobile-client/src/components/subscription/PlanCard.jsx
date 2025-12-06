import { motion } from 'framer-motion';
import { Check, Sparkles, Zap, Crown } from 'lucide-react';
import { Button } from '../Button';

/**
 * PlanCard - Subscription plan display card
 *
 * Props:
 * - plan: Plan object
 * - currentPlan: boolean - Whether this is the current plan
 * - onSelect: function - Plan selection handler
 * - loading: boolean - Loading state
 * - popular: boolean - Whether to show popular badge
 */

export const PlanCard = ({
  plan,
  currentPlan = false,
  onSelect,
  loading = false,
  popular = false,
}) => {
  const {
    name,
    price,
    billing_period = 'month',
    features = [],
    limits = {},
    description,
  } = plan;

  const planIcons = {
    free: Sparkles,
    pro: Zap,
    enterprise: Crown,
  };

  const planColors = {
    free: {
      icon: 'text-gray-600 dark:text-gray-400',
      bg: 'bg-gray-100 dark:bg-gray-800',
      border: 'border-gray-200 dark:border-gray-700',
      badge: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
    },
    pro: {
      icon: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-100 dark:bg-blue-900/30',
      border: 'border-blue-500 dark:border-blue-400',
      badge: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
    },
    enterprise: {
      icon: 'text-purple-600 dark:text-purple-400',
      bg: 'bg-purple-100 dark:bg-purple-900/30',
      border: 'border-purple-500 dark:border-purple-400',
      badge: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400',
    },
  };

  const planKey = name.toLowerCase();
  const colors = planColors[planKey] || planColors.free;
  const PlanIcon = planIcons[planKey] || Sparkles;

  const formatPrice = (price) => {
    if (price === 0) return 'Free';
    return `$${price}`;
  };

  const getButtonText = () => {
    if (currentPlan) return 'Current Plan';
    if (planKey === 'free') return 'Downgrade';
    return 'Upgrade';
  };

  const getButtonVariant = () => {
    if (currentPlan) return 'secondary';
    if (planKey === 'free') return 'secondary';
    return 'primary';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        relative bg-white dark:bg-dark-bg-secondary rounded-xl p-6 border-2 transition-all
        ${currentPlan ? colors.border : 'border-gray-200 dark:border-dark-bg-tertiary'}
        ${popular && !currentPlan ? 'shadow-lg scale-105' : ''}
      `}
    >
      {/* Popular Badge */}
      {popular && !currentPlan && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors.badge}`}>
            Most Popular
          </span>
        </div>
      )}

      {/* Current Plan Badge */}
      {currentPlan && (
        <div className="absolute -top-3 right-4">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors.badge}`}>
            Current
          </span>
        </div>
      )}

      {/* Icon */}
      <div className={`w-12 h-12 ${colors.bg} rounded-xl flex items-center justify-center mb-4`}>
        <PlanIcon size={24} className={colors.icon} />
      </div>

      {/* Plan Name */}
      <h3 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
        {name}
      </h3>

      {/* Description */}
      {description && (
        <p className="text-sm text-gray-600 dark:text-dark-text-secondary mb-4">
          {description}
        </p>
      )}

      {/* Price */}
      <div className="mb-6">
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold text-gray-900 dark:text-dark-text-primary">
            {formatPrice(price)}
          </span>
          {price !== 0 && (
            <span className="text-gray-600 dark:text-dark-text-secondary">
              /{billing_period}
            </span>
          )}
        </div>
      </div>

      {/* Features */}
      <div className="space-y-3 mb-6">
        {features.map((feature, index) => (
          <div key={index} className="flex items-start gap-2">
            <Check size={18} className="text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-gray-700 dark:text-dark-text-secondary">
              {feature}
            </span>
          </div>
        ))}
      </div>

      {/* Limits */}
      {Object.keys(limits).length > 0 && (
        <div className="mb-6 p-3 bg-gray-50 dark:bg-dark-bg-tertiary rounded-lg border border-gray-200 dark:border-dark-bg-tertiary">
          <h4 className="text-xs font-semibold text-gray-500 dark:text-dark-text-tertiary uppercase mb-2">
            Limits
          </h4>
          <div className="space-y-1">
            {limits.events !== undefined && (
              <div className="text-sm text-gray-700 dark:text-dark-text-secondary">
                <span className="font-medium">{limits.events === -1 ? 'Unlimited' : limits.events}</span> events
              </div>
            )}
            {limits.team_members !== undefined && (
              <div className="text-sm text-gray-700 dark:text-dark-text-secondary">
                <span className="font-medium">{limits.team_members === -1 ? 'Unlimited' : limits.team_members}</span> team members
              </div>
            )}
            {limits.storage !== undefined && (
              <div className="text-sm text-gray-700 dark:text-dark-text-secondary">
                <span className="font-medium">{limits.storage}GB</span> storage
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action Button */}
      <Button
        variant={getButtonVariant()}
        onClick={() => onSelect(plan)}
        disabled={currentPlan || loading}
        loading={loading}
        fullWidth
      >
        {getButtonText()}
      </Button>
    </motion.div>
  );
};
