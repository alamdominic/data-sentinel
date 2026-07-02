import type { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

export function Card({ className = '', children, ...rest }: CardProps) {
  return (
    <div
      className={`rounded-card border border-border bg-surface p-6 shadow-soft ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
}
