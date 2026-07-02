import { useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { formatDuration, formatNumber } from '@datasentinel/utils';
import { PageHeader } from '@/components/PageHeader';
import { MetricCard } from '@/components/MetricCard';
import { ChartCard } from '@/components/ChartCard';
import { ErrorState } from '@/components/ErrorState';
import { DataTable, type DataTableColumn } from '@/components/DataTable';
import { FilterPanel, type FilterValues } from '@/components/FilterPanel';
import { PageFilters } from '@/components/layout/FilterSlot';
import { useStatistics } from '@/features/statistics/useStatistics';
import { useRegisteredEtls } from '@/features/etl-registry/useRegisteredEtls';
import type { EtlStatistics } from '@datasentinel/types';

const chartTooltipStyle = {
  backgroundColor: '#242426',
  border: '1px solid #2C2C2E',
  borderRadius: 12,
  color: '#F5F5F7',
};

const perEtlColumns: Array<DataTableColumn<EtlStatistics>> = [
  {
    key: 'etlName',
    header: 'ETL',
    render: (row) => <span className="font-medium">{row.displayName ?? row.etlName}</span>,
  },
  {
    key: 'executionCount',
    header: 'Ejecuciones',
    align: 'right',
    render: (row) => formatNumber(row.executionCount),
  },
  {
    key: 'errorCount',
    header: 'Errores',
    align: 'right',
    render: (row) => (
      <span className={row.errorCount > 0 ? 'text-danger' : undefined}>
        {formatNumber(row.errorCount)}
      </span>
    ),
  },
  {
    key: 'averageDurationSeconds',
    header: 'Promedio',
    align: 'right',
    render: (row) => formatDuration(row.averageDurationSeconds),
  },
  {
    key: 'maxDurationSeconds',
    header: 'Maximo',
    align: 'right',
    render: (row) => formatDuration(row.maxDurationSeconds),
  },
  {
    key: 'minDurationSeconds',
    header: 'Minimo',
    align: 'right',
    render: (row) => formatDuration(row.minDurationSeconds),
  },
];

export function StatisticsPage() {
  const [filters, setFilters] = useState<FilterValues>({});
  const etlsQuery = useRegisteredEtls();
  const statisticsQuery = useStatistics(filters);
  const stats = statisticsQuery.data;
  const isLoading = statisticsQuery.isLoading;

  if (statisticsQuery.isError) {
    return (
      <div className="flex flex-col gap-6">
        <PageHeader title="Estadisticas" />
        <ErrorState error={statisticsQuery.error} onRetry={() => statisticsQuery.refetch()} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Estadisticas" description="Comportamiento historico de los ETLs" />

      <PageFilters>
        <FilterPanel
          etls={etlsQuery.data ?? []}
          value={filters}
          onApply={setFilters}
          showStatus={false}
        />
      </PageFilters>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard
          label="Ejecuciones"
          value={formatNumber(stats?.executionCount ?? 0)}
          isLoading={isLoading}
        />
        <MetricCard
          label="Errores"
          value={formatNumber(stats?.errorCount ?? 0)}
          tone={stats && stats.errorCount > 0 ? 'danger' : 'default'}
          isLoading={isLoading}
        />
        <MetricCard
          label="Tiempo promedio"
          value={formatDuration(stats?.averageDurationSeconds)}
          isLoading={isLoading}
        />
        <MetricCard
          label="Tiempo maximo"
          value={formatDuration(stats?.maxDurationSeconds)}
          isLoading={isLoading}
        />
        <MetricCard
          label="Tiempo minimo"
          value={formatDuration(stats?.minDurationSeconds)}
          isLoading={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ChartCard title="Tendencia semanal" isLoading={isLoading}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={stats?.weeklyTrend ?? []}>
              <CartesianGrid stroke="#2C2C2E" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="period" stroke="#6E6E73" fontSize={12} tickLine={false} />
              <YAxis stroke="#6E6E73" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Line
                type="monotone"
                dataKey="executions"
                name="Ejecuciones"
                stroke="#0071E3"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="failures"
                name="Fallos"
                stroke="#FF453A"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Tendencia mensual" isLoading={isLoading}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats?.monthlyTrend ?? []}>
              <CartesianGrid stroke="#2C2C2E" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="period" stroke="#6E6E73" fontSize={12} tickLine={false} />
              <YAxis stroke="#6E6E73" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Bar dataKey="executions" name="Ejecuciones" fill="#0071E3" radius={[4, 4, 0, 0]} />
              <Bar dataKey="failures" name="Fallos" fill="#FF453A" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <section className="flex flex-col gap-4">
        <h2 className="text-subtitle text-textPrimary">Resumen por ETL</h2>
        <DataTable
          columns={perEtlColumns}
          rows={stats?.perEtl ?? []}
          rowKey={(row) => row.etlName}
          isLoading={isLoading}
        />
      </section>
    </div>
  );
}
