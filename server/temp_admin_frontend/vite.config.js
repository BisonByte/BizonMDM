import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/devices': { // This is for the /devices endpoint directly
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/logs': { // This is for the /logs endpoint directly
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});