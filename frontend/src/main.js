import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

console.log('🔄 开始初始化Vue应用...')

// 创建Vue应用实例
const app = createApp(App)

// 使用路由
app.use(router)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('❌ Vue错误:', err)
  console.error('📍 发生在组件:', instance?.$options?.name || '未知组件')
  console.error('📝 错误信息:', info)
  
  // 显示错误通知
  if (typeof window !== 'undefined' && window.$root?.showNotification) {
    window.$root.showNotification('应用发生错误', 'error')
  }
}

// 全局属性 - 用于调试
app.config.globalProperties.$log = {
  info: (...args) => console.log('ℹ️ ', ...args),
  error: (...args) => console.error('❌', ...args),
  warn: (...args) => console.warn('⚠️', ...args)
}

// 挂载应用
try {
  console.log('📌 准备挂载Vue应用...')
  
  router.isReady().then(() => {
    console.log('✅ 路由准备就绪')
    app.mount('#app')
    console.log('🎉 Vue应用已成功挂载到 #app')
    
    // 检查路由状态
    console.log('📍 当前路由:', router.currentRoute.value)
  }).catch((error) => {
    console.error('❌ 路由准备失败:', error)
    // 即使路由有问题也尝试挂载应用
    app.mount('#app')
  })
} catch (error) {
  console.error('💥 应用挂载失败:', error)
}