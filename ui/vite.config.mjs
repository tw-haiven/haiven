// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  esbuild: {
    include: /\.js$/,
    exclude: [],
    loader: "jsx",
  },
  test: {
    environment: "jsdom",
    globals: true,
    include: ["**/*.test.{js,jsx,ts,tsx}"],
    setupFiles: "@testing-library/jest-dom",
    mockReset: true,
    testTimeout: 10000, // 10 seconds default timeout
  },
});
