import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';

function apiLogger() {
  return {
    name: 'api-logger',
    configureServer(server) {
      // возврат последнего сохранённого ответа
      server.middlewares.use('/api/testdata', (req, res) => {
        const dir = path.join(process.cwd(), 'dev_logs');
        fs.mkdirSync(dir, { recursive: true });
        const files = fs
          .readdirSync(dir)
          .filter((f) => f.startsWith('api_'))
          .sort();
        if (!files.length) {
          res.statusCode = 404;
          res.end('No log files');
          return;
        }
        const file = files[files.length - 1];
        const data = fs.readFileSync(path.join(dir, file));
        res.setHeader('Content-Type', 'application/json');
        res.end(data);
      });

      server.middlewares.use((req, res, next) => {
        if (!req.url.startsWith('/api') || req.url === '/api/testdata') {
          return next();
        }
        const chunks = [];
        const origWrite = res.write.bind(res);
        const origEnd = res.end.bind(res);
        res.write = (chunk, ...args) => {
          if (chunk) chunks.push(Buffer.from(chunk));
          return origWrite(chunk, ...args);
        };
        res.end = (chunk, ...args) => {
          if (chunk) chunks.push(Buffer.from(chunk));
          const body = Buffer.concat(chunks).toString();
          const dir = path.join(process.cwd(), 'dev_logs');
          fs.mkdirSync(dir, { recursive: true });
          const file = path.join(dir, `api_${Date.now()}.json`);
          fs.writeFileSync(file, body);
          return origEnd(chunk, ...args);
        };
        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), apiLogger()],
  build: {
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
});
