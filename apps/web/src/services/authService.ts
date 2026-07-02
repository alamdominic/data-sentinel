import type { AuthUser, LoginResult } from '@datasentinel/types';
import { apiRequest } from '@/services/apiClient';

export const authService = {
  login(email: string, password: string): Promise<LoginResult> {
    return apiRequest<LoginResult>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
      auth: false,
    });
  },
  me(): Promise<AuthUser> {
    return apiRequest<AuthUser>('/api/auth/me');
  },
};
