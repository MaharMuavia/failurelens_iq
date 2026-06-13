import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig, loadEnv} from 'vite';

export default defineConfig(({ mode }) => {
  // Load env file from the parent directory
  const env = loadEnv(mode, "../", "");
  
  const backendPort = env.BACKEND_PORT || env.PORT || "8000";
  const backendHost = env.HOST || "localhost";
  const host = backendHost === "0.0.0.0" ? "localhost" : backendHost;
  const backendUrl = `http://${host}:${backendPort}`;
  
  const proxyTarget = (typeof process !== "undefined" && process.env && process.env.VITE_PROXY_TARGET) || env.VITE_PROXY_TARGET || backendUrl;

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      port: 5173,
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modify—file watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
      // Disable file watching when DISABLE_HMR is true to save CPU during agent edits.
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
      proxy: {
        "/api": {
          target: proxyTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, "")
        }
      }
    },
  };
});
