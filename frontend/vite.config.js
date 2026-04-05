import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  preview: {
    allowedHosts: ["frontend-production-ca2b.up.railway.app"],
  },
  plugins: [react()],
})
