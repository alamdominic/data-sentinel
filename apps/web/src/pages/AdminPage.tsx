import { useState, type FormEvent } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import type { EtlRegistryEntry } from '@datasentinel/types';
import { formatDateTime } from '@datasentinel/utils';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { TextInput } from '@/components/inputs/TextInput';
import { DataTable, type DataTableColumn } from '@/components/DataTable';
import { useRegisteredEtls } from '@/features/etl-registry/useRegisteredEtls';
import { etlRegistryService, type RegisterEtlInput } from '@/services/etlRegistryService';
import { ApiError } from '@/services/apiClient';

const EMPTY_FORM: RegisterEtlInput = { etlName: '', tableName: '' };

export function AdminPage() {
  const queryClient = useQueryClient();
  const etlsQuery = useRegisteredEtls(true);
  const [form, setForm] = useState<RegisterEtlInput>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['etl-registry'] });

  const registerMutation = useMutation({
    mutationFn: (input: RegisterEtlInput) => etlRegistryService.registerEtl(input),
    onSuccess: (created) => {
      setForm(EMPTY_FORM);
      setFormError(null);
      setFormSuccess(`ETL ${created.etlName} registrado. Ya aparece en el dashboard.`);
      invalidate();
    },
    onError: (error) => {
      setFormSuccess(null);
      if (error instanceof ApiError) {
        const detail = error.details[0];
        setFormError(detail?.issue ?? error.message);
      } else {
        setFormError('No se pudo registrar el ETL');
      }
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ etlId, isActive }: { etlId: number; isActive: boolean }) =>
      etlRegistryService.setActive(etlId, isActive),
    onSuccess: invalidate,
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);
    registerMutation.mutate(form);
  };

  const update = (patch: Partial<RegisterEtlInput>) =>
    setForm((prev) => ({ ...prev, ...patch }));

  const columns: Array<DataTableColumn<EtlRegistryEntry>> = [
    {
      key: 'etlName',
      header: 'ETL',
      render: (row) => (
        <div>
          <p className="font-medium">{row.displayName ?? row.etlName}</p>
          <p className="text-label text-textMuted">
            {row.schemaName}.{row.tableName}
          </p>
        </div>
      ),
    },
    { key: 'environment', header: 'Ambiente', render: (row) => row.environment ?? '—' },
    { key: 'serverName', header: 'Servidor', render: (row) => row.serverName ?? '—' },
    { key: 'createdAt', header: 'Registrado', render: (row) => formatDateTime(row.createdAt) },
    {
      key: 'isActive',
      header: 'Estado',
      render: (row) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-1.5 text-label font-medium ${
            row.isActive ? 'bg-success/15 text-success' : 'bg-textSecondary/15 text-textSecondary'
          }`}
        >
          {row.isActive ? 'Activo' : 'Inactivo'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      render: (row) => (
        <Button
          variant={row.isActive ? 'danger' : 'secondary'}
          className="h-9 px-3 text-label"
          disabled={toggleMutation.isPending}
          onClick={() => toggleMutation.mutate({ etlId: row.etlId, isActive: !row.isActive })}
        >
          {row.isActive ? 'Desactivar' : 'Activar'}
        </Button>
      ),
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Administracion de ETLs"
        description="Registra nuevas tablas ETL sin redeploy. Solo tablas del schema etl_execution_aws."
      />

      <Card>
        <h3 className="mb-4 flex items-center gap-2 text-heading text-textPrimary">
          <Plus className="h-5 w-5 text-primary" aria-hidden />
          Registrar nueva tabla ETL
        </h3>
        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <TextInput
              id="admin-etl-name"
              label="Nombre ETL *"
              value={form.etlName}
              onChange={(event) => update({ etlName: event.target.value })}
              placeholder="etl_facturacion"
              required
            />
            <TextInput
              id="admin-table-name"
              label="Tabla *"
              value={form.tableName}
              onChange={(event) => update({ tableName: event.target.value })}
              placeholder="etl_facturacion"
              required
            />
            <TextInput
              id="admin-display-name"
              label="Nombre visible"
              value={form.displayName ?? ''}
              onChange={(event) => update({ displayName: event.target.value || undefined })}
              placeholder="Facturacion"
            />
            <TextInput
              id="admin-environment"
              label="Ambiente"
              value={form.environment ?? ''}
              onChange={(event) => update({ environment: event.target.value || undefined })}
              placeholder="prod"
            />
            <TextInput
              id="admin-server"
              label="Servidor"
              value={form.serverName ?? ''}
              onChange={(event) => update({ serverName: event.target.value || undefined })}
              placeholder="aws-etl-01"
            />
            <TextInput
              id="admin-description"
              label="Descripcion"
              value={form.description ?? ''}
              onChange={(event) => update({ description: event.target.value || undefined })}
            />
          </div>
          {formError && (
            <p className="rounded-control bg-danger/10 px-4 py-3 text-description text-danger" role="alert">
              {formError}
            </p>
          )}
          {formSuccess && (
            <p className="rounded-control bg-success/10 px-4 py-3 text-description text-success">
              {formSuccess}
            </p>
          )}
          <div>
            <Button type="submit" disabled={registerMutation.isPending}>
              {registerMutation.isPending ? 'Registrando…' : 'Registrar ETL'}
            </Button>
          </div>
        </form>
      </Card>

      <section className="flex flex-col gap-4">
        <h2 className="text-subtitle text-textPrimary">ETLs registrados</h2>
        <DataTable
          columns={columns}
          rows={etlsQuery.data ?? []}
          rowKey={(row) => String(row.etlId)}
          isLoading={etlsQuery.isLoading}
          error={etlsQuery.isError ? etlsQuery.error : undefined}
          onRetry={() => etlsQuery.refetch()}
          emptyMessage="No hay ETLs registrados todavia."
        />
      </section>
    </div>
  );
}
