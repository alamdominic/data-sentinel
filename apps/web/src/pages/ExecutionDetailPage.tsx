import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { formatDateTime, formatDuration, formatNumber } from '@datasentinel/utils';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { StatusBadge } from '@/components/StatusBadge';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ErrorState } from '@/components/ErrorState';
import { useExecutionDetail } from '@/features/execution-detail/useExecutionDetail';

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 border-b border-border py-2.5 last:border-b-0">
      <span className="text-description text-textSecondary">{label}</span>
      <span className="break-all text-right text-description text-textPrimary">{value ?? '—'}</span>
    </div>
  );
}

export function ExecutionDetailPage() {
  const { executionId } = useParams<{ executionId: string }>();
  const detailQuery = useExecutionDetail(executionId);
  const detail = detailQuery.data;

  if (detailQuery.isLoading) {
    return (
      <div className="flex justify-center py-20">
        <LoadingSpinner label="Cargando detalle…" />
      </div>
    );
  }
  if (detailQuery.isError || !detail) {
    return <ErrorState error={detailQuery.error} onRetry={() => detailQuery.refetch()} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <Link
        to="/executions"
        className="inline-flex items-center gap-2 text-description text-textSecondary hover:text-textPrimary"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Volver a ejecuciones
      </Link>

      <PageHeader
        title={detail.etlName}
        description={detail.executionId ?? undefined}
        actions={<StatusBadge status={detail.status} />}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 text-heading text-textPrimary">General</h3>
          <DetailRow label="Identificador" value={detail.executionId} />
          <DetailRow label="Inicio" value={formatDateTime(detail.startTime)} />
          <DetailRow label="Fin" value={formatDateTime(detail.endTime)} />
          <DetailRow label="Duracion" value={formatDuration(detail.durationSeconds)} />
          <DetailRow label="Estado" value={<StatusBadge status={detail.status} />} />
        </Card>

        <Card>
          <h3 className="mb-3 text-heading text-textPrimary">Procesamiento</h3>
          <DetailRow label="Registros extraidos" value={formatNumber(detail.recordsExtracted)} />
          <DetailRow label="Registros cargados" value={formatNumber(detail.recordsLoaded)} />
          <DetailRow
            label="Registros rechazados"
            value={
              <span className={detail.recordsRejected > 0 ? 'text-warning' : undefined}>
                {formatNumber(detail.recordsRejected)}
              </span>
            }
          />
        </Card>

        <Card className={detail.errorMessage ? 'border-danger/40' : ''}>
          <h3 className="mb-3 text-heading text-textPrimary">Errores</h3>
          {detail.errorMessage ? (
            <>
              <p className="rounded-control bg-danger/10 px-4 py-3 text-description text-danger">
                {detail.errorMessage}
              </p>
              {detail.errorStacktrace && (
                <details className="mt-4">
                  <summary className="cursor-pointer text-description text-textSecondary">
                    Ver stacktrace
                  </summary>
                  <pre className="mt-3 max-h-72 overflow-auto rounded-control bg-background p-4 text-label text-textSecondary">
                    {detail.errorStacktrace}
                  </pre>
                </details>
              )}
            </>
          ) : (
            <p className="text-description text-textMuted">Sin errores registrados.</p>
          )}
        </Card>

        <Card>
          <h3 className="mb-3 text-heading text-textPrimary">Variables</h3>
          <DetailRow label="Archivo origen" value={detail.sourceFile} />
          <DetailRow label="Request ID" value={detail.requestId} />
          <DetailRow label="Tipo de ejecucion" value={detail.executionType} />
          <DetailRow label="Version" value={detail.etlVersion} />
          <DetailRow label="Registrado" value={formatDateTime(detail.createdAt)} />
        </Card>
      </div>
    </div>
  );
}
