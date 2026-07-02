/** Tabla de ejecuciones reutilizada por Dashboard, Ejecuciones e Historial. */
import { useNavigate } from 'react-router-dom';
import type { ExecutionSummary } from '@datasentinel/types';
import { formatDateTime, formatDuration, formatNumber } from '@datasentinel/utils';
import { DataTable, type DataTableColumn } from '@/components/DataTable';
import { StatusBadge } from '@/components/StatusBadge';

interface ExecutionsTableProps {
  rows: ExecutionSummary[];
  isLoading?: boolean;
  error?: unknown;
  onRetry?: () => void;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
  onSortChange?: (key: string) => void;
  compact?: boolean;
}

export function ExecutionsTable({
  rows,
  isLoading,
  error,
  onRetry,
  sortBy,
  sortDir,
  onSortChange,
  compact = false,
}: ExecutionsTableProps) {
  const navigate = useNavigate();

  const columns: Array<DataTableColumn<ExecutionSummary>> = [
    {
      key: 'etlName',
      header: 'ETL',
      sortable: true,
      render: (row) => <span className="font-medium">{row.etlName}</span>,
    },
    {
      key: 'startTime',
      header: 'Inicio',
      sortable: true,
      render: (row) => formatDateTime(row.startTime),
    },
    {
      key: 'endTime',
      header: 'Fin',
      sortable: true,
      render: (row) => formatDateTime(row.endTime),
    },
    {
      key: 'durationSeconds',
      header: 'Duracion',
      sortable: true,
      render: (row) => formatDuration(row.durationSeconds),
    },
    {
      key: 'status',
      header: 'Estado',
      sortable: true,
      render: (row) => <StatusBadge status={row.status} />,
    },
    ...(compact
      ? []
      : ([
          {
            key: 'recordsExtracted',
            header: 'Extraidos',
            sortable: true,
            align: 'right',
            render: (row) => formatNumber(row.recordsExtracted),
          },
          {
            key: 'recordsLoaded',
            header: 'Cargados',
            sortable: true,
            align: 'right',
            render: (row) => formatNumber(row.recordsLoaded),
          },
          {
            key: 'recordsRejected',
            header: 'Rechazados',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span className={row.recordsRejected > 0 ? 'text-warning' : undefined}>
                {formatNumber(row.recordsRejected)}
              </span>
            ),
          },
        ] satisfies Array<DataTableColumn<ExecutionSummary>>)),
  ];

  return (
    <DataTable
      columns={columns}
      rows={rows}
      rowKey={(row) => row.id}
      onRowClick={(row) => navigate(`/executions/${encodeURIComponent(row.id)}`)}
      sortBy={sortBy}
      sortDir={sortDir}
      onSortChange={onSortChange}
      isLoading={isLoading}
      error={error}
      onRetry={onRetry}
    />
  );
}
