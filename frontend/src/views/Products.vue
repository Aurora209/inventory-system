<template>
  <div class="container">
    <div class="products-page">
      <!-- 产品管理 -->
      
      <!-- 统计卡片 -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon total">
            <i class="icon">📦</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ Array.isArray(products) ? products.length : 0 }}</div>
            <div class="stat-label">产品总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon low">
            <i class="icon">⚠️</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ Array.isArray(lowStockProducts) ? lowStockProducts.length : 0 }}</div>
            <div class="stat-label">低库存</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon out">
            <i class="icon">❌</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ Array.isArray(outOfStockProducts) ? outOfStockProducts.length : 0 }}</div>
            <div class="stat-label">缺货产品</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon category">
            <i class="icon">📂</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ Array.isArray(categoryTree) ? categoryTree.length : 0 }}</div>
            <div class="stat-label">产品分类</div>
          </div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="action-bar">
        <div class="action-controls">
          <div class="control-group action-buttons">
            <button class="btn btn-primary" @click="showAddModal = true">
              <i class="icon">➕</i> 添加产品
            </button>
          </div>
          <div class="control-group action-buttons">
            <button class="btn btn-secondary" @click="exportProducts">
              <i class="icon">📤</i> 导出数据
            </button>
          </div>
          <div class="control-group search-group">
            <div class="search-box">
              <input 
                type="text" 
                v-model="searchTerm" 
                placeholder="搜索产品名称或SKU..."
                class="search-input"
              >
              <i class="search-icon">🔍</i>
            </div>
          </div>
          <div class="control-group filter-group">
            <div class="category-dropdown">
              <select v-model="selectedCategory" class="category-select">
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
          </div>
        </div>
      </div>

      <!-- 产品列表 -->
      <div class="section">
        <div class="section-header">
          <h3>产品列表</h3>
          <div class="section-actions">
            <span class="total-count">共 {{ Array.isArray(filteredProducts) ? filteredProducts.length : 0 }} 个产品</span>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
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
              <tr v-for="product in (Array.isArray(filteredProducts) ? filteredProducts : [])" :key="product.id">
                <td class="col-sku">
                  <div class="sku-code">{{ product.sku }}</div>
                </td>
                <td class="col-name">
                  <div class="product-info">
                    <div class="product-name">{{ product.name }}</div>
                    <div class="product-desc" v-if="product.description">{{ product.description }}</div>
                  </div>
                </td>
                <td class="col-category">
                  <span class="category-badge">{{ getCategoryPath(product.category_id) }}</span>
                </td>
                <td class="col-stock">
                  <span class="stock-quantity">{{ product.quantity }}</span>
                  <span class="stock-unit">{{ product.unit }}</span>
                </td>
                <td class="col-price">
                  <span class="price-value">¥{{ product.price?.toFixed(2) }}</span>
                </td>
                <td class="col-value">
                  <span class="value-amount">¥{{ parseFloat((product.quantity * product.price) || 0).toFixed(2) }}</span>
                </td>
                <td class="col-status">
                  <span :class="['status-badge', getStockStatusClass(product)]">
                    {{ getStockStatusText(product) }}
                  </span>
                </td>
                <td class="col-actions">
                  <button class="btn btn-sm btn-secondary" @click="editProduct(product)">
                    <i class="icon">✏️</i> 编辑
                  </button>
                  <button class="btn btn-sm btn-danger" @click="deleteProduct(product.id)">
                    <i class="icon">🗑️</i> 删除
                  </button>
                </td>
              </tr>
              <tr v-if="!Array.isArray(filteredProducts) || filteredProducts.length === 0">
                <td colspan="8" class="empty-state">
                  <div class="empty-content">
                    <div class="empty-icon">📦</div>
                    <h3>暂无产品数据</h3>
                    <p v-if="searchTerm || selectedCategory">没有找到匹配的产品</p>
                    <p v-else>还没有添加任何产品</p>
                    <button class="btn btn-primary" @click="showAddModal = true" v-if="!searchTerm && !selectedCategory">
                      添加第一个产品
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- 添加产品模态框 -->
  <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>添加产品</h3>
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
              <select v-model="newProduct.category_id">
                <option value="">选择分类</option>
                <optgroup v-for="category in categoryTree" :key="category.id" :label="category.name">
                  <option :value="category.id">{{ category.name }}</option>
                  <option v-for="subCategory in category.children" :key="subCategory.id" :value="subCategory.id">
                    &nbsp;&nbsp;{{ subCategory.name }}
                  </option>
                </optgroup>
              </select>
            </div>
            <div class="form-group">
              <label>单位</label>
              <input type="text" v-model="newProduct.unit" placeholder="输入单位，如：个、kg、L等">
            </div>
            <div class="form-group">
              <label>库存数量</label>
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

  <!-- 编辑产品模态框 -->
  <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>编辑产品</h3>
        <button class="modal-close" @click="showEditModal = false">×</button>
      </div>
      <div class="modal-body" v-if="editingProduct">
        <form @submit.prevent="updateProduct">
          <div class="form-grid">
            <div class="form-group">
              <label>SKU *</label>
              <input type="text" v-model="editingProduct.sku" required placeholder="输入产品SKU">
            </div>
            <div class="form-group">
              <label>产品名称 *</label>
              <input type="text" v-model="editingProduct.name" required placeholder="输入产品名称">
            </div>
            <div class="form-group">
              <label>分类</label>
              <select v-model="editingProduct.category_id">
                <option value="">选择分类</option>
                <optgroup v-for="category in categoryTree" :key="category.id" :label="category.name">
                  <option :value="category.id">{{ category.name }}</option>
                  <option v-for="subCategory in category.children" :key="subCategory.id" :value="subCategory.id">
                    &nbsp;&nbsp;{{ subCategory.name }}
                  </option>
                </optgroup>
              </select>
            </div>
            <div class="form-group">
              <label>单位</label>
              <input type="text" v-model="editingProduct.unit" placeholder="输入单位，如：个、kg、L等">
            </div>
            <div class="form-group">
              <label>库存数量</label>
              <input type="number" v-model.number="editingProduct.quantity" min="0" placeholder="0">
            </div>
            <div class="form-group">
              <label>单价 (¥)</label>
              <input type="number" v-model.number="editingProduct.price" step="0.01" min="0" placeholder="0.00">
            </div>
            <div class="form-group full-width">
              <label>产品描述</label>
              <textarea v-model="editingProduct.description" placeholder="输入产品描述（可选）" rows="3"></textarea>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="showEditModal = false">取消</button>
            <button type="submit" class="btn btn-primary">更新产品</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Products',
  data() {
    return {
      products: [], // 确保初始化为数组
      categoryTree: [],
      searchTerm: '',
      selectedCategory: '',
      showAddModal: false,
      showEditModal: false,
      newProduct: {
        sku: '',
        name: '',
        category_id: '',
        quantity: 0,
        price: 0,
        unit: '个',
        description: ''
      },
      editingProduct: null
    }
  },
  computed: {
    filteredProducts() {
      let filtered = Array.isArray(this.products) ? this.products : [];
      
      // 搜索过滤
      if (this.searchTerm) {
        const term = this.searchTerm.toLowerCase();
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(term) || 
          p.sku.toLowerCase().includes(term)
        );
      }
      
      // 分类过滤
      if (this.selectedCategory) {
        // 查找选中分类及其直接子分类的 id 列表
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
      
      return filtered;
    },
    lowStockProducts() {
      const products = Array.isArray(this.products) ? this.products : [];
      return products.filter(p => p.quantity > 0 && p.min_stock && p.quantity <= p.min_stock);
    },
    outOfStockProducts() {
      const products = Array.isArray(this.products) ? this.products : [];
      return products.filter(p => p.quantity === 0);
    }
  },
  mounted() {
    console.log('📦 Products组件已加载')
    this.loadProducts()
    this.loadCategoryTree()
  },
  methods: {
    async loadProducts() {
      try {
        const response = await fetch('/api/products');
        if (response.ok) {
          const result = await response.json();
          // 根据后端API响应格式处理数据
          if (result.success) {
            // 如果是分页响应，从data中提取产品列表
            if (Array.isArray(result.data)) {
              this.products = result.data;
            } else if (result.data && Array.isArray(result.data.products)) {
              this.products = result.data.products;
            } else {
              this.products = [];
            }
          } else {
            this.products = [];
          }
        } else {
          this.products = [];
        }
      } catch (error) {
        this.products = [];
      }
    },
    
    async loadCategoryTree() {
      try {
        const response = await fetch('/api/categories/tree');
        if (response.ok) {
          const result = await response.json();
          // 根据后端API响应格式处理数据
          if (result.success) {
            this.categoryTree = Array.isArray(result.data.categories) ? result.data.categories : [];
          } else {
            this.categoryTree = [];
          }
        } else {
          this.categoryTree = [];
        }
      } catch (error) {
        this.categoryTree = [];
      }
    },

    getCategoryPath(categoryId) {
      // 查找分类完整路径
      const findPath = (categories, targetId, path = []) => {
        for (const category of categories) {
          if (category.id === targetId) {
            return [...path, category.name];
          }
          if (category.children && category.children.length) {
            const result = findPath(category.children, targetId, [...path, category.name]);
            if (result) return result;
          }
        }
        return null;
      };

      if (!categoryId) return '未分类';
      
      const path = findPath(this.categoryTree, categoryId);
      return path ? path.join(' > ') : '未知分类';
    },

    getStockStatusClass(product) {
      if (product.quantity === 0) return 'status-out';
      if (product.min_stock && product.quantity <= product.min_stock) return 'status-low';
      if (product.quantity < 10) return 'status-warning';
      return 'status-normal';
    },

    getStockStatusText(product) {
      if (product.quantity === 0) return '缺货';
      if (product.min_stock && product.quantity <= product.min_stock) return '低库存';
      if (product.quantity < 10) return '库存较少';
      return '正常';
    },

    async addProduct() {
      try {
        const response = await fetch('/api/products', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.newProduct)
        });

        const result = await response.json();
        
        if (response.ok && result.success) {
          this.showAddModal = false;
          this.newProduct = {
            sku: '',
            name: '',
            category_id: '',
            quantity: 0,
            price: 0,
            unit: '个',
            description: ''
          };
          this.loadProducts();
          // 显示成功消息
          this.$emit('show-notification', '产品添加成功', 'success');
        } else {
          // 显示错误消息
          this.$emit('show-notification', result.message || '添加产品失败', 'error');
        }
      } catch (error) {
        this.$emit('show-notification', '添加产品时发生错误', 'error');
      }
    },

    editProduct(product) {
      this.editingProduct = { ...product };
      this.showEditModal = true;
    },

    async updateProduct() {
      if (!this.editingProduct) return;

      try {
        const response = await fetch(`/api/products/${this.editingProduct.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.editingProduct)
        });

        const result = await response.json();
        
        if (response.ok && result.success) {
          this.showEditModal = false;
          this.editingProduct = null;
          this.loadProducts();
          // 显示成功消息
          this.$emit('show-notification', '产品更新成功', 'success');
        } else {
          // 显示错误消息
          this.$emit('show-notification', result.message || '更新产品失败', 'error');
        }
      } catch (error) {
        this.$emit('show-notification', '更新产品时发生错误', 'error');
      }
    },

    async deleteProduct(id) {
      if (!confirm('确定要删除这个产品吗？')) return;

      try {
        const response = await fetch(`/api/products/${id}`, {
          method: 'DELETE'
        });

        const result = await response.json();
        
        if (response.ok && result.success) {
          this.loadProducts();
          // 显示成功消息
          this.$emit('show-notification', '产品删除成功', 'success');
        } else {
          // 显示错误消息
          this.$emit('show-notification', result.message || '删除产品失败', 'error');
        }
      } catch (error) {
        this.$emit('show-notification', '删除产品时发生错误', 'error');
      }
    },

    exportProducts() {
      // 导出功能实现
      this.$emit('show-notification', '导出功能尚未实现', 'info');
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，与之前相同 */
.products-page {
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
  font-size: 1rem;
}

/* 添加统计卡片容器样式，使其水平排列 */
.stats-overview {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 200px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 1.5rem;
}

.stat-icon.total {
  background: #e3f2fd;
  color: #1976d2;
}

.stat-icon.low {
  background: #fff3e0;
  color: #ef6c00;
}

.stat-icon.out {
  background: #ffebee;
  color: #c62828;
}

.stat-icon.category {
  background: #f3e5f5;
  color: #7b1fa2;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--dark-color);
}

.stat-label {
  font-size: 0.9rem;
  color: var(--secondary-color);
  font-weight: 500;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
  border: 1px solid var(--border-color);
}

/* 操作控件样式 */
.action-bar {
  margin-bottom: 24px;
}

.action-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
  align-items: center;
}

.control-group {
  width: auto;
}

.control-group .search-box {
  width: 100%;
}

.control-group .category-select {
  width: 100%;
}

/* 新增样式：在大屏幕上调整搜索框和分类下拉框布局 */
@media (min-width: 769px) {
  .action-controls {
    flex-direction: row;
  }
  
  .control-group.search-group {
    flex: 1;
    min-width: 300px;
  }
  
  .control-group.category-group {
    margin-left: auto;
  }
  
  .control-group .search-box {
    min-width: 300px;
  }
  
  .control-group .category-select {
    min-width: 200px;
  }
}

@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filters {
    flex-direction: column;
    max-width: none;
  }
  
  .search-box,
  .category-dropdown {
    min-width: auto;
    width: 100%;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .data-table {
    min-width: auto;
  }
  
  .data-table th,
  .data-table td {
    padding: 12px 8px;
    font-size: 0.9rem;
  }
  
  /* 在小屏幕上，统计卡片垂直排列 */
  .stats-overview {
    flex-direction: column;
  }
  
  /* 在小屏幕上，操作控件垂直排列 */
  .action-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-group {
    width: 100%;
  }
  
  .search-box {
    min-width: auto;
  }
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
  min-width: 200px;
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

/* 移除特殊的选项样式，使用默认浏览器样式 */
.category-select optgroup {
  font-weight: bold;
}

.category-select option[value=""] {
  font-style: italic;
  color: var(--secondary-color);
}

.table-container {
  overflow-x: auto;
  border-radius: 8px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
}

.data-table th {
  background: var(--light-color);
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--dark-color);
  border-bottom: 2px solid var(--border-color);
  white-space: nowrap;
}

.data-table td {
  padding: 16px 12px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.data-table tbody tr {
  transition: all 0.2s ease;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.sku-cell .sku-code {
  background: #f8f9fa;
  padding: 6px 10px;
  border-radius: 6px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.85rem;
  color: var(--dark-color);
  font-weight: 500;
}

.name-cell .product-info .product-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.name-cell .product-info .product-desc {
  font-size: 0.85rem;
  color: var(--secondary-color);
  line-height: 1.3;
}

.category-cell .category-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
}

.stock-cell {
  font-weight: 600;
}

.stock-cell .stock-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.stock-cell .stock-info .unit {
  color: var(--secondary-color);
  font-size: 0.85rem;
}

.stock-cell .stock-alerts {
  display: flex;
  gap: 4px;
}

.stock-cell .stock-alerts .alert {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: 500;
}

.stock-cell .stock-alerts .alert.low {
  background: var(--warning-color);
  color: white;
}

.stock-cell .stock-alerts .alert.zero {
  background: var(--danger-color);
  color: white;
}

.stock-out-of-stock {
  color: var(--danger-color);
}

.stock-low-stock {
  color: var(--warning-color);
}

.stock-over-stock {
  color: var(--info-color);
}

.stock-normal {
  color: var(--success-color);
}

.price-cell .price {
  font-weight: 600;
  color: var(--success-color);
}

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

.actions-cell .action-buttons {
  display: flex;
  gap: 6px;
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

.btn-edit {
  background: #e3f2fd;
  color: #1976d2;
}

.btn-delete {
  background: #ffebee;
  color: #c62828;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-content .empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-content h3 {
  margin-bottom: 12px;
  color: var(--dark-color);
}

.empty-content p {
  margin-bottom: 24px;
  color: var(--secondary-color);
  font-size: 1rem;
}

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
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
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

.tree-select-container {
  position: relative;
}

.tree-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.95rem;
  background: white;
  appearance: none;
  cursor: pointer;
}

.select-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary-color);
  pointer-events: none;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}


@media (max-width: 480px) {
  .section {
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