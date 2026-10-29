import vue from "@vitejs/plugin-vue";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const proxy = {
    "/api": {
      target: env.VITE_PROXY_TARGET || "http://localhost:8080",
      changeOrigin: true,
    },
    "/media": {
      target: env.VITE_PROXY_TARGET || "http://localhost:8080",
      changeOrigin: true,
    },
  };
  return {
    plugins: [vue()],
    server: { port: 5173, strictPort: true, proxy },
    preview: { proxy },
  };
});
