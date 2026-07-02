import type { ReactNode } from 'react';
import { Card } from '@/components/Card';
import { Skeleton } from '@/components/Skeleton';

interface MetricCardProps {
  label: string;
  value: ReactNode;
  context?: string;
  icon?: ReactNode;
  tone?: 'default' | 'success' | 'danger' | 'info' | 'warning';
  isLoading?: boolean;
}

const toneClasses: Record<NonNullable<MetricCardProps['tone']>, string> = {
  default: 'text-textPrimary',
  success: 'text-success',
  danger: 'text-danger',
  info: 'text-info',
  warning: 'text-warning',
};

export function MetricCard({
  label,
  value,
  context,
  icon,
  tone = 'default',
  isLoading = false,
}: MetricCardProps) {
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-label uppercase tracking-wide text-textSecondary">{label}</span>
        {icon && <span className="text-textMuted">{icon}</span>}
      </div>
      {isLoading ? (
        <Skeleton className="h-9 w-24" />
      ) : (
        <span className={`text-title leading-none ${toneClasses[tone]}`}>{value}</span>
      )}
      {context && <span className="text-label text-textMuted">{context}</span>}
    </Card>
  );
}
