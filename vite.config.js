import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  server: {
    port: 57843,
  },
  preview: {
    port: 57844,
  },
  build: {
    outDir: "dist",
    assetsInlineLimit: 0,
  },
});
