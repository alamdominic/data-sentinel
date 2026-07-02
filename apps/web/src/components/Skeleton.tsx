import type { HTMLAttributes } from 'react';

export function Skeleton({ className = '', ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`animate-pulse rounded-control bg-surfaceElevated ${className}`} {...rest} />
  );
}
