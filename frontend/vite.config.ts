import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  // Keep local Nitro off for faster iteration; enable when deploying.
  nitro: false,
  vite: {
    server: {
      port: 3000,
      proxy: {
        "/api": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
        },
        "/uploads": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
        },
      },
    },
  },
});
