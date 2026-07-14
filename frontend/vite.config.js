import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        port: 5173,
        host: true,
        proxy: {
            '/api': {
                // In Docker the backend is reachable as the compose service name;
                // set VITE_PROXY_TARGET=http://backend:8000 there. Defaults to localhost for local dev.
                target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
    build: {
        outDir: 'dist',
        sourcemap: true,
    },
});
