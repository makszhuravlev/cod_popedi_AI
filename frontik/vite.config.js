import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
    allowedHosts: ["katuscha.ssrv.su", "localhost", "127.0.0.1", "10.0.8.15"],
  },
});
