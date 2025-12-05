import { motion } from 'framer-motion';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  icon,
  onClick,
  disabled = false,
  ...props
}) => {
  const baseClasses = 'font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2';

  const variantClasses = {
    primary: 'bg-primary text-white shadow-md hover:bg-primary-dark active:scale-95',
    secondary: 'bg-white text-primary border-2 border-primary hover:bg-gray-50 active:scale-95',
    success: 'bg-success text-white shadow-md hover:bg-success-dark active:scale-95',
    danger: 'bg-danger text-white shadow-md hover:bg-danger-dark active:scale-95',
    ghost: 'bg-transparent text-primary hover:bg-gray-100 active:scale-95',
  };

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  const widthClass = fullWidth ? 'w-full' : '';
  const disabledClass = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass} ${disabledClass}`;

  return (
    <motion.button
      whileTap={!disabled ? { scale: 0.95 } : {}}
      className={classes}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {icon && <span>{icon}</span>}
      {children}
    </motion.button>
  );
};
