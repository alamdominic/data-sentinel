import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/Button';
import { ApiError } from '@/services/apiClient';

interface ErrorStateProps {
  error?: unknown;
  onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  const message =
    error instanceof ApiError ? error.message : 'Ocurrio un error al cargar la informacion.';
  const code = error instanceof ApiError ? error.code : undefined;
  return (
    <div className="flex flex-col items-center gap-3 py-12 text-center">
      <AlertTriangle className="h-10 w-10 text-danger" aria-hidden />
      <p className="text-description text-textSecondary">{message}</p>
      {code && <span className="text-label text-textMuted">Codigo: {code}</span>}
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          Reintentar
        </Button>
      )}
    </div>
  );
}
