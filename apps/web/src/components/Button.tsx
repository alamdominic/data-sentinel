import type { ButtonHTMLAttributes, ReactNode } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-primary text-white hover:bg-primary/90',
  secondary: 'bg-surfaceElevated text-textPrimary hover:bg-surfaceElevated/80 border border-border',
  ghost: 'bg-transparent text-textSecondary hover:text-textPrimary hover:bg-surfaceElevated/60',
  danger: 'bg-danger/15 text-danger hover:bg-danger/25 border border-danger/30',
};

export function Button({ variant = 'primary', className = '', children, ...rest }: ButtonProps) {
  return (
    <button
      className={`inline-flex h-11 items-center justify-center gap-2 rounded-control px-5 text-description font-medium transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-50 ${variantClasses[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
