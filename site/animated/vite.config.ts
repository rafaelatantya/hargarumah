import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite must not write into a parent of its root, so we keep outDir as the
// default `dist/`. The deploy workflow stages the dist content under
// <site>/animated/ so the production URL is clean (`/animated/`, no /dist/).
// Locally `npm run dev` (Vite dev server) and `npm run build` + `npm run
// preview` both work as expected.
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    target: 'es2022',
    chunkSizeWarningLimit: 1500,
  },
})
