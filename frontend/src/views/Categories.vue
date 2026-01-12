<template>
  <div class="container">
    <div class="categories-page">
	 <!-- 产品分类管理 -->
      <div class="section">
        <div class="section-header">
          <h3>分类结构</h3>
          <button class="btn btn-primary" @click="showAddCategoryModal(null)">
            <i class="icon">➕</i> 添加一级分类
          </button>
        </div>

        <!-- 分类树形结构 -->
        <div class="categories-tree">
          <div v-if="categories.length === 0" class="empty-state">
            <div class="empty-icon">📂</div>
            <h3>暂无分类数据</h3>
            <p>还没有创建任何产品分类</p>
            <button class="btn btn-primary" @click="showAddCategoryModal(null)">
              添加第一个分类
            </button>
          </div>

          <div v-else class="tree-container">
            <div class="category-node" 
                 v-for="category in categories" 
                 :key="category.id"
                 :style="{ marginLeft: getCategoryIndent(category) }">
              
              <!-- 分类项 -->
              <div class="category-item" :class="`level-${category.level}`">
                <div class="category-content">
                  <div class="category-info">
                    <div class="category-icon">
                      <i v-if="category.level === 1" class="icon">📁</i>
                      <i v-else class="icon">📄</i>
                    </div>
                    <div class="category-details">
                      <div class="category-name">{{ category.name }}</div>
                      <div class="category-meta">
                        <span class="category-id">ID: {{ category.id }}</span>
                        <span class="category-level">层级: {{ category.level }}</span>
                        <span v-if="category.parent_id" class="category-parent">
                          父级: {{ getParentName(category.parent_id) }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="category-actions">
                    <button class="btn btn-sm btn-success" @click="showAddCategoryModal(category)">
                      <i class="icon">➕</i> 添加子分类
                    </button>
                    <button class="btn btn-sm btn-secondary" @click="editCategory(category)">
                      <i class="icon">✏️</i> 编辑
                    </button>
                    <button class="btn btn-sm btn-danger" @click="deleteCategory(category.id)">
                      <i class="icon">🗑️</i> 删除
                    </button>
                  </div>
                </div>
              </div>

              <!-- 子分类 -->
              <div v-if="category.children && category.children.length > 0" class="children-container">
                <div class="category-node" 
                     v-for="child in category.children" 
                     :key="child.id"
                     :style="{ marginLeft: getCategoryIndent(child) }">
                  
                  <div class="category-item" :class="`level-${child.level}`">
                    <div class="category-content">
                      <div class="category-info">
                        <div class="category-icon">
                          <i class="icon">📄</i>
                        </div>
                        <div class="category-details">
                          <div class="category-name">{{ child.name }}</div>
                          <div class="category-meta">
                            <span class="category-id">ID: {{ child.id }}</span>
                            <span class="category-level">层级: {{ child.level }}</span>
                            <span class="category-parent">父级: {{ category.name }}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div class="category-actions">
                        <button class="btn btn-sm btn-success" @click="showAddCategoryModal(child)">
                          <i class="icon">➕</i> 添加子分类
                        </button>
                        <button class="btn btn-sm btn-secondary" @click="editCategory(child)">
                          <i class="icon">✏️</i> 编辑
                        </button>
                        <button class="btn btn-sm btn-danger" @click="deleteCategory(child.id)">
                          <i class="icon">🗑️</i> 删除
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- 三级分类（如果有的话） -->
                  <div v-if="child.children && child.children.length > 0" class="children-container">
                    <div class="category-node" 
                         v-for="grandchild in child.children" 
                         :key="grandchild.id"
                         :style="{ marginLeft: getCategoryIndent(grandchild) }">
                      
                      <div class="category-item" :class="`level-${grandchild.level}`">
                        <div class="category-content">
                          <div class="category-info">
                            <div class="category-icon">
                              <i class="icon">📄</i>
                            </div>
                            <div class="category-details">
                              <div class="category-name">{{ grandchild.name }}</div>
                              <div class="category-meta">
                                <span class="category-id">ID: {{ grandchild.id }}</span>
                                <span class="category-level">层级: {{ grandchild.level }}</span>
                                <span class="category-parent">父级: {{ child.name }}</span>
                              </div>
                            </div>
                          </div>
                          
                          <div class="category-actions">
                            <button class="btn btn-sm btn-secondary" @click="editCategory(grandchild)">
                              <i class="icon">✏️</i> 编辑
                            </button>
                            <button class="btn btn-sm btn-danger" @click="deleteCategory(grandchild.id)">
                              <i class="icon">🗑️</i> 删除
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 添加/编辑分类模态框 -->
  <div v-if="showModal" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ editingCategory ? '编辑分类' : (parentCategory ? '添加子分类' : '添加一级分类') }}</h3>
        <button class="modal-close" @click="closeModal">×</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="saveCategory">
          <div class="form-group">
            <label>分类名称 *</label>
            <input 
              type="text" 
              v-model="categoryForm.name" 
              required 
              placeholder="请输入分类名称"
              maxlength="50"
            >
          </div>
          
          <div v-if="parentCategory" class="parent-category-info">
            <div class="parent-category-badge">
              <span>父级分类:</span>
              <strong>{{ parentCategory.name }}</strong>
            </div>
            <div class="level-info">
              分类层级: {{ parentCategory.level + 1 }}
            </div>
          </div>
          
          <div v-if="editingCategory" class="current-info">
            <div class="info-item">
              <span class="label">分类ID:</span>
              <span class="value">{{ editingCategory.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">当前层级:</span>
              <span class="value">{{ editingCategory.level }}</span>
            </div>
            <div v-if="editingCategory.parent_id" class="info-item">
              <span class="label">父级ID:</span>
              <span class="value">{{ editingCategory.parent_id }}</span>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Categories',
  data() {
    return {
      categories: [],
      showModal: false,
      parentCategory: null,
      editingCategory: null,
      categoryForm: {
        name: ''
      }
    };
  },
  mounted() {
    console.log('📂 Categories组件已加载')
    this.loadCategories();
  },
  methods: {
    async loadCategories() {
      try {
        const response = await fetch('/api/categories/tree');
        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            this.categories = result.data.categories || [];
          } else {
            console.error('获取分类数据失败:', result.message);
            this.categories = [];
          }
        } else {
          console.error('获取分类数据失败:', response.status);
          this.categories = [];
        }
      } catch (error) {
        console.error('获取分类数据出错:', error);
        this.categories = [];
      }
      
      console.log('分类数据加载完成:', this.categories);
    },
    
    getCategoryIndent(category) {
      // 根据层级计算缩进
      const baseIndent = 20; // 基础缩进
      const levelIndent = (category.level - 1) * 30; // 每级增加30px
      return `${baseIndent + levelIndent}px`;
    },
    
    getParentName(parentId) {
      // 查找父级分类名称
      const findParent = (categories, targetId) => {
        for (const category of categories) {
          if (category.id === targetId) {
            return category.name;
          }
          if (category.children && category.children.length > 0) {
            const parentName = findParent(category.children, targetId);
            if (parentName) return parentName;
          }
        }
        return null;
      };
      
      return findParent(this.categories, parentId) || '未知';
    },
    
    showAddCategoryModal(parent) {
      this.parentCategory = parent;
      this.editingCategory = null;
      this.categoryForm = {
        name: ''
      };
      this.showModal = true;
    },
    
    editCategory(category) {
      this.editingCategory = category;
      this.parentCategory = null;
      this.categoryForm = {
        name: category.name
      };
      this.showModal = true;
    },
    
    closeModal() {
      this.showModal = false;
      this.parentCategory = null;
      this.editingCategory = null;
      this.categoryForm = {
        name: ''
      };
    },
    
    async saveCategory() {
      try {
        const payload = {
          name: this.categoryForm.name,
          parent_id: this.parentCategory ? this.parentCategory.id : null
        };
        
        console.log('Sending category data:', payload); // 调试日志
        
        const response = await fetch('/api/categories', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          this.closeModal();
          await this.loadCategories();
          // 显示成功消息
          if (this.$emit) {
            this.$emit('show-notification', '分类添加成功', 'success');
          } else {
            alert('分类添加成功');
          }
        } else {
          const errorMessage = result.message || `HTTP错误: ${response.status}`;
          console.error('添加分类失败:', response.status, errorMessage);
          if (this.$emit) {
            this.$emit('show-notification', `添加分类失败: ${errorMessage}`, 'error');
          } else {
            alert(`添加分类失败: ${errorMessage}`);
          }
        }
      } catch (error) {
        console.error('添加分类出错:', error);
        const errorMessage = error.message || error;
        if (this.$emit) {
          this.$emit('show-notification', `添加分类时发生网络错误: ${errorMessage}`, 'error');
        } else {
          alert(`添加分类时发生网络错误: ${errorMessage}`);
        }
      }
    },
    
    async deleteCategory(categoryId) {
      // 首先检查有哪些产品使用了该分类
      try {
        const response = await fetch(`/api/categories/${categoryId}/usage`);
        if (response.ok) {
          const result = await response.json();
          if (result.success && result.data) {
            if (result.data.product_count > 0) {
              let productInfo = "以下产品使用了该分类:\n";
              result.data.products.forEach(p => {
                productInfo += `- ${p.sku}: ${p.name}\n`;
              });
              productInfo += "\n请先将这些产品移至其他分类或删除后再尝试删除该分类。";
              
              if (this.$emit) {
                this.$emit('show-notification', productInfo, 'info');
              } else {
                alert(productInfo);
              }
              return;
            }
          } else {
            console.error('检查分类使用情况失败:', result.message);
          }
        } else {
          console.error('检查分类使用情况失败:', response.status);
        }
      } catch (error) {
        console.error('检查分类使用情况出错:', error);
      }
      
      if (!confirm('确定要删除这个分类吗？删除分类将同时删除其下的所有子分类。')) return;
      
      try {
        const response = await fetch(`/api/categories/${categoryId}`, {
          method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          // 重新加载分类数据
          await this.loadCategories();
          console.log('分类删除成功:', categoryId);
          if (this.$emit) {
            this.$emit('show-notification', '分类删除成功', 'success');
          } else {
            alert('分类删除成功');
          }
        } else {
          const errorMessage = result.message || '未知错误';
          console.error('删除分类失败:', response.status, errorMessage);
          if (this.$emit) {
            this.$emit('show-notification', `删除分类失败: ${errorMessage}`, 'error');
          } else {
            alert(`删除分类失败: ${errorMessage}`);
          }
        }
      } catch (error) {
        console.error('删除分类失败:', error);
        const errorMessage = error.message || error;
        if (this.$emit) {
          this.$emit('show-notification', `删除分类失败: ${errorMessage}`, 'error');
        } else {
          alert(`删除分类失败: ${errorMessage}`);
        }
      }
    }
  }
};
</script>

<style scoped>
.categories-page {
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

.section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
  border: 1px solid var(--border-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.section-header h3 {
  margin: 0;
  color: var(--dark-color);
  font-size: 1.3rem;
  font-weight: 600;
}

/* 树形结构样式 */
.categories-tree {
  min-height: 200px;
}

.tree-container {
  border-radius: 8px;
  overflow: hidden;
}

.category-node {
  transition: all 0.3s ease;
}

.category-item {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.category-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.1);
}

.category-item.level-1 {
  background: #f8f9fa;
  border-left: 4px solid var(--primary-color);
}

.category-item.level-2 {
  background: white;
  border-left: 4px solid var(--success-color);
}

.category-item.level-3 {
  background: #fafafa;
  border-left: 4px solid var(--warning-color);
}

.category-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.category-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--light-color);
}

.category-icon .icon {
  font-size: 1.2rem;
}

.category-details {
  flex: 1;
}

.category-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--dark-color);
  margin-bottom: 4px;
}

.category-meta {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: var(--secondary-color);
}

.category-id,
.category-level,
.category-parent {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.children-container {
  border-left: 2px dashed var(--border-color);
  margin-left: 20px;
  padding-left: 20px;
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

/* 模态框样式 */
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
  max-width: 500px;
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

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--dark-color);
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.parent-category-info {
  padding: 12px;
  background: var(--light-color);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.parent-category-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: var(--primary-color);
}

.level-info {
  padding: 8px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-weight: 500;
}

.current-info {
  padding: 12px;
  background: var(--light-color);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  color: var(--secondary-color);
}

.info-item .value {
  font-weight: 500;
  color: var(--dark-color);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .category-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .category-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .category-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .modal-content {
    margin: 10px;
  }
  
  .modal-body {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .section {
    padding: 16px;
  }
  
  .category-content {
    padding: 12px 16px;
  }
  
  .category-actions {
    flex-wrap: wrap;
  }
  
  .btn-sm {
    font-size: 0.8rem;
    padding: 6px 10px;
  }
}
</style>