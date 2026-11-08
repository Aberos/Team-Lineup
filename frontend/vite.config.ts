import path from "node:path"

import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vitest/config"

function normalizePrefix(prefix: string | undefined): string {
  const trimmed = (prefix ?? "").trim().replace(/\/+$/, "")
  if (trimmed === "") {
    return ""
  }
  return trimmed.startsWith("/") ? trimmed : `/${trimmed}`
}

export default defineConfig(({ command }) => {
  const isBuild = command === "build"
  const appPrefix = isBuild ? normalizePrefix(process.env.APP_PREFIX) : ""

  return {
    plugins: [react(), tailwindcss()],
    base: isBuild ? `${appPrefix}/static/` : "/",
    define: {
      __APP_PREFIX__: JSON.stringify(appPrefix),
    },
    resolve: {
      alias: {
        "@": path.resolve(import.meta.dirname, "./src"),
      },
    },
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: process.env.VITE_API_TARGET ?? "http://localhost:8000",
          changeOrigin: false,
        },
      },
    },
    build: {
      outDir: "dist",
      emptyOutDir: true,
    },
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: "./src/test/setup.ts",
    },
  }
})
