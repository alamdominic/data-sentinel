import { useQuery } from '@tanstack/react-query';
import { etlRegistryService } from '@/services/etlRegistryService';

export function useRegisteredEtls(includeInactive = false) {
  return useQuery({
    queryKey: ['etl-registry', { includeInactive }],
    queryFn: () => etlRegistryService.getRegisteredEtls(includeInactive),
  });
}
