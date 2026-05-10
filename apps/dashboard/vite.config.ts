import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
  },
  test: {
    // Use node environment for unit tests that don't need DOM.
    // Component rendering tests are integration tests; T4 tests focus on logic.
    environment: "node",
    globals: false,
  },
});
