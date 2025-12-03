import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to the backend server running on port 8000
      '/chat': 'http://localhost:8000',
      '/agent': 'http://localhost:8000',
      '/job': 'http://localhost:8000',
      '/files': 'http://localhost:8000',
      '/static': 'http://localhost:8000'
    }
  }
});