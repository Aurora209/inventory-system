<template>
  <div class="container">
    <div class="inventory-page">
      <!--库存管理 -->
      <!-- 统计卡片 -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon total">
            <i class="icon">📦</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalProducts || 0 }}</div>
            <div class="stat-label">总产品数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon value">
            <i class="icon">💰</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ formatCurrency(stats.totalValue) }}</div>
            <div class="stat-label">库存总值</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon incoming">
            <i class="icon">📥</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.todayIncoming || 0 }}</div>
            <div class="stat-label">今日入库</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon outgoing">
            <i class="icon">📤</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.todayOutgoing || 0 }}</div>
            <div class="stat-label">今日出库</div>
          </div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="action-bar">
        <div class="action-left">
          <button class="btn btn-primary" @click="showAddModal = true">
            <i class="icon">➕</i> 新增交易
          </button>
          <button class="btn btn-secondary" @click="startInventoryCheck">
            <i class="icon">📋</i> 库存盘点
          </button>
        </div>
        <div class="action-right">
          <div class="search-box">
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="搜索产品名称或SKU..."
              class="search-input"
            >
            <i class="search-icon">🔍</i>
          </div>
          <div class="category-dropdown">
            <select v-model="selectedCategory" class="category-select" @change="filterByCategory">
              <option value="">所有分类</option>
              <optgroup v-for="category in categoryTree" :key="category.id" :label="category.name">
                <option :value="category.id">
                  {{ category.name }}
                </option>
                <option 
                  v-for="subCategory in category.children" 
                  :key="subCategory.id" 
                  :value="subCategory.id"
                >
                  &nbsp;&nbsp;├─ {{ subCategory.name }}
                </option>
              </optgroup>
            </select>
            <i class="dropdown-icon">📂</i>
          </div>
          <select v-model="filterType" class="filter-select">
            <option value="">所有类型</option>
            <option value="in">入库</option>
            <option value="out">出库</option>
          </select>
        </div>
      </div>

      <!-- 库存列表 -->
      <div class="inventory-section">
        <div class="section-header">
          <h3>库存列表</h3>
          <div class="section-actions">
            <span class="total-count">共 {{ filteredProducts.length }} 个产品</span>
          </div>
        </div>

        <div class="table-container">
          <table class="inventory-table">
            <thead>
              <tr>
                <th class="col-checkbox">
                  <input type="checkbox" v-model="selectAll">
                </th>
                <th class="col-sku">SKU</th>
                <th class="col-name">产品名称</th>
                <th class="col-category">分类</th>
                <th class="col-stock">库存数量</th>
                <th class="col-price">单价</th>
                <th class="col-value">库存价值</th>
                <th class="col-status">状态</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProducts" :key="product.id" 
                  :class="{'selected': selectedProducts.includes(product.id)}">
                <td class="col-checkbox">
                  <input type="checkbox" 
                         :value="product.id" 
                         v-model="selectedProducts">
                </td>
                <td class="col-sku">{{ product.sku }}</td>
                <td class="col-name">{{ product.name }}</td>
                <td class="col-category">{{ getCategoryName(product.category_id) }}</td>
                <td class="col-stock">{{ product.quantity }}</td>
                <td class="col-price">¥{{ formatCurrency(product.price) }}</td>
                <td class="col-value">¥{{ formatCurrency(Number(product.quantity) * Number(product.price)) }}</td>
                <td class="col-status">
                  <span :class="'status-badge ' + getStockStatus(product)">
                    {{ getStockStatusText(product) }}
                  </span>
                </td>
                <td class="col-actions">
                  <button class="btn-icon" @click="editProduct(product)" title="编辑">
                    <i class="icon">✏️</i>
                  </button>
                  <button class="btn-icon danger" @click="deleteProduct(product.id)" title="删除">
                    <i class="icon">🗑️</i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 添加产品模态框 -->
      <div class="modal-overlay" v-if="showAddModal" @click="showAddModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>添加产品库存</h3>
            <button class="modal-close" @click="showAddModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addProduct">
              <div class="form-grid">
                <div class="form-group">
                  <label>SKU *</label>
                  <input type="text" v-model="newProduct.sku" required placeholder="输入产品SKU">
                </div>
                <div class="form-group">
                  <label>产品名称 *</label>
                  <input type="text" v-model="newProduct.name" required placeholder="输入产品名称">
                </div>
                <div class="form-group">
                  <label>分类</label>
                  <select v-model="newProduct.category">
                    <option value="">选择分类</option>
                    <option value="电子产品">电子产品</option>
                    <option value="电脑配件">电脑配件</option>
                    <option value="办公用品">办公用品</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>单位</label>
                  <select v-model="newProduct.unit">
                    <option value="个">个</option>
                    <option value="台">台</option>
                    <option value="件">件</option>
                    <option value="箱">箱</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>初始库存</label>
                  <input type="number" v-model.number="newProduct.quantity" min="0" placeholder="0">
                </div>
                <div class="form-group">
                  <label>单价 (¥)</label>
                  <input type="number" v-model.number="newProduct.price" step="0.01" min="0" placeholder="0.00">
                </div>
                <div class="form-group full-width">
                  <label>产品描述</label>
                  <textarea v-model="newProduct.description" placeholder="输入产品描述（可选）" rows="3"></textarea>
                </div>
              </div>
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="showAddModal = false">取消</button>
                <button type="submit" class="btn btn-primary">添加产品</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 库存盘点模态框 -->
      <div class="modal-overlay" v-if="showInventoryCheckModal" @click="showInventoryCheckModal = false">
        <div class="modal-content large" @click.stop>
          <div class="modal-header">
            <h3>库存盘点</h3>
            <button class="modal-close" @click="showInventoryCheckModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="inventory-check-header">
              <div class="header-info">
                <p>请选择要盘点的产品，或点击"全选"选择所有产品进行盘点。</p>
              </div>
              <div class="header-actions">
                <button class="btn btn-secondary" @click="selectAllForInventory">
                  {{ inventoryCheck.selectAll ? '取消全选' : '全选' }}
                </button>
              </div>
            </div>
            
            <div class="table-container">
              <table class="inventory-check-table">
                <thead>
                  <tr>
                    <th class="col-checkbox">
                      <input type="checkbox" v-model="inventoryCheck.selectAll" @change="toggleAllInventorySelection">
                    </th>
                    <th class="col-sku">SKU</th>
                    <th class="col-name">产品名称</th>
                    <th class="col-category">分类</th>
                    <th class="col-system-stock">系统库存</th>
                    <th class="col-actual-stock">实际库存</th>
                    <th class="col-difference">差异数量</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="product in inventoryCheck.products" :key="product.id">
                    <td class="col-checkbox">
                      <input type="checkbox" 
                             :value="product.id" 
                             v-model="inventoryCheck.selectedProducts">
                    </td>
                    <td class="col-sku">{{ product.sku }}</td>
                    <td class="col-name">{{ product.name }}</td>
                    <td class="col-category">{{ getCategoryName(product.category_id) }}</td>
                    <td class="col-system-stock">{{ product.systemQuantity }}</td>
                    <td class="col-actual-stock">
                      <input type="number" 
                             v-model.number="product.actualQuantity" 
                             @input="calculateDifference(product)"
                             min="0">
                    </td>
                    <td class="col-difference" 
                        :class="{
                          'positive': product.difference > 0,
                          'negative': product.difference < 0,
                          'zero': product.difference === 0
                        }">
                      {{ product.difference }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="inventory-summary">
              <div class="summary-item">
                <span class="label">盘点产品数:</span>
                <span class="value">{{ inventoryCheck.selectedProducts.length }}</span>
              </div>
              <div class="summary-item">
                <span class="label">盘盈产品数:</span>
                <span class="value positive">{{ inventoryProfitCount }}</span>
              </div>
              <div class="summary-item">
                <span class="label">盘亏产品数:</span>
                <span class="value negative">{{ inventoryLossCount }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showInventoryCheckModal = false">取消</button>
            <button class="btn btn-primary" @click="saveInventoryCheck" :disabled="!canSaveInventoryCheck">保存盘点结果</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Inventory',
  data() {
    return {
      products: [],
      recentTransactions: [],
      categories: [], // 添加分类数据
      categoryTree: [], // 添加分类树数据
      searchTerm: '',
      selectedCategory: '', // 添加选中的分类
      filterType: '',
      selectedProducts: [],
      showAddModal: false,
      showInventoryCheckModal: false, // 添加库存盘点模态框显示状态
      stats: {
        totalProducts: 0,
        totalValue: 0,
        todayIncoming: 0,
        todayOutgoing: 0
      },
      newProduct: {
        sku: '',
        name: '',
        category: '',
        quantity: 0,
        price: 0,
        unit: '个',
        description: '',
        minStock: 0,
        maxStock: 100
      },
      // 添加库存盘点相关数据
      inventoryCheck: {
        selectAll: false,
        selectedProducts: [],
        products: []
      }
    }
  },
  computed: {
    filteredProducts() {
      let filtered = this.products
      
      // 文本搜索过滤
      if (this.searchTerm) {
        const term = this.searchTerm.toLowerCase()
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(term) || 
          p.sku.toLowerCase().includes(term)
        )
      }
      
      // 分类过滤：如果选择的是一级分类，展示该一级分类及其二级分类下的所有产品；选择二级分类则只展示该二级分类的产品
      if (this.selectedCategory) {
        const findIds = (categories, targetId) => {
          for (const cat of categories) {
            if (String(cat.id) === String(targetId)) {
              const ids = [String(cat.id)];
              if (cat.children && cat.children.length) {
                ids.push(...cat.children.map(c => String(c.id)));
              }
              return ids;
            }
            if (cat.children && cat.children.length) {
              const res = findIds(cat.children, targetId);
              if (res) return res;
            }
          }
          return null;
        };

        const ids = findIds(this.categoryTree, this.selectedCategory) || [String(this.selectedCategory)];
        filtered = filtered.filter(p => ids.includes(String(p.category_id)));
      }
      
      return filtered
    },
    selectAll: {
      get() {
        return this.products.length > 0 && this.selectedProducts.length === this.products.length
      },
      set(value) {
        this.selectedProducts = value ? this.products.map(p => p.id) : []
      }
    },
    // 添加库存盘点相关的计算属性
    inventoryProfitCount() {
      return this.inventoryCheck.products
        .filter(p => this.inventoryCheck.selectedProducts.includes(p.id) && p.difference > 0)
        .length;
    },
    inventoryLossCount() {
      return this.inventoryCheck.products
        .filter(p => this.inventoryCheck.selectedProducts.includes(p.id) && p.difference < 0)
        .length;
    },
    canSaveInventoryCheck() {
      return this.inventoryCheck.selectedProducts.length > 0;
    }
  },
  mounted() {
    console.log('📦 Inventory组件已加载')
    this.loadProducts()
    this.loadCategories() // 加载分类数据
    this.loadCategoryTree() // 加载分类树数据
    this.loadRecentTransactions()
  },
  methods: {
    async loadProducts() {
      try {
        const response = await fetch('/api/products')
        if (response.ok) {
          const data = await response.json()
          // 检查是否是新的API格式（包含success字段）
          if (data && data.hasOwnProperty('success')) {
            if (data.success) {
              this.products = data.data || []
            } else {
              console.error('获取产品列表失败:', data.message)
              this.products = []
            }
          } else {
            // 兼容旧格式
            this.products = data || []
          }
          this.calculateStats()
        } else {
          console.error('获取产品列表失败:', response.status)
          this.products = []
          this.calculateStats()
        }
      } catch (error) {
        console.error('获取产品列表出错:', error)
        this.products = []
        this.calculateStats()
      }
    },
    
    // 添加加载分类的方法
    async loadCategories() {
      try {
        const response = await fetch('/api/categories/flat')
        if (response.ok) {
          const data = await response.json()
          // 检查是否是新的API格式（包含success字段）
          if (data && data.hasOwnProperty('success')) {
            if (data.success) {
              this.categories = data.data || []
            } else {
              console.error('获取分类列表失败:', data.message)
              this.categories = []
            }
          } else {
            // 兼容旧格式
            this.categories = data || []
          }
        } else {
          console.error('获取分类列表失败:', response.status)
        }
      } catch (error) {
        console.error('获取分类列表出错:', error)
      }
    },
    
    // 添加加载分类树的方法
    async loadCategoryTree() {
      try {
        const response = await fetch('/api/categories/tree')
        if (response.ok) {
          const data = await response.json()
          // 检查是否是新的API格式（包含success字段）
          if (data && data.hasOwnProperty('success')) {
            if (data.success) {
              this.categoryTree = Array.isArray(data.data.categories) ? data.data.categories : []
            } else {
              console.error('获取分类树失败:', data.message)
              this.categoryTree = []
            }
          } else {
            // 兼容旧格式
            this.categoryTree = Array.isArray(data.categories) ? data.categories : []
          }
        } else {
          console.error('获取分类树失败:', response.status)
          this.categoryTree = []
        }
      } catch (error) {
        console.error('获取分类树出错:', error)
        this.categoryTree = []
      }
    },
    
    // 添加分类筛选方法
    filterByCategory() {
      // 筛选逻辑将在computed属性中实现
    },
    
    // 添加库存盘点方法
    startInventoryCheck() {
      // 初始化库存盘点数据
      this.inventoryCheck.products = this.products.map(product => ({
        id: product.id,
        sku: product.sku,
        name: product.name,
        category_id: product.category_id,
        systemQuantity: product.quantity,
        actualQuantity: product.quantity, // 默认使用系统数量
        difference: 0
      }));
      
      this.inventoryCheck.selectedProducts = [];
      this.inventoryCheck.selectAll = false;
      this.showInventoryCheckModal = true;
    },
    
    toggleAllInventorySelection() {
      if (this.inventoryCheck.selectAll) {
        this.inventoryCheck.selectedProducts = this.inventoryCheck.products.map(p => p.id);
      } else {
        this.inventoryCheck.selectedProducts = [];
      }
    },
    
    selectAllForInventory() {
      if (this.inventoryCheck.selectedProducts.length === this.inventoryCheck.products.length) {
        // 如果已经全选，则取消全选
        this.inventoryCheck.selectedProducts = [];
        this.inventoryCheck.selectAll = false;
      } else {
        // 如果没有全选，则全选
        this.inventoryCheck.selectedProducts = this.inventoryCheck.products.map(p => p.id);
        this.inventoryCheck.selectAll = true;
      }
    },
    
    calculateDifference(product) {
      if (typeof product.actualQuantity === 'number') {
        product.difference = product.actualQuantity - product.systemQuantity;
      } else {
        product.difference = 0;
      }
    },
    
    async performInventoryCheck() {
      try {
        // 准备盘点数据
        const checkItems = this.inventoryCheck.products
          .filter(p => this.inventoryCheck.selectedProducts.includes(p.id))
          .map(p => ({
            product_id: p.id,
            system_quantity: p.systemQuantity,
            actual_quantity: p.actualQuantity,
            difference: p.difference
          }));

        // 调用后端API进行库存盘点
        const response = await fetch('/api/inventory/check', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ items: checkItems })
        });

        if (response.ok) {
          const data = await response.json();
          // 检查是否是新的API格式（包含success字段）
          if (data && data.hasOwnProperty('success')) {
            if (data.success) {
              this.showNotification('库存盘点完成', 'success');
              this.showInventoryCheckModal = false;
              // 重新加载产品数据
              await this.loadProducts();
            } else {
              this.showNotification('库存盘点失败: ' + (data.message || '未知错误'), 'error');
            }
          } else {
            // 兼容旧格式
            this.showNotification(data.message || '库存盘点完成', 'success');
            this.showInventoryCheckModal = false;
            // 重新加载产品数据
            await this.loadProducts();
          }
        } else {
          const errorData = await response.json();
          this.showNotification('库存盘点失败: ' + (errorData.message || '服务器错误'), 'error');
        }
      } catch (error) {
        console.error('库存盘点出错:', error);
        this.showNotification('库存盘点出错: ' + (error.message || '网络错误'), 'error');
      }
    },
    
    async loadRecentTransactions() {
      try {
        const response = await fetch('/api/transactions/recent')
        if (response.ok) {
          const data = await response.json()
          // 检查是否是新的API格式（包含success字段）
          if (data && data.hasOwnProperty('success')) {
            if (data.success) {
              this.recentTransactions = data.data.transactions || []
            } else {
              console.error('获取最近交易记录失败:', data.message)
              this.recentTransactions = []
            }
          } else {
            // 兼容旧格式
            this.recentTransactions = data.transactions || []
          }
        } else {
          console.error('获取最近交易记录失败:', response.status)
          this.recentTransactions = []
        }
      } catch (error) {
        console.error('获取最近交易记录出错:', error)
        this.recentTransactions = []
      }
    },

    calculateStats() {
      this.stats.totalProducts = this.products.length
      this.stats.totalValue = this.products.reduce((sum, p) => sum + (Number(p.quantity) * Number(p.price)), 0)
      this.stats.todayIncoming = this.recentTransactions
        .filter(t => t.transaction_type === 'in' && this.isToday(t.transaction_date))
        .reduce((sum, t) => sum + t.quantity, 0)
      this.stats.todayOutgoing = this.recentTransactions
        .filter(t => t.transaction_type === 'out' && this.isToday(t.transaction_date))
        .reduce((sum, t) => sum + t.quantity, 0)
    },

    isToday(date) {
      const today = new Date()
      const checkDate = new Date(date)
      return checkDate.toDateString() === today.toDateString()
    },

    getStockStatus(product) {
      if (product.quantity === 0) {
        return 'out-of-stock'
      } else if (product.min_stock && product.quantity <= product.min_stock) {
        return 'low-stock'
      } else if (product.max_stock && product.quantity >= product.max_stock) {
        return 'over-stock'
      }
      return 'normal'
    },

    getStockStatusText(product) {
      const status = this.getStockStatus(product)
      const statusMap = {
        'out-of-stock': '缺货',
        'low-stock': '库存低',
        'over-stock': '库存过高',
        'normal': '正常'
      }
      return statusMap[status]
    },

    formatCurrency(value) {
      const num = parseFloat(value);
      return isNaN(num) ? '0.00' : num.toFixed(2);
    },

    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString('zh-CN')
    },

    async addProduct() {
      try {
        const response = await fetch('/api/products', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            sku: this.newProduct.sku,
            name: this.newProduct.name,
            category_id: this.getCategoryIdByName(this.newProduct.category),
            quantity: this.newProduct.quantity,
            price: this.newProduct.price,
            unit: this.newProduct.unit,
            description: this.newProduct.description,
            min_stock: this.newProduct.minStock,
            max_stock: this.newProduct.maxStock
          })
        })
        
        if (response.ok) {
          const product = await response.json()
          this.products.push(product)
          this.showAddModal = false
          this.resetNewProduct()
          this.calculateStats()
        } else {
          console.error('添加产品失败:', response.status)
        }
      } catch (error) {
        console.error('添加产品出错:', error)
      }
    },
    
    getCategoryIdByName(categoryName) {
      // 这里应该根据分类名称获取分类ID
      // 由于目前没有分类API，暂时返回null
      return null
    },

    async deleteProduct(productId) {
      if (confirm('确定要删除这个产品吗？')) {
        try {
          const response = await fetch(`/api/products/${productId}`, {
            method: 'DELETE'
          })
          
          if (response.ok) {
            this.products = this.products.filter(p => p.id !== productId)
            this.calculateStats()
          } else {
            console.error('删除产品失败:', response.status)
          }
        } catch (error) {
          console.error('删除产品出错:', error)
        }
      }
    },

    resetNewProduct() {
      this.newProduct = {
        sku: '',
        name: '',
        category: '',
        quantity: 0,
        price: 0,
        unit: '个',
        description: '',
        minStock: 0,
        maxStock: 100
      }
    },
    
    getCategoryName(categoryId) {
      if (!categoryId) return '未分类';
      const category = this.categories.find(c => c.id == categoryId);
      return category ? category.name : '未分类';
    }
  }
}
</script>

<style scoped>
.inventory-page {
  padding: 20px 0;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  color: var(--dark-color);
  margin-bottom: 10px;
  font-size: 2.2rem;
  font-weight: 700;
}

.page-header p {
  color: var(--secondary-color);
  margin-bottom: 0;
  font-size: 1.1rem;
}

/* 统计卡片 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 1.5rem;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.value {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.incoming {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.outgoing {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--dark-color);
  margin-bottom: 4px;
}

.stat-label {
  color: var(--secondary-color);
  font-size: 0.9rem;
  font-weight: 500;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.action-left {
  display: flex;
  gap: 12px;
}

.action-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-box {
  position: relative;
  min-width: 280px;
}

.search-input {
  width: 100%;
  padding: 10px 16px 10px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary-color);
}

/* 添加分类下拉列表样式 */
.category-dropdown {
  position: relative;
  min-width: 200px;
}

.category-select {
  width: 100%;
  padding: 10px 16px 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.95rem;
  background: white;
  appearance: none;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--dark-color);
}

.category-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.dropdown-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary-color);
  pointer-events: none;
}

.filter-select {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: white;
  min-width: 120px;
}

/* 分区样式 */
.inventory-section,
.transactions-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.section-header h3 {
  margin: 0;
  color: var(--dark-color);
  font-size: 1.3rem;
  font-weight: 600;
}

.total-count {
  color: var(--secondary-color);
  font-size: 0.9rem;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  border-radius: 8px;
}

.inventory-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
}

.inventory-table th {
  background: var(--light-color);
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--dark-color);
  border-bottom: 2px solid var(--border-color);
  white-space: nowrap;
}

.inventory-table td {
  padding: 16px 12px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.inventory-table tbody tr {
  transition: all 0.2s ease;
}

.inventory-table tbody tr:hover {
  background: #f8f9fa;
}

.inventory-table tbody tr.selected {
  background: #e3f2fd;
}

/* 列宽设置 */
.col-checkbox {
  width: 40px;
  text-align: center;
}

.col-sku {
  width: 120px;
}

.col-name {
  min-width: 200px;
}

.col-category {
  width: 100px;
}

.col-stock {
  width: 140px;
}

.col-price {
  width: 100px;
}

.col-value {
  width: 120px;
}

.col-status {
  width: 80px;
}

.col-actions {
  width: 120px;
}

/* 表格内容样式 */
.sku-code {
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.85rem;
  color: var(--dark-color);
}

.product-info .product-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.product-info .product-desc {
  font-size: 0.85rem;
  color: var(--secondary-color);
  line-height: 1.3;
}

.category-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.stock-info .stock-quantity {
  font-weight: 600;
  margin-bottom: 2px;
}

.stock-info .stock-range {
  font-size: 0.8rem;
  color: var(--secondary-color);
}

.stock-range .min-stock {
  margin-right: 8px;
}

.price, .value {
  font-weight: 600;
  color: var(--success-color);
}

/* 状态标签 */
.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
  display: inline-block;
  min-width: 60px;
}

.status-badge.out-of-stock {
  background: #ffebee;
  color: #c62828;
}

.status-badge.low-stock {
  background: #fff3e0;
  color: #ef6c00;
}

.status-badge.over-stock {
  background: #e3f2fd;
  color: #1565c0;
}

.status-badge.normal {
  background: #e8f5e8;
  color: #2e7d32;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.btn-icon:hover {
  transform: scale(1.1);
}

.btn-info {
  background: #e3f2fd;
  color: #1976d2;
}

.btn-warning {
  background: #fff3e0;
  color: #ef6c00;
}

.btn-danger {
  background: #ffebee;
  color: #c62828;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--secondary-color);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  margin-bottom: 12px;
  color: var(--dark-color);
}

.empty-state p {
  margin-bottom: 24px;
  font-size: 1rem;
}

/* 交易记录 */
.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transaction-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: var(--light-color);
  border-radius: 8px;
  border-left: 4px solid transparent;
  transition: all 0.2s ease;
}

.transaction-item.type-in {
  border-left-color: var(--success-color);
}

.transaction-item.type-out {
  border-left-color: var(--danger-color);
}

.transaction-item:hover {
  background: #f8f9fa;
  transform: translateX(4px);
}

.transaction-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 1.2rem;
}

.transaction-item.type-in .transaction-icon {
  background: #e8f5e8;
  color: var(--success-color);
}

.transaction-item.type-out .transaction-icon {
  background: #ffebee;
  color: var(--danger-color);
}

.transaction-info {
  flex: 1;
}

.transaction-product {
  font-weight: 600;
  margin-bottom: 4px;
}

.transaction-meta {
  display: flex;
  gap: 12px;
  font-size: 0.85rem;
  color: var(--secondary-color);
}

.transaction-type {
  text-transform: uppercase;
  font-weight: 600;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-content.large {
  max-width: 90%;
  max-height: 90vh;
}

/* 库存盘点模态框样式 */
.inventory-check-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.header-info p {
  margin: 0;
  color: var(--secondary-color);
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 盘点表格 */
.inventory-check-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.inventory-check-table th,
.inventory-check-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.inventory-check-table th {
  background: var(--light-color);
  font-weight: 600;
  color: var(--dark-color);
  white-space: nowrap;
}

/* 盘点表格列宽设置 */
.col-system-stock,
.col-actual-stock,
.col-difference {
  width: 120px;
  text-align: center;
}

.col-actual-stock input {
  width: 80px;
  padding: 6px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  text-align: center;
  font-size: 0.95rem;
}

.col-actual-stock input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

/* 差异列样式 */
.col-difference {
  font-weight: 600;
}

.col-difference.positive {
  color: var(--success-color);
}

.col-difference.negative {
  color: var(--danger-color);
}

.col-difference.zero {
  color: var(--secondary-color);
}

/* 盘点摘要 */
.inventory-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 24px;
  padding: 16px;
  background: var(--light-color);
  border-radius: 8px;
  font-size: 0.95rem;
}

.summary-item {
  text-align: center;
  flex: 1;
}

.summary-item:not(:last-child) {
  border-right: 1px solid var(--border-color);
}

.summary-item .label {
  display: block;
  margin-bottom: 4px;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.summary-item .value {
  font-size: 1.3rem;
  font-weight: 700;
}

.summary-item .value.positive {
  color: var(--success-color);
}

.summary-item .value.negative {
  color: var(--danger-color);
}

/* 模态框底部操作栏 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: white;
  border-radius: 0 0 12px 12px;
  margin-top: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--secondary-color);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background: var(--light-color);
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--dark-color);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-left,
  .action-right {
    justify-content: center;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .transaction-meta {
    flex-direction: column;
    gap: 4px;
  }
}

@media (max-width: 480px) {
  .inventory-section,
  .transactions-section {
    padding: 16px;
  }
  
  .modal-content {
    margin: 10px;
  }
  
  .modal-body {
    padding: 16px;
  }
}
</style>