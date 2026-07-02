import type { ExecutionFilterParams, StatisticsSummary } from '@datasentinel/types';
import { toQueryString } from '@datasentinel/utils';
import { apiRequest } from '@/services/apiClient';

export const statisticsService = {
  getStatistics(filters: ExecutionFilterParams = {}): Promise<StatisticsSummary> {
    return apiRequest<StatisticsSummary>(`/api/statistics${toQueryString(filters)}`);
  },
};
