import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/medicines': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/cart': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/serviceability': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/orders': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/coupons': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
