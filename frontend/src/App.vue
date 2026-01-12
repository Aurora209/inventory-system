<template>
  <div id="app">
    <header class="app-header">
      <div class="header-content">
      </div>
    </header>
    
    <div class="page-title" v-if="$route.meta.title">
      <div class="title-container">
        <h1>{{ $route.meta.title }}</h1>
        <p class="subtitle">{{ getPageSubtitle($route.meta.title) }}</p>
      </div>
    </div>
    
    <nav class="main-nav">
      <div class="nav-container">
        <ul class="nav-list">
          <li>
            <router-link to="/" class="nav-link" exact-active-class="active">
              仪表板
            </router-link>
          </li>
          <li>
            <router-link to="/products" class="nav-link" active-class="active">
              产品管理
            </router-link>
          </li>
          <li>
            <router-link to="/purchase-orders" class="nav-link" active-class="active">
              采购订单
            </router-link>
          </li>
          <li>
            <router-link to="/sales-orders" class="nav-link" active-class="active">
              销售订单
            </router-link>
          </li>
          <li>
            <router-link to="/bom" class="nav-link" active-class="active">
              BOM管理
            </router-link>
          </li>
          <li>
            <router-link to="/production" class="nav-link" active-class="active">
              生产管理
            </router-link>
          </li>
          <li>
            <router-link to="/inventory" class="nav-link" active-class="active">
              库存管理
            </router-link>
          </li>
          <li class="dropdown">
            <a href="javascript:void(0)" class="nav-link dropdown-toggle">辅助工具</a>
            <ul class="dropdown-menu">
              <li>
                <router-link to="/unit-converter" class="nav-link" active-class="active">
                  单位换算器
                </router-link>
              </li>
              <li>
                <router-link to="/exchange-rate" class="nav-link" active-class="active">
                  汇率换算
                </router-link>
              </li>
              <li>
                <router-link to="/categories" class="nav-link" active-class="active">
                  产品分类
                </router-link>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view></router-view>
    </main>
    
    <footer class="page-footer">
      <div class="footer-content">
        <p>&copy; 2025 库存管理系统. 保留所有权利.</p>
        <div class="footer-links">
          <a href="javascript:void(0)">隐私政策</a>
          <a href="javascript:void(0)">使用条款</a>
          <a href="javascript:void(0)">联系我们</a>
        </div>
      </div>
    </footer>
    
    <Notification ref="notification" />
    
    <!-- 调试信息 -->
    <div v-if="false" class="debug-info">
      <p>当前路由: {{ $route.path }}</p>
      <p>路由参数: {{ $route.params }}</p>
    </div>
  </div>
</template>

<script>
import Notification from './components/Notification.vue'

export default {
  name: 'App',
  components: {
    Notification
  },
  methods: {
    showNotification(message, type = 'info') {
      if (this.$refs.notification) {
        this.$refs.notification.showNotification(message, type)
      } else {
        console.log('📢 通知:', message, type)
      }
    },
    getPageSubtitle(title) {
      const subtitles = {
        '仪表板': '系统概览和关键指标',
        '产品管理': '管理产品信息、库存和分类',
        '订单管理': '管理采购订单和销售订单',
        'BOM管理': '管理产品的物料清单和成本计算',
        '生产管理': '制定和跟踪生产计划',
        '库存管理': '监控库存水平和交易记录',
        '单位转换': '在不同单位之间进行数值转换',
        '汇率转换': '实时汇率转换和计算',
        '产品分类': '管理产品分类和层级结构'
      }
      return subtitles[title] || ''
    }
  },
  provide() {
    return {
      showNotification: this.showNotification
    }
  },
  mounted() {
    // 提供全局通知方法
    this.$root.showNotification = this.showNotification
    console.log('🏠 App组件已挂载')
    console.log('📍 当前路由:', this.$route.path)
    console.log('🛣️ 路由实例:', this.$router)
    
    // 测试路由方法
    setTimeout(() => {
      console.log('🧪 测试路由导航...')
    }, 1000)
  }
}
</script>

<style>
/* 全局样式变量 */
:root {
  --primary-color: #4a90e2;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  --light-color: #f8f9fa;
  --dark-color: #343a40;
  --border-color: #dee2e6;
  --background-color: #f5f7fa;
  --text-color: #212529;
  --nav-width: 1200px;
  --sidebar-width: 250px;
  --header-height: 60px;
  --transition-speed: 0.3s;
}

/* 基础样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 容器 */
.container {
  max-width: var(--nav-width);
  margin: 0 auto;
  padding: 0 20px;
}

/* 页面标题 */
.page-title {
  padding: 15px 0;
  margin-bottom: 20px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}

/* 页面头部 */
.app-header {
  text-align: center;
  padding: 10px 0;
  background-color: white;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.header-content {
  max-width: var(--nav-width);
  margin: 0 auto;
  padding: 0 20px;
}

.app-header h1 {
  font-size: 2.5rem;
  color: var(--dark-color);
  margin-bottom: 10px;
}

.app-header .subtitle {
  font-size: 1.1rem;
  color: var(--secondary-color);
}

/* 导航菜单 */
.main-nav {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  max-width: 1120px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}

.nav-list {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
  flex-wrap: wrap;
}

.nav-list > li {
  position: relative;
}

.nav-link {
  display: block;
  padding: 15px 20px;
  text-decoration: none;
  color: var(--text-color);
  font-weight: 500;
  transition: all var(--transition-speed);
  border-radius: 4px;
  margin: 5px;
}

.nav-link:hover,
.nav-link.active {
  background-color: var(--primary-color);
  color: white;
}

/* 下拉菜单 */
.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  list-style: none;
  padding: 10px 0;
  min-width: 150px;
  z-index: 100;
  display: none;
}

.dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-menu .nav-link {
  margin: 0;
  border-radius: 0;
}

.dropdown-menu .nav-link:hover {
  background-color: var(--light-color);
  color: var(--primary-color);
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  padding: 0 20px 40px;
}

/* 页脚 */
.page-footer {
  background-color: var(--dark-color);
  color: white;
  padding: 30px 0;
  margin-top: auto;
}

.footer-content {
  max-width: var(--nav-width);
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  flex-wrap: wrap;
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-links a {
  color: white;
  text-decoration: none;
  transition: opacity var(--transition-speed);
}

.footer-links a:hover {
  text-decoration: underline;
}

/* 调试信息 */
.debug-info {
  position: fixed;
  bottom: 10px;
  right: 10px;
  background: rgba(0,0,0,0.8);
  color: white;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 1000;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 10px;
  }
  
  .nav-list {
    flex-direction: column;
  }
  
  .nav-list .dropdown-menu {
    position: static;
    display: block;
    box-shadow: none;
    border: none;
    padding-left: 20px;
  }
  
  .footer-links {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  
  .page-footer {
    padding: 15px 0;
  }
  
  .page-title,
  .main-nav {
    max-width: 100%;
  }
}
</style>

<style>
/* 全局样式变量 */
:root {
  --primary-color: #4a90e2;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  --light-color: #f8f9fa;
  --dark-color: #343a40;
  --border-color: #dee2e6;
  --background-color: #f5f7fa;
  --text-color: #212529;
  --nav-width: 1200px;
  --sidebar-width: 250px;
  --header-height: 60px;
  --transition-speed: 0.3s;
}

/* 基础样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 页面标题 */
.page-title {
  padding: 15px 0;
  margin-bottom: 20px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}

.title-container {
  max-width: var(--nav-width);
  margin: 0 auto;
  padding: 0 20px;
  text-align: center;
}

.title-container h1 {
  font-size: 2rem;
  color: var(--dark-color);
  margin: 0 0 8px 0;
}

.title-container .subtitle {
  font-size: 1.1rem;
  color: var(--secondary-color);
  margin: 10px 0 0;
  font-weight: normal;
}

/* 按钮样式 */
.btn {
  display: inline-block;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all var(--transition-speed);
  text-decoration: none;
  text-align: center;
  font-size: 0.9rem;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: #357abd;
}

.btn-secondary {
  background-color: var(--secondary-color);
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: var(--danger-color);
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-success {
  background-color: var(--success-color);
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.btn-warning {
  background-color: var(--warning-color);
  color: white;
}

.btn-warning:hover {
  background-color: #e0a800;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 页面头部 */
.app-header {
  text-align: center;
  padding: 10px 0;
  background-color: white;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.header-content {
  max-width: var(--nav-width);
  margin: 0 auto;
  padding: 0 20px;
}

/* 导航菜单 */
.main-nav {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.nav-container {
  max-width: var(--nav-width);
  margin: 0 auto;
  padding: 0 20px;
}

.nav-list {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
  flex-wrap: wrap;
}

.nav-list > li {
  position: relative;
}

.nav-link {
  display: block;
  padding: 15px 20px;
  text-decoration: none;
  color: var(--text-color);
  font-weight: 500;
  transition: all var(--transition-speed);
  border-radius: 4px;
  margin: 5px;
}

.nav-link:hover,
.nav-link.active {
  background-color: var(--primary-color);
  color: white;
}

/* 下拉菜单 */
.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  list-style: none;
  padding: 10px 0;
  min-width: 150px;
  z-index: 100;
  display: none;
}

.dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-menu .nav-link {
  margin: 0;
  border-radius: 0;
}

.dropdown-menu .nav-link:hover {
  background-color: var(--light-color);
  color: var(--primary-color);
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  padding: 0 20px 40px;
  max-width: var(--nav-width);
  margin: 0 auto;
  width: 100%;
}

/* 页脚 */
.page-footer {
  background-color: var(--dark-color);
  color: white;
  padding: 30px 0;
  margin-top: auto;
}

.footer-content {
  max-width: var(--nav-width);
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  flex-wrap: wrap;
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-links a {
  color: white;
  text-decoration: none;
  transition: opacity var(--transition-speed);
}

.footer-links a:hover {
  text-decoration: underline;
}

/* 表单样式 */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color var(--transition-speed);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.25);
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.data-table th,
.data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  background-color: var(--light-color);
  font-weight: 600;
  color: var(--dark-color);
}

.data-table tbody tr:hover {
  background-color: #f8f9fa;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--secondary-color);
}

/* 状态标签 */
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  color: white;
}

.status-pending {
  background-color: var(--warning-color);
}

.status-processing {
  background-color: var(--info-color);
}

.status-completed {
  background-color: var(--success-color);
}

.status-cancelled {
  background-color: var(--danger-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-list {
    flex-direction: column;
  }
  
  .nav-list .dropdown-menu {
    position: static;
    display: block;
    box-shadow: none;
    border: none;
    padding-left: 20px;
  }
  
  .footer-links {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  
  .page-footer {
    padding: 15px 0;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .title-container h1 {
    font-size: 1.5rem;
  }
  
  .main-content {
    padding: 0 10px 40px;
  }
}
</style>