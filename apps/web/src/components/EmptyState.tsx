import { Inbox } from 'lucide-react';

export function EmptyState({
  message = 'No hay datos para los filtros actuales.',
}: {
  message?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-3 py-12 text-center">
      <Inbox className="h-10 w-10 text-textMuted" aria-hidden />
      <p className="text-description text-textSecondary">{message}</p>
    </div>
  );
}
