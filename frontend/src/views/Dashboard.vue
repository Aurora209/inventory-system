<template>
  <div class="dashboard-page">
    <div class="container">
<!--      <div class="page-header">
       <h2>系统概览</h2>
        <p>实时监控库存和生产状态</p>
      </div> -->

      <!-- 统计卡片 -->
      <div class="stats-grid">
<!--        <div class="stat-card">
          <div class="stat-icon products">
            <i class="icon">📦</i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.products }}</h3>
            <p>产品总数</p>
          </div>
        </div> -->
       <div class="stat-card">
          <div class="stat-icon inventory">
            <i class="icon">💰</i>
          </div>
          <div class="stat-info">
            <h3>¥{{ formatCurrency(stats.inventoryValue) }}</h3>
            <p>库存总值</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon incoming">
            <i class="icon">📥</i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.incoming }}</h3>
            <p>今日入库</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon outgoing">
            <i class="icon">📤</i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.outgoing }}</h3>
            <p>今日出库</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon alerts">
            <i class="icon">⚠️</i>
          </div>
          <div class="stat-info">
            <h3>{{ stats.alerts }}</h3>
            <p>库存预警</p>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <div class="chart-card">
          <h3>库存预警</h3>
          <div class="alerts-list">
            <div v-if="limitedStockAlerts.length === 0" class="no-alerts">
              <p>暂无库存预警</p>
            </div>
            <div v-else class="alert-item" v-for="alert in limitedStockAlerts" :key="alert.id">
              <span class="alert-product">{{ alert.product_name }}</span>
              <span class="alert-sku">SKU: {{ alert.sku }}</span>
              <span class="alert-quantity">当前库存: {{ alert.current_quantity }}</span>
              <span class="alert-min">最低库存: {{ alert.min_stock }}</span>
              <span class="alert-status" :class="`status-${alert.status}`">
                {{ alert.status === 'low' ? '库存偏低' : '库存为零' }}
              </span>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3>近期交易</h3>

          <div class="transactions-filter" style="margin-bottom:12px">
            <label style="margin-right:8px">显示类型：</label>
            <select v-model="transactionFilter">
              <option value="">全部</option>
              <option value="in">采购订单（入库）</option>
              <option value="out">销售订单（出库）</option>
            </select>
          </div>

          <div class="recent-transactions">
            <div v-if="filteredRecentTransactions.length === 0" class="no-transactions">
              <p>暂无近期交易</p>
            </div>
            <div v-else class="transaction-item" v-for="transaction in filteredRecentTransactions" :key="transaction.id">
              <span class="transaction-product">{{ transaction.product_name }}</span>
              <span class="transaction-type" :class="`type-${transaction.transaction_type}`">
                {{ transaction.transaction_type === 'in' ? '入库' : '出库' }}
              </span>
              <span class="transaction-quantity">{{ transaction.quantity }}</span>
              <span class="transaction-date">{{ formatDate(transaction.transaction_date) }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        products: 0,
        inventoryValue: 0,
        incoming: 0,
        outgoing: 0,
        alerts: 0
      },
      recentTransactions: [],
      stockAlerts: [],
      // '' = 所有, 'in' = 采购/入库, 'out' = 销售/出库
      transactionFilter: ''
    }
  },
  computed: {
    // 限制库存预警只显示前五项
    limitedStockAlerts() {
      return Array.isArray(this.stockAlerts) ? this.stockAlerts.slice(0, 5) : []
    },
    // 根据筛选类型过滤近期交易并限制前五项
    filteredRecentTransactions() {
      let items = Array.isArray(this.recentTransactions) ? this.recentTransactions : []
      if (this.transactionFilter) {
        items = items.filter(t => String(t.transaction_type) === String(this.transactionFilter))
      }
      return items.slice(0, 5)
    }
  },
  mounted() {
    console.log('📊 Dashboard组件已加载')
    this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        // 获取统计信息
        const statsResponse = await fetch('/api/dashboard')
        if (statsResponse.ok) {
          const result = await statsResponse.json()
          if (result.success) {
            this.stats = {
              products: result.data.summary.total_products,
              inventoryValue: result.data.summary.total_inventory_value,
              incoming: result.data.summary.today_incoming,
              outgoing: result.data.summary.today_outgoing,
              alerts: result.data.summary.low_stock_count
            }
          } else {
            console.error('获取统计信息失败:', result.message)
            this.stats = {
              products: 0,
              inventoryValue: 0,
              incoming: 0,
              outgoing: 0,
              alerts: 0
            }
          }
        } else {
          console.error('获取统计信息失败:', statsResponse.status)
          this.stats = {
            products: 0,
            inventoryValue: 0,
            incoming: 0,
            outgoing: 0,
            alerts: 0
          }
        }
        
        // 获取库存预警
        const alertsResponse = await fetch('/api/dashboard/alerts')
        if (alertsResponse.ok) {
          const result = await alertsResponse.json()
          if (result.success) {
            this.stockAlerts = result.data.alerts || []
          } else {
            console.error('获取库存预警失败:', result.message)
            this.stockAlerts = []
          }
        } else {
          console.error('获取库存预警失败:', alertsResponse.status)
          this.stockAlerts = []
        }
        
        // 获取近期交易
        const transactionsResponse = await fetch('/api/dashboard/transactions')
        if (transactionsResponse.ok) {
          const result = await transactionsResponse.json()
          if (result.success) {
            this.recentTransactions = result.data.transactions || []
          } else {
            console.error('获取近期交易失败:', result.message)
            this.recentTransactions = []
          }
        } else {
          console.error('获取近期交易失败:', transactionsResponse.status)
          this.recentTransactions = []
        }
      } catch (error) {
        console.error('获取仪表板数据出错:', error)
        this.stats = {
          products: 0,
          inventoryValue: 0,
          incoming: 0,
          outgoing: 0,
          alerts: 0
        }
        this.stockAlerts = []
        this.recentTransactions = []
      }
    },
    formatCurrency(value) {
      return parseFloat(value || 0).toFixed(2)
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.dashboard-page {
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  margin: 0;
  font-size: 2.4rem;
  color: var(--dark-color);
}

.page-header p {
  margin: 0;
  font-size: 1.2rem;
  color: var(--secondary-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2rem;
  margin-right: 15px;
}

.stat-icon.products {
  color: var(--primary-color);
}

.stat-icon.inventory {
  color: var(--success-color);
}

.stat-icon.incoming {
  color: var(--info-color);
}

.stat-icon.outgoing {
  color: var(--warning-color);
}

.stat-icon.alerts {
  color: var(--danger-color);
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--dark-color);
  margin-bottom: 5px;
}

.stat-info p {
  margin: 0;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr; /* 上下堆叠 */
  gap: 20px;
  margin-bottom: 30px;
}

.transactions-filter {
  display: flex;
  align-items: center;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: var(--dark-color);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

/* 库存预警样式 */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--light-color);
  align-items: center;
}

.alert-product {
  flex: 1;
  font-weight: 500;
}

.alert-sku {
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.alert-quantity,
.alert-min {
  font-size: 0.9rem;
}

.alert-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  color: white;
}

.alert-status.status-low {
  background-color: var(--warning-color);
}

.alert-status.status-zero {
  background-color: var(--danger-color);
}

.no-alerts,
.no-transactions {
  text-align: center;
  padding: 20px;
  color: var(--secondary-color);
}

/* 近期交易样式 */
.recent-transactions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.transaction-item {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--light-color);
  align-items: center;
}

.transaction-product {
  flex: 1;
  font-weight: 500;
}

.transaction-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  color: white;
}

.transaction-type.type-in {
  background-color: var(--success-color);
}

.transaction-type.type-out {
  background-color: var(--info-color);
}

.transaction-quantity {
  font-weight: 500;
}

.transaction-date {
  color: var(--secondary-color);
  font-size: 0.9rem;
  margin-left: auto;
}

.debug-info {
  text-align: center;
  padding: 10px;
  background: var(--light-color);
  border-radius: 4px;
  margin-top: 20px;
  font-size: 0.9rem;
  color: var(--info-color);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .alert-item,
  .transaction-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .transaction-date {
    margin-left: 0;
  }
}
</style>