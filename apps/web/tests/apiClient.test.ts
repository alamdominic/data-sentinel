import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiRequest, tokenStorage } from '@/services/apiClient';

const originalFetch = globalThis.fetch;

function mockFetch(status: number, body: unknown) {
  globalThis.fetch = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  ) as typeof fetch;
}

describe('apiRequest', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_API_BASE_URL', 'http://api.test');
    tokenStorage.clear();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.unstubAllEnvs();
  });

  it('returns parsed JSON on success', async () => {
    mockFetch(200, { status: 'ok' });
    const result = await apiRequest<{ status: string }>('/api/health');
    expect(result.status).toBe('ok');
  });

  it('sends Authorization header when token exists', async () => {
    tokenStorage.set('abc123');
    mockFetch(200, {});
    await apiRequest('/api/dashboard');
    const call = vi.mocked(globalThis.fetch).mock.calls[0];
    const headers = (call[1] as RequestInit).headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer abc123');
  });

  it('normalizes API error payload', async () => {
    mockFetch(400, {
      error: { code: 'VALIDATION_ERROR', message: 'Parametros invalidos', details: [] },
    });
    await expect(apiRequest('/api/executions')).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      status: 400,
    });
  });

  it('clears token on 401', async () => {
    tokenStorage.set('expired');
    mockFetch(401, { error: { code: 'UNAUTHORIZED', message: 'Sesion expirada', details: [] } });
    await expect(apiRequest('/api/auth/me')).rejects.toBeInstanceOf(ApiError);
    expect(tokenStorage.get()).toBeNull();
  });

  it('wraps network failures', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('fetch failed')) as typeof fetch;
    await expect(apiRequest('/api/health')).rejects.toMatchObject({ code: 'NETWORK_ERROR' });
  });
});
