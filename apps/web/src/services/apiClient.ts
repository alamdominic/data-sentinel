/**
 * Cliente HTTP hacia la API.
 * Normaliza errores tecnicos al formato { code, message, details }.
 * No contiene reglas de negocio.
 */
import type { ApiErrorPayload } from '@datasentinel/types';

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details: Array<{ field?: string; issue?: string }>;

  constructor(
    code: string,
    message: string,
    status: number,
    details: Array<{ field?: string; issue?: string }> = [],
  ) {
    super(message);
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

const TOKEN_STORAGE_KEY = 'datasentinel.token';

export const tokenStorage = {
  get(): string | null {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  },
  set(token: string): void {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  },
  clear(): void {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  },
};

function baseUrl(): string {
  // Prioridad: config de runtime (window.__ENV__, inyectada al crear el
  // contenedor via docker-entrypoint.sh) sobre la de build time de Vite
  // (solo relevante en `npm run dev` / `npm run build` fuera de Docker).
  const runtime = window.__ENV__?.API_BASE_URL;
  const url = runtime !== undefined ? runtime : import.meta.env.VITE_API_BASE_URL;
  if (url === undefined) {
    throw new ApiError('CONFIG_ERROR', 'API_BASE_URL no configurada', 0);
  }
  // Cadena vacia = mismo origen (nginx sirve frontend y proxya /api).
  return url === '' ? '' : url.replace(/\/$/, '');
}

async function parseError(response: Response): Promise<ApiError> {
  let payload: ApiErrorPayload | null = null;
  try {
    payload = (await response.json()) as ApiErrorPayload;
  } catch {
    // cuerpo no JSON
  }
  if (payload?.error) {
    return new ApiError(
      payload.error.code,
      payload.error.message,
      response.status,
      payload.error.details ?? [],
    );
  }
  return new ApiError('HTTP_ERROR', `Error HTTP ${response.status}`, response.status);
}

export async function apiRequest<T>(
  path: string,
  options: { method?: string; body?: unknown; auth?: boolean } = {},
): Promise<T> {
  const { method = 'GET', body, auth = true } = options;
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = tokenStorage.get();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${baseUrl()}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError('NETWORK_ERROR', 'No se pudo conectar con el servidor', 0);
  }

  if (response.status === 401) {
    tokenStorage.clear();
    throw await parseError(response);
  }
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as T;
}
