import type { ReactNode } from 'react';
import { Card } from '@/components/Card';
import { Skeleton } from '@/components/Skeleton';

interface ChartCardProps {
  title: string;
  children: ReactNode;
  isLoading?: boolean;
  height?: number;
}

export function ChartCard({ title, children, isLoading, height = 260 }: ChartCardProps) {
  return (
    <Card>
      <h3 className="mb-4 text-heading text-textPrimary">{title}</h3>
      {isLoading ? (
        <Skeleton style={{ height }} className="w-full" />
      ) : (
        <div style={{ height }}>{children}</div>
      )}
    </Card>
  );
}
