/**
 * Tipos compartidos entre frontend y contratos de la API.
 * Espejo de los DTOs del backend (camelCase).
 */

export const EXECUTION_STATUSES = [
  'SUCCESS',
  'FAILED',
  'RUNNING',
  'WARNING',
  'CANCELLED',
] as const;

export type ExecutionStatus = (typeof EXECUTION_STATUSES)[number];

export interface ExecutionSummary {
  id: string;
  etlName: string;
  executionId: string | null;
  startTime: string;
  endTime: string | null;
  durationSeconds: number | null;
  status: string;
  recordsExtracted: number;
  recordsLoaded: number;
  recordsRejected: number;
  executionType: string | null;
  etlVersion: string | null;
  sourceFile: string | null;
}

export interface ExecutionDetail extends ExecutionSummary {
  errorMessage: string | null;
  errorStacktrace: string | null;
  requestId: string | null;
  createdAt: string | null;
}

export interface PaginatedExecutions {
  items: ExecutionSummary[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface TrendPoint {
  period: string;
  executions: number;
  failures: number;
  averageDurationSeconds: number | null;
}

export interface StatusCount {
  status: string;
  count: number;
}

export interface DashboardMetrics {
  totalEtls: number;
  successfulExecutions: number;
  failedExecutions: number;
  runningExecutions: number;
  averageDurationSeconds: number | null;
  lastExecution: ExecutionSummary | null;
  lastError: ExecutionSummary | null;
  executionTrend: TrendPoint[];
  failureTrend: TrendPoint[];
  statusDistribution: StatusCount[];
  recentExecutions: ExecutionSummary[];
}

export interface EtlStatistics {
  etlName: string;
  displayName: string | null;
  executionCount: number;
  errorCount: number;
  averageDurationSeconds: number | null;
  maxDurationSeconds: number | null;
  minDurationSeconds: number | null;
}

export interface StatisticsSummary {
  averageDurationSeconds: number | null;
  maxDurationSeconds: number | null;
  minDurationSeconds: number | null;
  errorCount: number;
  executionCount: number;
  weeklyTrend: TrendPoint[];
  monthlyTrend: TrendPoint[];
  perEtl: EtlStatistics[];
}

export interface AuthUser {
  userId: number;
  email: string;
  fullName: string | null;
  role: string;
  isActive: boolean;
  lastLoginAt: string | null;
}

export interface LoginResult {
  accessToken: string;
  tokenType: string;
  user: AuthUser;
}

export interface EtlRegistryEntry {
  etlId: number;
  etlName: string;
  schemaName: string;
  tableName: string;
  displayName: string | null;
  description: string | null;
  environment: string | null;
  serverName: string | null;
  isActive: boolean;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface ApiErrorPayload {
  error: {
    code: string;
    message: string;
    details: Array<{ field?: string; issue?: string }>;
  };
}

export interface ExecutionFilterParams {
  etl?: string;
  startDate?: string;
  endDate?: string;
  status?: string;
  environment?: string;
  server?: string;
  executionType?: string;
  sourceFile?: string;
  requestId?: string;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}
