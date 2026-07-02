import { useQuery } from '@tanstack/react-query';
import type { ExecutionFilterParams } from '@datasentinel/types';
import { statisticsService } from '@/services/statisticsService';

export function useStatistics(filters: ExecutionFilterParams) {
  return useQuery({
    queryKey: ['statistics', filters],
    queryFn: () => statisticsService.getStatistics(filters),
  });
}
