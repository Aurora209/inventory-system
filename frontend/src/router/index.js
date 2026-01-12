import { createRouter, createWebHistory } from 'vue-router'

// 使用正确的相对路径导入组件
const Dashboard = () => import('../views/Dashboard.vue')
const Products = () => import('../views/Products.vue')
const Orders = () => import('../views/Orders.vue')
const PurchaseOrders = () => import('../views/PurchaseOrders.vue')
const SalesOrders = () => import('../views/SalesOrders.vue')
const BOM = () => import('../views/BOM.vue')
const Production = () => import('../views/Production.vue')
const Inventory = () => import('../views/Inventory.vue')
const UnitConverter = () => import('../views/UnitConverter.vue')
const ExchangeRate = () => import('../views/ExchangeRate.vue')
const Categories = () => import('../views/Categories.vue')
const PackingList = () => import('../views/PackingList.vue')
const Reports = () => import('../views/Reports.vue')

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '仪表板' }
  },
  {
    path: '/products',
    name: 'Products',
    component: Products,
    meta: { title: '产品管理' }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders,
    meta: { title: '订单管理' }
  },
  {
    path: '/purchase-orders',
    name: 'PurchaseOrders',
    component: PurchaseOrders,
    meta: { title: '采购订单' }
  },
  {
    path: '/sales-orders',
    name: 'SalesOrders',
    component: SalesOrders,
    meta: { title: '销售订单' }
  },
  {
    path: '/bom',
    name: 'BOM',
    component: BOM,
    meta: { title: 'BOM管理' }
  },
  {
    path: '/production',
    name: 'Production',
    component: Production,
    meta: { title: '生产管理' }
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: Inventory,
    meta: { title: '库存管理' }
  },
  {
    path: '/unit-converter',
    name: 'UnitConverter',
    component: UnitConverter,
    meta: { title: '单位转换' }
  },
  {
    path: '/exchange-rate',
    name: 'ExchangeRate',
    component: ExchangeRate,
    meta: { title: '汇率转换' }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: Categories,
    meta: { title: '产品分类' }
  },
  {
    path: '/packing-list',
    name: 'PackingList',
    component: PackingList,
    meta: { title: '装箱单' }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { title: '报表中心' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 添加调试信息
router.beforeEach((to, from, next) => {
  console.log('🚀 路由导航:', from.name || from.path, '→', to.name || to.path)
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 库存管理系统`
  }
  
  next()
})

router.afterEach((to, from) => {
  console.log('✅ 路由完成:', to.name || to.path)
})

// 错误处理
router.onError((error) => {
  console.error('❌ 路由错误:', error)
  
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    const chunkMatch = error.message.match(/(\w+-\w+)\.js/)
    const chunkName = chunkMatch ? chunkMatch[1] : 'unknown'
    console.error(`📦 组件块加载失败: ${chunkName}`)
  }
})

export default router