import { useQuery } from '@tanstack/react-query';
import { executionsService } from '@/services/executionsService';

export function useExecutionDetail(compositeId: string | undefined) {
  return useQuery({
    queryKey: ['execution-detail', compositeId],
    queryFn: () => executionsService.getExecutionDetail(compositeId!),
    enabled: Boolean(compositeId),
  });
}
