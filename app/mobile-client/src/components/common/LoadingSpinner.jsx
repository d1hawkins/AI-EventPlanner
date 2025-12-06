import { motion } from 'framer-motion';

/**
 * LoadingSpinner - Animated loading indicator
 *
 * Props:
 * - size: 'sm' | 'md' | 'lg' (default: 'md')
 * - fullPage: boolean - Center in full viewport
 * - message: string - Optional loading message
 */

export const LoadingSpinner = ({ size = 'md', fullPage = false, message }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const spinner = (
    <motion.div
      className={`${sizeClasses[size]} border-4 border-primary/20 border-t-primary rounded-full`}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear',
      }}
    />
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-white dark:bg-dark-bg-primary transition-colors z-50">
        {spinner}
        {message && (
          <p className="mt-4 text-gray-600 dark:text-dark-text-secondary transition-colors">
            {message}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-8">
      {spinner}
      {message && (
        <p className="mt-4 text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">
          {message}
        </p>
      )}
    </div>
  );
};

/**
 * ButtonSpinner - Inline spinner for buttons
 */
export const ButtonSpinner = ({ size = 'sm' }) => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
  };

  return (
    <motion.div
      className={`${sizeClasses[size]} border-2 border-current/30 border-t-current rounded-full`}
      animate={{ rotate: 360 }}
      transition={{
        duration: 0.8,
        repeat: Infinity,
        ease: 'linear',
      }}
    />
  );
};

/**
 * SkeletonLoader - Skeleton loading placeholder
 */
export const SkeletonLoader = ({ count = 1, type = 'text', className = '' }) => {
  const skeletons = Array.from({ length: count });

  const typeClasses = {
    text: 'h-4 rounded',
    title: 'h-6 rounded',
    card: 'h-32 rounded-xl',
    circle: 'w-12 h-12 rounded-full',
    button: 'h-10 rounded-lg',
  };

  return (
    <>
      {skeletons.map((_, index) => (
        <motion.div
          key={index}
          className={`bg-gray-200 dark:bg-dark-bg-tertiary ${typeClasses[type]} ${className} mb-3`}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </>
  );
};

/**
 * CardSkeleton - Skeleton for card components
 */
export const CardSkeleton = ({ count = 3 }) => {
  const skeletons = Array.from({ length: count });

  return (
    <>
      {skeletons.map((_, index) => (
        <div
          key={index}
          className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 mb-4 transition-colors"
        >
          <div className="flex items-start gap-3">
            <SkeletonLoader type="circle" className="flex-shrink-0" />
            <div className="flex-1">
              <SkeletonLoader type="title" className="w-3/4" />
              <SkeletonLoader type="text" className="w-1/2 mt-2" />
            </div>
          </div>
          <SkeletonLoader type="text" className="w-full mt-4" />
          <SkeletonLoader type="button" className="w-32 mt-4" />
        </div>
      ))}
    </>
  );
};
