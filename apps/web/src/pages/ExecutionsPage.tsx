import { useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { Pagination } from '@/components/Pagination';
import { FilterPanel, type FilterValues } from '@/components/FilterPanel';
import { PageFilters } from '@/components/layout/FilterSlot';
import { TextInput } from '@/components/inputs/TextInput';
import { Button } from '@/components/Button';
import { useExecutions } from '@/features/executions/useExecutions';
import { useRegisteredEtls } from '@/features/etl-registry/useRegisteredEtls';
import { ExecutionsTable } from '@/features/executions/ExecutionsTable';

const PAGE_LIMIT = 25;

interface AdvancedFilters {
  executionType?: string;
  sourceFile?: string;
  requestId?: string;
}

export function ExecutionsPage() {
  const [filters, setFilters] = useState<FilterValues>({});
  const [advanced, setAdvanced] = useState<AdvancedFilters>({});
  const [advancedDraft, setAdvancedDraft] = useState<AdvancedFilters>({});
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('startTime');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  const etlsQuery = useRegisteredEtls();
  const executionsQuery = useExecutions({
    ...filters,
    ...advanced,
    sortBy,
    sortDir,
    page,
    limit: PAGE_LIMIT,
  });

  const handleSortChange = (key: string) => {
    if (key === sortBy) {
      setSortDir((dir) => (dir === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(key);
      setSortDir('desc');
    }
    setPage(1);
  };

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Ejecuciones"
        description="Consulta y filtra todas las ejecuciones registradas"
      />

      <PageFilters>
        <FilterPanel
          etls={etlsQuery.data ?? []}
          value={filters}
          onApply={(next) => {
            setFilters(next);
            setPage(1);
          }}
        />
      </PageFilters>

      <details className="rounded-card border border-border bg-surface p-5">
        <summary className="cursor-pointer text-description text-textSecondary">
          Filtros avanzados
        </summary>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <TextInput
            id="filter-execution-type"
            label="Tipo de ejecucion"
            value={advancedDraft.executionType ?? ''}
            onChange={(event) =>
              setAdvancedDraft((prev) => ({
                ...prev,
                executionType: event.target.value || undefined,
              }))
            }
          />
          <TextInput
            id="filter-source-file"
            label="Archivo origen"
            value={advancedDraft.sourceFile ?? ''}
            onChange={(event) =>
              setAdvancedDraft((prev) => ({ ...prev, sourceFile: event.target.value || undefined }))
            }
          />
          <TextInput
            id="filter-request-id"
            label="Request ID"
            value={advancedDraft.requestId ?? ''}
            onChange={(event) =>
              setAdvancedDraft((prev) => ({ ...prev, requestId: event.target.value || undefined }))
            }
          />
        </div>
        <div className="mt-4">
          <Button
            variant="secondary"
            onClick={() => {
              setAdvanced(advancedDraft);
              setPage(1);
            }}
          >
            Aplicar avanzados
          </Button>
        </div>
      </details>

      <ExecutionsTable
        rows={executionsQuery.data?.items ?? []}
        isLoading={executionsQuery.isLoading}
        error={executionsQuery.isError ? executionsQuery.error : undefined}
        onRetry={() => executionsQuery.refetch()}
        sortBy={sortBy}
        sortDir={sortDir}
        onSortChange={handleSortChange}
      />

      <div className="flex items-center justify-between">
        <span className="text-label text-textMuted">
          {executionsQuery.data
            ? `${executionsQuery.data.total} ejecuciones · pagina ${executionsQuery.data.page} de ${executionsQuery.data.totalPages}`
            : ''}
        </span>
        <Pagination
          page={page}
          totalPages={executionsQuery.data?.totalPages ?? 0}
          onPageChange={setPage}
        />
      </div>
    </div>
  );
}
