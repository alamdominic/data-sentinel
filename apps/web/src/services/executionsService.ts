import type {
  ExecutionDetail,
  ExecutionFilterParams,
  PaginatedExecutions,
} from '@datasentinel/types';
import { toQueryString } from '@datasentinel/utils';
import { apiRequest } from '@/services/apiClient';

export const executionsService = {
  getExecutions(filters: ExecutionFilterParams = {}): Promise<PaginatedExecutions> {
    return apiRequest<PaginatedExecutions>(`/api/executions${toQueryString(filters)}`);
  },
  getExecutionDetail(compositeId: string): Promise<ExecutionDetail> {
    return apiRequest<ExecutionDetail>(`/api/executions/${encodeURIComponent(compositeId)}`);
  },
};
