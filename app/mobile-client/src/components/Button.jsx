import { motion } from 'framer-motion';
import { ButtonSpinner } from './common/LoadingSpinner';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  icon,
  onClick,
  disabled = false,
  loading = false,
  ...props
}) => {
  const baseClasses = 'font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2';

  const variantClasses = {
    primary: 'bg-primary dark:bg-primary-light text-white shadow-md hover:bg-primary-dark dark:hover:bg-primary active:scale-95 transition-colors',
    secondary: 'bg-white dark:bg-dark-bg-secondary text-primary dark:text-primary-light border-2 border-primary dark:border-primary-light hover:bg-gray-50 dark:hover:bg-dark-bg-tertiary active:scale-95 transition-colors',
    success: 'bg-success text-white shadow-md hover:bg-success-dark active:scale-95',
    danger: 'bg-danger text-white shadow-md hover:bg-danger-dark active:scale-95',
    ghost: 'bg-transparent text-primary dark:text-primary-light hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary active:scale-95 transition-colors',
  };

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  const widthClass = fullWidth ? 'w-full' : '';
  const disabledClass = (disabled || loading) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass} ${disabledClass}`;

  return (
    <motion.button
      whileTap={!disabled && !loading ? { scale: 0.95 } : {}}
      className={classes}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <ButtonSpinner size="sm" />
      ) : (
        icon && <span>{icon}</span>
      )}
      {children}
    </motion.button>
  );
};
