import type { DashboardMetrics, ExecutionFilterParams } from '@datasentinel/types';
import { toQueryString } from '@datasentinel/utils';
import { apiRequest } from '@/services/apiClient';

export const dashboardService = {
  getDashboard(filters: ExecutionFilterParams = {}): Promise<DashboardMetrics> {
    return apiRequest<DashboardMetrics>(`/api/dashboard${toQueryString(filters)}`);
  },
};
