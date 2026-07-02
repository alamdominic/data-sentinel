import { useQuery, keepPreviousData } from '@tanstack/react-query';
import type { ExecutionFilterParams } from '@datasentinel/types';
import { executionsService } from '@/services/executionsService';

export function useExecutions(filters: ExecutionFilterParams) {
  return useQuery({
    queryKey: ['executions', filters],
    queryFn: () => executionsService.getExecutions(filters),
    placeholderData: keepPreviousData,
  });
}
