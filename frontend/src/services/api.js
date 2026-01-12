import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 使用相对路径，由Vite代理处理
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('🚀 请求发送:', config.method?.toUpperCase(), config.url, config.data || config.params)
    return config
  },
  error => {
    console.error('❌ 请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('✅ 响应接收:', response.config.url, response.status, response.data)
    // 根据后端API响应格式处理数据
    if (response.data && response.data.hasOwnProperty('success')) {
      return response.data
    }
    // 如果不是标准格式，直接返回数据
    return response.data || response
  },
  error => {
    console.error('❌ 响应错误:', error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// 产品相关API
export const productApi = {
  getProducts: () => api.get('/products'),
  getNonCompositeProducts: (params) => api.get('/products/non-composite', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
  createProduct: (data) => api.post('/products', data),
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/products/${id}`)
}

// 分类相关API
export const categoryApi = {
  getCategories: () => api.get('/categories'),
  getCategoryTree: () => api.get('/categories/tree'),
  createCategory: (data) => api.post('/categories', data),
  deleteCategory: (id) => api.delete(`/categories/${id}`),
  getCategoryUsage: (id) => api.get(`/categories/${id}/usage`)
}

// BOM相关API
export const bomApi = {
  getBom: (params) => api.get('/bom', { params }),
  createBomItem: (data) => api.post('/bom', data),
  updateBomItem: (id, data) => api.put(`/bom/${id}`, data),
  deleteBomItem: (id) => api.delete(`/bom/${id}`),
  deleteProductBom: (productId) => api.delete(`/bom/product/${productId}`)
}

// 订单相关API
export const orderApi = {
  getOrders: () => api.get('/orders'),
  getOrder: (id) => api.get(`/orders/${id}`),
  createOrder: (data) => api.post('/orders', data),
  updateOrder: (id, data) => api.put(`/orders/${id}`, data),
  deleteOrder: (id) => api.delete(`/orders/${id}`)
}

// 生产计划相关API
export const productionApi = {
  getProductionPlans: () => api.get('/production'),
  createProductionPlan: (data) => api.post('/production', data),
  updateProductionPlan: (id, data) => api.put(`/production/${id}`, data),
  deleteProductionPlan: (id) => api.delete(`/production/${id}`)
}

// 交易记录相关API
export const transactionApi = {
  getTransactions: (params) => api.get('/transactions', { params }),
  createTransaction: (data) => api.post('/transactions', data),
  getRecentTransactions: () => api.get('/transactions/recent')
}

// 库存相关API
export const inventoryApi = {
  checkInventory: (data) => api.post('/inventory/check', data)
}

// 报表相关API
export const reportApi = {
  exportBomExcel: () => api.get('/reports/bom/export', { responseType: 'blob' }),
  getMaterialRequirements: () => api.get('/reports/material-requirements'),
  getCostAnalysis: () => api.get('/reports/cost-analysis'),
  getPurchaseList: () => api.get('/reports/purchase-list')
}

// 默认导出API实例
export default api