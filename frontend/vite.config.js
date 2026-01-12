import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 8081,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false
      }
    },
    // 添加热重载配置
    hmr: {
      overlay: true
    }
  },
  build: {
    outDir: '../backend/static',
    emptyOutDir: true,
    // 确保块分割正确
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router'],
          utils: ['axios']
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  // 确保正确处理 Vue 组件
  optimizeDeps: {
    include: ['vue', 'vue-router', 'axios']
  }
})