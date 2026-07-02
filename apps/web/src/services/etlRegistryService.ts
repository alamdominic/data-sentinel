import type { EtlRegistryEntry } from '@datasentinel/types';
import { toQueryString } from '@datasentinel/utils';
import { apiRequest } from '@/services/apiClient';

export interface RegisterEtlInput {
  etlName: string;
  tableName: string;
  schemaName?: string;
  displayName?: string;
  description?: string;
  environment?: string;
  serverName?: string;
}

export const etlRegistryService = {
  getRegisteredEtls(includeInactive = false): Promise<EtlRegistryEntry[]> {
    return apiRequest<EtlRegistryEntry[]>(
      `/api/etl-registry${toQueryString({ includeInactive })}`,
    );
  },
  registerEtl(input: RegisterEtlInput): Promise<EtlRegistryEntry> {
    return apiRequest<EtlRegistryEntry>('/api/etl-registry', { method: 'POST', body: input });
  },
  setActive(etlId: number, isActive: boolean): Promise<EtlRegistryEntry> {
    return apiRequest<EtlRegistryEntry>(`/api/etl-registry/${etlId}`, {
      method: 'PATCH',
      body: { isActive },
    });
  },
};
