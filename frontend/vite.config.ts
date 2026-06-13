/// <reference types="vitest" />
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  // Load env file from the parent directory
  const env = loadEnv(mode, "../", "");
  
  const backendPort = env.BACKEND_PORT || env.PORT || "8000";
  const backendHost = env.HOST || "localhost";
  const host = backendHost === "0.0.0.0" ? "localhost" : backendHost;
  const backendUrl = `http://${host}:${backendPort}`;
  
  // Use VITE_PROXY_TARGET from process.env if available, fallback to loaded env or computed URL
  const proxyTarget = (typeof process !== "undefined" && process.env && process.env.VITE_PROXY_TARGET) || env.VITE_PROXY_TARGET || backendUrl;

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: proxyTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, "")
        }
      }
    },
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: "./src/setupTests.ts",
    }
  };
});
