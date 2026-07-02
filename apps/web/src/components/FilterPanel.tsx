/**
 * Panel de filtros compartido: ETL, fechas, estado, ambiente y servidor.
 * Los filtros se aplican con boton (no en cada tecla).
 */
import { useEffect, useMemo, useState } from 'react';
import { EXECUTION_STATUSES } from '@datasentinel/types';
import type { EtlRegistryEntry } from '@datasentinel/types';
import { Button } from '@/components/Button';
import { SelectInput } from '@/components/inputs/SelectInput';
import { TextInput } from '@/components/inputs/TextInput';
import { useFilterLayout } from '@/components/layout/FilterSlot';

export interface FilterValues {
  etl?: string;
  startDate?: string;
  endDate?: string;
  status?: string;
  environment?: string;
  server?: string;
}

interface FilterPanelProps {
  etls: EtlRegistryEntry[];
  value: FilterValues;
  onApply: (filters: FilterValues) => void;
  showStatus?: boolean;
}

export function FilterPanel({ etls, value, onApply, showStatus = true }: FilterPanelProps) {
  const [draft, setDraft] = useState<FilterValues>(value);

  useEffect(() => {
    setDraft(value);
  }, [value]);

  const environments = useMemo(
    () => [...new Set(etls.map((etl) => etl.environment).filter(Boolean))] as string[],
    [etls],
  );
  const servers = useMemo(
    () => [...new Set(etls.map((etl) => etl.serverName).filter(Boolean))] as string[],
    [etls],
  );

  const update = (patch: Partial<FilterValues>) => setDraft((prev) => ({ ...prev, ...patch }));

  const inSidebar = useFilterLayout() === 'sidebar';

  return (
    <div className={inSidebar ? '' : 'rounded-card border border-border bg-surface p-5'}>
      <div
        className={
          inSidebar
            ? 'grid grid-cols-1 gap-4'
            : 'grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6'
        }
      >
        <SelectInput
          id="filter-etl"
          label="ETL"
          placeholder="Todos"
          value={draft.etl ?? ''}
          onChange={(event) => update({ etl: event.target.value || undefined })}
          options={etls.map((etl) => ({
            value: etl.etlName,
            label: etl.displayName ?? etl.etlName,
          }))}
        />
        <TextInput
          id="filter-start"
          label="Fecha inicial"
          type="date"
          value={draft.startDate ?? ''}
          onChange={(event) => update({ startDate: event.target.value || undefined })}
        />
        <TextInput
          id="filter-end"
          label="Fecha final"
          type="date"
          value={draft.endDate ?? ''}
          onChange={(event) => update({ endDate: event.target.value || undefined })}
        />
        {showStatus && (
          <SelectInput
            id="filter-status"
            label="Estado"
            placeholder="Todos"
            value={draft.status ?? ''}
            onChange={(event) => update({ status: event.target.value || undefined })}
            options={EXECUTION_STATUSES.map((status) => ({ value: status, label: status }))}
          />
        )}
        <SelectInput
          id="filter-environment"
          label="Ambiente"
          placeholder="Todos"
          value={draft.environment ?? ''}
          onChange={(event) => update({ environment: event.target.value || undefined })}
          options={environments.map((environment) => ({ value: environment, label: environment }))}
        />
        <SelectInput
          id="filter-server"
          label="Servidor"
          placeholder="Todos"
          value={draft.server ?? ''}
          onChange={(event) => update({ server: event.target.value || undefined })}
          options={servers.map((server) => ({ value: server, label: server }))}
        />
      </div>
      <div className={`mt-4 flex gap-3 ${inSidebar ? 'flex-col' : ''}`}>
        <Button className={inSidebar ? 'w-full' : ''} onClick={() => onApply(draft)}>
          Aplicar filtros
        </Button>
        <Button
          variant="secondary"
          className={inSidebar ? 'w-full' : ''}
          onClick={() => {
            setDraft({});
            onApply({});
          }}
        >
          Limpiar
        </Button>
      </div>
    </div>
  );
}
