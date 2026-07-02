import { Loader2 } from 'lucide-react';

export function LoadingSpinner({ label = 'Cargando…' }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-textSecondary" role="status" aria-label={label}>
      <Loader2 className="h-5 w-5 animate-spin" aria-hidden />
      <span className="text-description">{label}</span>
    </div>
  );
}
