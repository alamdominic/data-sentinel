import { useMemo, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { Pagination } from '@/components/Pagination';
import { SelectInput } from '@/components/inputs/SelectInput';
import { EmptyState } from '@/components/EmptyState';
import { useExecutions } from '@/features/executions/useExecutions';
import { useRegisteredEtls } from '@/features/etl-registry/useRegisteredEtls';
import { ExecutionsTable } from '@/features/executions/ExecutionsTable';

const PAGE_LIMIT = 25;

export function HistoryPage() {
  const etlsQuery = useRegisteredEtls();
  const [selectedEtl, setSelectedEtl] = useState('');
  const [page, setPage] = useState(1);

  const etlOptions = useMemo(
    () =>
      (etlsQuery.data ?? []).map((etl) => ({
        value: etl.etlName,
        label: etl.displayName ?? etl.etlName,
      })),
    [etlsQuery.data],
  );

  const executionsQuery = useExecutions({
    etl: selectedEtl || undefined,
    sortBy: 'startTime',
    sortDir: 'desc',
    page,
    limit: PAGE_LIMIT,
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Historial"
        description="Todas las ejecuciones anteriores del ETL seleccionado"
      />

      <div className="max-w-sm">
        <SelectInput
          id="history-etl"
          label="ETL"
          placeholder="Selecciona un ETL"
          value={selectedEtl}
          onChange={(event) => {
            setSelectedEtl(event.target.value);
            setPage(1);
          }}
          options={etlOptions}
        />
      </div>

      {selectedEtl ? (
        <>
          <ExecutionsTable
            rows={executionsQuery.data?.items ?? []}
            isLoading={executionsQuery.isLoading}
            error={executionsQuery.isError ? executionsQuery.error : undefined}
            onRetry={() => executionsQuery.refetch()}
          />
          <div className="flex justify-end">
            <Pagination
              page={page}
              totalPages={executionsQuery.data?.totalPages ?? 0}
              onPageChange={setPage}
            />
          </div>
        </>
      ) : (
        <EmptyState message="Selecciona un ETL para consultar su historial." />
      )}
    </div>
  );
}
