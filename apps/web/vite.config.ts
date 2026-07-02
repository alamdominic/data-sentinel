/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@datasentinel/types': path.resolve(__dirname, '../../packages/types/src'),
      '@datasentinel/utils': path.resolve(__dirname, '../../packages/utils/src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['punk-cave-kinds-van.trycloudflare.com'],
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.{ts,tsx}', '../../packages/utils/tests/**/*.test.ts'],
  },
});
