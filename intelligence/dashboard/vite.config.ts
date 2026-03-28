import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  // Makes the built app work under a subpath like /console/ when deployed as static files.
  base: './',
  plugins: [react()],
})
