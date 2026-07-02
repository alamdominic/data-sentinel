import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  Database,
  RefreshCw,
  XCircle,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { formatDateTime, formatDuration, formatRelativeTime } from '@datasentinel/utils';
import { PageHeader } from '@/components/PageHeader';
import { MetricCard } from '@/components/MetricCard';
import { ChartCard } from '@/components/ChartCard';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { ErrorState } from '@/components/ErrorState';
import { StatusBadge } from '@/components/StatusBadge';
import { FilterPanel, type FilterValues } from '@/components/FilterPanel';
import { PageFilters } from '@/components/layout/FilterSlot';
import { useDashboard } from '@/features/dashboard/useDashboard';
import { useRegisteredEtls } from '@/features/etl-registry/useRegisteredEtls';
import { ExecutionsTable } from '@/features/executions/ExecutionsTable';

const STATUS_COLORS: Record<string, string> = {
  SUCCESS: '#30D158',
  FAILED: '#FF453A',
  RUNNING: '#64D2FF',
  WARNING: '#FFD60A',
  CANCELLED: '#A1A1A6',
  UNKNOWN: '#6E6E73',
};

const chartTooltipStyle = {
  backgroundColor: '#242426',
  border: '1px solid #2C2C2E',
  borderRadius: 12,
  color: '#F5F5F7',
};

export function DashboardPage() {
  const [filters, setFilters] = useState<FilterValues>({});
  const etlsQuery = useRegisteredEtls();
  const dashboardQuery = useDashboard(filters);
  const data = dashboardQuery.data;
  const isLoading = dashboardQuery.isLoading;

  if (dashboardQuery.isError) {
    return (
      <div className="flex flex-col gap-6">
        <PageHeader title="Dashboard" />
        <ErrorState error={dashboardQuery.error} onRetry={() => dashboardQuery.refetch()} />
      </div>
    );
  }

  const donutData =
    data?.statusDistribution.filter((item) => item.count > 0).map((item) => ({
      name: item.status,
      value: item.count,
    })) ?? [];

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Dashboard"
        description={
          data
            ? `Actualizado ${formatRelativeTime(new Date().toISOString())}`
            : 'Resumen de ejecuciones ETL'
        }
        actions={
          <Button
            variant="secondary"
            onClick={() => dashboardQuery.refetch()}
            disabled={dashboardQuery.isFetching}
          >
            <RefreshCw
              className={`h-4 w-4 ${dashboardQuery.isFetching ? 'animate-spin' : ''}`}
              aria-hidden
            />
            Refrescar
          </Button>
        }
      />

      <PageFilters>
        <FilterPanel etls={etlsQuery.data ?? []} value={filters} onApply={setFilters} />
      </PageFilters>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard
          label="Total ETLs"
          value={data?.totalEtls ?? 0}
          icon={<Database className="h-5 w-5" />}
          isLoading={isLoading}
          context="Registrados y activos"
        />
        <MetricCard
          label="Exitosos"
          value={data?.successfulExecutions ?? 0}
          tone="success"
          icon={<CheckCircle2 className="h-5 w-5" />}
          isLoading={isLoading}
        />
        <MetricCard
          label="Fallidos"
          value={data?.failedExecutions ?? 0}
          tone={data && data.failedExecutions > 0 ? 'danger' : 'default'}
          icon={<XCircle className="h-5 w-5" />}
          isLoading={isLoading}
        />
        <MetricCard
          label="En ejecucion"
          value={data?.runningExecutions ?? 0}
          tone="info"
          icon={<Activity className="h-5 w-5" />}
          isLoading={isLoading}
        />
        <MetricCard
          label="Tiempo promedio"
          value={formatDuration(data?.averageDurationSeconds)}
          icon={<Clock className="h-5 w-5" />}
          isLoading={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 text-heading text-textPrimary">Ultima ejecucion</h3>
          {data?.lastExecution ? (
            <Link
              to={`/executions/${encodeURIComponent(data.lastExecution.id)}`}
              className="flex items-center justify-between gap-4 rounded-control p-3 transition-colors hover:bg-surfaceElevated"
            >
              <div>
                <p className="text-body font-medium text-textPrimary">
                  {data.lastExecution.etlName}
                </p>
                <p className="text-label text-textMuted">
                  {formatDateTime(data.lastExecution.startTime)} ·{' '}
                  {formatDuration(data.lastExecution.durationSeconds)}
                </p>
              </div>
              <StatusBadge status={data.lastExecution.status} />
            </Link>
          ) : (
            <p className="text-description text-textMuted">Sin ejecuciones en el rango.</p>
          )}
        </Card>
        <Card className={data?.lastError ? 'border-danger/40' : ''}>
          <h3 className="mb-3 flex items-center gap-2 text-heading text-textPrimary">
            <AlertCircle className="h-5 w-5 text-danger" aria-hidden />
            Ultimo error
          </h3>
          {data?.lastError ? (
            <Link
              to={`/executions/${encodeURIComponent(data.lastError.id)}`}
              className="block rounded-control p-3 transition-colors hover:bg-surfaceElevated"
            >
              <p className="text-body font-medium text-textPrimary">{data.lastError.etlName}</p>
              <p className="text-label text-textMuted">
                {formatDateTime(data.lastError.startTime)}
              </p>
            </Link>
          ) : (
            <p className="text-description text-textMuted">Sin errores en el rango. </p>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <ChartCard title="Tendencia de ejecuciones" isLoading={isLoading}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data?.executionTrend ?? []}>
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
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Tendencia de fallos" isLoading={isLoading}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data?.failureTrend ?? []}>
              <CartesianGrid stroke="#2C2C2E" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="period" stroke="#6E6E73" fontSize={12} tickLine={false} />
              <YAxis stroke="#6E6E73" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Bar dataKey="failures" name="Fallos" fill="#FF453A" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Distribucion por estado" isLoading={isLoading}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={donutData}
                dataKey="value"
                nameKey="name"
                innerRadius="55%"
                outerRadius="80%"
                paddingAngle={2}
              >
                {donutData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_COLORS[entry.name] ?? '#6E6E73'} />
                ))}
              </Pie>
              <Tooltip contentStyle={chartTooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-subtitle text-textPrimary">Ejecuciones recientes</h2>
          <Link to="/executions" className="text-description text-primary hover:underline">
            Ver todas
          </Link>
        </div>
        <ExecutionsTable
          rows={data?.recentExecutions ?? []}
          isLoading={isLoading}
          compact
        />
      </section>
    </div>
  );
}
