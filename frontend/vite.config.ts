import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/database": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/sarsa": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/assets": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
