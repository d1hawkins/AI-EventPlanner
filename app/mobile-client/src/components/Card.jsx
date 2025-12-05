import { motion } from 'framer-motion';

export const Card = ({
  children,
  className = '',
  onClick,
  interactive = false,
  ...props
}) => {
  const baseClasses = 'bg-white rounded-lg shadow-md p-4';
  const interactiveClasses = interactive
    ? 'cursor-pointer hover:shadow-lg transition-shadow duration-200'
    : '';

  const Component = interactive || onClick ? motion.div : 'div';
  const motionProps = interactive || onClick ? {
    whileTap: { scale: 0.98 },
    transition: { duration: 0.1 }
  } : {};

  return (
    <Component
      className={`${baseClasses} ${interactiveClasses} ${className}`}
      onClick={onClick}
      {...motionProps}
      {...props}
    >
      {children}
    </Component>
  );
};
