import { useQuery } from '@tanstack/react-query';
import type { ExecutionFilterParams } from '@datasentinel/types';
import { dashboardService } from '@/services/dashboardService';

export function useDashboard(filters: ExecutionFilterParams) {
  return useQuery({
    queryKey: ['dashboard', filters],
    queryFn: () => dashboardService.getDashboard(filters),
  });
}
