import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In dev, proxy /api to the gateway and strip the prefix so /api/agent/query
// reaches the gateway as /agent/query (matching the nginx proxy in prod).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
