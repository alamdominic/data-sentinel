/**
 * Config inyectada en runtime por docker-entrypoint.sh (envsubst sobre
 * env.template.js -> env.js), cargada en index.html antes del bundle.
 * En desarrollo local, public/env.js define un objeto vacio y se usa el
 * fallback de import.meta.env.VITE_API_BASE_URL.
 */
interface RuntimeEnv {
  API_BASE_URL?: string;
}

interface Window {
  __ENV__?: RuntimeEnv;
}
