<template>
  <div class="container">
    <div class="bom-page">
      <!-- 操作栏 -->
      <div class="action-bar" style="margin-bottom: 24px;">
        <div class="action-left">
          <button class="btn btn-primary" @click="showAddBomModal = true">
            <i class="icon">➕</i> 添加BOM
          </button>
          <button class="btn btn-secondary" @click="showAddCompositeBomModal = true">
            <i class="icon">📦</i> 添加组合产品BOM
          </button>
          <button class="btn btn-secondary" @click="generateBomReport">
            <i class="icon">📊</i> BOM报表
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

      <!-- BOM成品列表 -->
      <div class="section">
        <div class="section-header">
          <h3>BOM成品列表</h3>
          <div class="section-actions">
            <span class="total-count">共 {{ filteredProducts.length }} 个产品</span>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-sku">SKU</th>
                <th class="col-name">产品名称</th>
                <th class="col-category">分类</th>
                <th class="col-items">物料数量</th>
                <th class="col-cost">物料成本</th>
                <th class="col-status">状态</th>
                <th class="col-updated">最后更新</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProducts" :key="product.id" class="product-row">
                <td class="col-sku">
                  <span class="sku-code">{{ product.sku }}</span>
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
                <td class="col-items">
                  <span class="items-count">{{ product.bomItems?.length || 0 }} 项</span>
                </td>
                <td class="col-cost">
                  <span class="cost-value">¥{{ product.totalCost?.toFixed(2) || '0.00' }}</span>
                </td>
                <td class="col-status">
                  <span :class="['status-badge', getBomStatus(product)]">
                    {{ getBomStatusText(product) }}
                  </span>
                </td>
                <td class="col-updated">
                  <span class="update-time">{{ formatDate(product.updated_at) }}</span>
                </td>
                <td class="col-actions">
                  <div class="action-buttons">
                    <button class="btn-icon btn-view" @click="viewBomDetails(product)" title="查看详情">
                      <i class="icon">👁️</i>
                    </button>
                    <button class="btn-icon btn-edit" @click="editBom(product)" title="编辑BOM">
                      <i class="icon">✏️</i>
                    </button>
                    <button class="btn-icon btn-copy" @click="copyBom(product)" title="复制BOM">
                      <i class="icon">📋</i>
                    </button>
                    <button class="btn-icon btn-delete" @click="deleteBom(product.id)" title="删除BOM">
                      <i class="icon">🗑️</i>
                    </button>
                  </div>
                </td>
              </tr>
              <!-- 空状态 -->
              <tr v-if="filteredProducts.length === 0">
                <td colspan="8" class="empty-state">
                  <div class="empty-content">
                    <i class="empty-icon">📋</i>
                    <h3>暂无BOM数据</h3>
                    <p>还没有为任何产品创建物料清单</p>
                    <button class="btn btn-primary" @click="showAddBomModal = true">
                      添加第一个BOM
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- BOM详情模态框 -->
      <div class="modal-overlay" v-if="showBomDetailModal" @click="showBomDetailModal = false">
        <div class="modal-content large" @click.stop>
          <div class="modal-header">
            <h3>{{ selectedProduct?.name }} - BOM详情</h3>
            <button class="modal-close" @click="showBomDetailModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="bom-detail-header">
              <div class="product-summary">
                <div class="summary-item">
                  <label>产品SKU:</label>
                  <span>{{ selectedProduct?.sku }}</span>
                </div>
                <div class="summary-item">
                  <label>产品名称:</label>
                  <span>{{ selectedProduct?.name }}</span>
                </div>
                <div class="summary-item">
                  <label>物料总数:</label>
                  <span>{{ selectedProduct?.bomItems?.length || 0 }} 项</span>
                </div>
                <div class="summary-item">
                  <label>总物料成本:</label>
                  <span class="total-cost">¥{{ selectedProduct?.totalCost?.toFixed(2) || '0.00' }}</span>
                </div>
              </div>
            </div>

            <div class="bom-items-section">
              <h4>物料清单</h4>
              <div class="table-container">
                <table class="bom-items-table">
                  <thead>
                    <tr>
                      <th>物料名称</th>
                      <th>SKU</th>
                      <th>单位用量</th>
                      <th>当前库存</th>
                      <th>单价</th>
                      <th>成本</th>
                      <th>库存状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in selectedProduct?.bomItems || []" :key="item.id">
                      <td class="material-name">{{ item.materialName }}</td>
                      <td class="material-sku">{{ item.materialSku }}</td>
                      <td class="quantity-required">{{ item.quantityRequired }} {{ item.unit }}</td>
                      <td :class="['current-stock', getStockStatusClass(item)]">
                        {{ (item.currentStock || 0).toFixed(2) }} {{ item.unit }}
                      </td>
                      <td class="material-price">¥{{ parseFloat(item.materialPrice || 0).toFixed(4) }}</td>
                      <td class="item-cost">¥{{ parseFloat(item.itemCost || 0).toFixed(4) }}</td>
                      <td class="stock-status">
                        <span :class="['status-indicator', getStockStatus(item)]">
                          {{ getStockStatusText(item) }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                  <tfoot>
                    <tr>
                      <td colspan="5"><strong>总成本</strong></td>
                      <td><strong>¥{{ parseFloat(selectedProduct?.totalCost || 0).toFixed(4) }}</strong></td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
              
              <div class="modal-actions">
                <button class="btn btn-secondary" @click="showBomDetailModal = false">关闭</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 查看BOM模态框 -->
      <div class="modal-overlay" v-if="showViewBomModal" @click="showViewBomModal = false">
        <div class="modal-content large" @click.stop>
          <div class="modal-header">
            <h3>{{ selectedProduct?.name }} - BOM详情</h3>
            <button class="modal-close" @click="showViewBomModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="bom-detail-header">
              <div class="product-summary">
                <div class="summary-item">
                  <label>产品SKU:</label>
                  <span>{{ selectedProduct?.sku }}</span>
                </div>
                <div class="summary-item">
                  <label>产品名称:</label>
                  <span>{{ selectedProduct?.name }}</span>
                </div>
                <div class="summary-item">
                  <label>总成本:</label>
                  <span>¥{{ parseFloat(selectedProduct?.totalCost || 0).toFixed(4) }}</span>
                </div>
              </div>
            </div>
            
            <div class="bom-detail-table">
              <table>
                <thead>
                  <tr>
                    <th>组件SKU</th>
                    <th>组件名称</th>
                    <th>数量</th>
                    <th>单位</th>
                    <th>单价</th>
                    <th>成本</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in bomData" :key="item.id">
                    <td>{{ item.component.sku }}</td>
                    <td>{{ item.component.name }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ item.unit }}</td>
                    <td>¥{{ parseFloat(item.component.price || 0).toFixed(4) }}</td>
                    <td>¥{{ parseFloat(item.itemCost || 0).toFixed(4) }}</td>
                    <td>
                      <span :class="['status-indicator', getStockStatus(item)]">
                        {{ getStockStatusText(item) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="5"><strong>总成本</strong></td>
                    <td><strong>¥{{ parseFloat(selectedProduct?.totalCost || 0).toFixed(4) }}</strong></td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
            
            <div class="modal-actions">
              <button class="btn btn-secondary" @click="showViewBomModal = false">关闭</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加BOM模态框 -->
      <div class="modal-overlay" v-if="showAddBomModal" @click="showAddBomModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>添加BOM</h3>
            <button class="modal-close" @click="showAddBomModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="product-sku">产品SKU</label>
              <input type="text" id="product-sku" v-model="newBom.sku" placeholder="输入产品SKU" />
            </div>
            <div class="form-group">
              <label for="product-name">产品名称</label>
              <input type="text" id="product-name" v-model="newBom.name" placeholder="输入产品名称" />
            </div>
            <div class="form-group">
              <label for="product-description">产品描述</label>
              <textarea id="product-description" v-model="newBom.description" placeholder="输入产品描述"></textarea>
            </div>
            <div class="form-group">
              <label for="product-category">产品类别</label>
              <select id="product-category" v-model="newBom.category_id">
                <option v-for="category in categories" :value="category.id">{{ category.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label for="product-bom-items">物料清单</label>
              <textarea id="product-bom-items" v-model="newBom.bomItems" placeholder="输入物料清单"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showAddBomModal = false">取消</button>
            <button class="btn btn-primary" @click="addBom">保存</button>
          </div>
        </div>
      </div>

      <!-- 编辑BOM模态框 -->
      <div class="modal-overlay" v-if="showEditBomModal" @click="showEditBomModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>编辑BOM</h3>
            <button class="modal-close" @click="showEditBomModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="product-sku">产品SKU</label>
              <input type="text" id="product-sku" v-model="selectedProduct.sku" placeholder="输入产品SKU" />
            </div>
            <div class="form-group">
              <label for="product-name">产品名称</label>
              <input type="text" id="product-name" v-model="selectedProduct.name" placeholder="输入产品名称" />
            </div>
            <div class="form-group">
              <label for="product-description">产品描述</label>
              <textarea id="product-description" v-model="selectedProduct.description" placeholder="输入产品描述"></textarea>
            </div>
            <div class="form-group">
              <label for="product-category">产品类别</label>
              <select id="product-category" v-model="selectedProduct.category_id">
                <option v-for="category in categoryTree" :value="category.id">{{ category.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label for="product-bom-items">物料清单</label>
              <textarea id="product-bom-items" v-model="selectedProduct.bomItems" placeholder="输入物料清单"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showEditBomModal = false">取消</button>
            <button class="btn btn-primary" @click="updateBom">保存</button>
          </div>
        </div>
      </div>

      <!-- 复制BOM模态框 -->
      <div class="modal-overlay" v-if="showCopyBomModal" @click="showCopyBomModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>复制BOM</h3>
            <button class="modal-close" @click="showCopyBomModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="product-sku">产品SKU</label>
              <input type="text" id="product-sku" v-model="newBom.sku" placeholder="输入产品SKU" />
            </div>
            <div class="form-group">
              <label for="product-name">产品名称</label>
              <input type="text" id="product-name" v-model="newBom.name" placeholder="输入产品名称" />
            </div>
            <div class="form-group">
              <label for="product-description">产品描述</label>
              <textarea id="product-description" v-model="newBom.description" placeholder="输入产品描述"></textarea>
            </div>
            <div class="form-group">
              <label for="product-category">产品类别</label>
              <select id="product-category" v-model="newBom.category_id">
                <option v-for="category in categories" :value="category.id">{{ category.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label for="product-bom-items">物料清单</label>
              <textarea id="product-bom-items" v-model="newBom.bomItems" placeholder="输入物料清单"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showCopyBomModal = false">取消</button>
            <button class="btn btn-primary" @click="addBom">保存</button>
          </div>
        </div>
      </div>

      <!-- 删除BOM模态框 -->
      <div class="modal-overlay" v-if="showDeleteBomModal" @click="showDeleteBomModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>删除BOM</h3>
            <button class="modal-close" @click="showDeleteBomModal = false">×</button>
          </div>
          <div class="modal-body">
            <p>确定要删除BOM吗？</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showBomDetailModal = false">关闭</button>
            <button class="btn btn-primary" @click="editBom(selectedProduct)">编辑BOM</button>
          </div>
        </div>
      </div>

      <!-- 添加BOM模态框 -->
      <div class="modal-overlay" v-if="showAddBomModal" @click="showAddBomModal = false">
        <div class="modal-content large" @click.stop>
          <div class="modal-header">
            <h3>添加BOM</h3>
            <button class="modal-close" @click="showAddBomModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addNewBom">
              <div class="form-grid">
                <div class="form-group">
                  <label for="productName">产品名称</label>
                  <input type="text" id="productName" v-model="newBom.productName" required />
                </div>
                <div class="form-group">
                  <label for="productSku">产品SKU</label>
                  <input type="text" id="productSku" v-model="newBom.productSku" required />
                </div>
                <div class="form-group">
                  <label>选择产品 *</label>
                  <select v-model="newBom.product_id" required class="product-select">
                    <option value="">请选择产品</option>
                    <option v-for="product in availableProducts" :key="product.id" :value="product.id">
                      {{ product.name }} ({{ product.sku }})
                    </option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label>产品容量/重量</label>
                  <input 
                    type="number" 
                    v-model="newBom.productQuantity" 
                    min="0"
                    step="0.01"
                    placeholder="输入产品总容量或重量"
                  >
                </div>
                
                <div class="form-group">
                  <label>单位</label>
                  <input 
                    type="text" 
                    v-model="newBom.productUnit" 
                    placeholder="如：ml、g等"
                  >
                </div>
                
                <div class="form-group full-width">
                  <label>BOM描述</label>
                  <textarea v-model="newBom.description" placeholder="输入BOM描述（可选）" rows="3"></textarea>
                </div>
              </div>
              
              <!-- 按比例计算功能 -->
              <div class="bom-form-section" v-if="newBom.product_id && newBom.productQuantity && newBom.productUnit">
                <h4>按比例计算物料</h4>
                <div class="form-grid">
                  <div class="form-group">
                    <label>选择物料 *</label>
                    <select 
                      v-model="selectedRatioProduct" 
                      @change="onRatioProductChange"
                    >
                      <option value="">请选择物料</option>
                      <option 
                        v-for="product in allProducts" 
                        :key="product.id" 
                        :value="product.id"
                      >
                        {{ product.name }} ({{ product.sku }})
                      </option>
                    </select>
                    <div class="form-hint">从现有产品中选择作为物料</div>
                  </div>
                  
                  <div class="form-group">
                    <label>物料名称</label>
                    <input 
                      type="text" 
                      v-model="ratioItem.materialName" 
                      readonly
                      placeholder="选择物料后自动填充"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label>占比 (%)</label>
                    <input 
                      type="number" 
                      v-model="ratioItem.percentage" 
                      min="0"
                      max="100"
                      step="0.01"
                      placeholder="输入占比"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label>单位</label>
                    <input 
                      type="text" 
                      v-model="ratioItem.unit" 
                      readonly
                      placeholder="物料单位"
                    >
                    <div class="form-hint">根据物料原始单位自动换算</div>
                  </div>
                  
                  <div class="form-group">
                    <button type="button" class="btn btn-secondary" @click="addRatioItem">
                      添加物料比例
                    </button>
                  </div>
                </div>
                
                <!-- 物料比例列表 -->
                <div class="bom-items-section">
                  <h4>物料比例列表</h4>
                  <div class="table-container">
                    <table class="bom-items-table">
                      <thead>
                        <tr>
                          <th>物料名称</th>
                          <th>占比 (%)</th>
                          <th>单位</th>
                          <th>计算用量</th>
                          <th>操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(item, index) in ratioItems" :key="index">
                          <td>{{ item.materialName }}</td>
                          <td>{{ item.percentage }}%</td>
                          <td>{{ item.unit }}</td>
                          <td>{{ (newBom.productQuantity * item.percentage / 100).toFixed(2) }} {{ item.unit }}</td>
                          <td>
                            <button class="btn-icon btn-delete" @click="removeRatioItem(index)" title="删除">
                              <i class="icon">🗑️</i>
                            </button>
                          </td>
                        </tr>
                        <tr v-if="ratioItems.length === 0">
                          <td colspan="5" class="empty-state">
                            <div class="empty-content">
                              <i class="empty-icon">📋</i>
                              <p>暂无物料比例</p>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colspan="2" class="text-right"><strong>总占比:</strong></td>
                          <td><strong>{{ ratioItems.reduce((sum, item) => sum + parseFloat(item.percentage || 0), 0).toFixed(2) }}%</strong></td>
                          <td><strong>{{ ratioItems.reduce((sum, item) => sum + (newBom.productQuantity * item.percentage / 100), 0).toFixed(2) }} {{ newBom.productUnit }}</strong></td>
                          <td></td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                  
                  <div class="form-actions" v-if="ratioItems.length > 0">
                    <button type="button" class="btn btn-primary" @click="convertRatioToBomItems">
                      转换为BOM物料
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- 添加物料部分 -->
              <div class="bom-form-section" v-if="newBom.product_id">
                <h4>添加物料</h4>
                <div class="form-grid">
                  <div class="form-group">
                    <label>选择物料 *</label>
                    <select 
                      v-model="selectedMaterialProduct" 
                      @change="onMaterialProductChange"
                    >
                      <option value="">请选择物料</option>
                      <option 
                        v-for="product in allProducts" 
                        :key="product.id" 
                        :value="product.id"
                      >
                        {{ product.name }} ({{ product.sku }})
                      </option>
                    </select>
                    <div class="form-hint">从现有产品中选择作为物料</div>
                  </div>
                  
                  <div class="form-group">
                    <label>物料名称</label>
                    <input 
                      type="text" 
                      v-model="newBomItem.materialName" 
                      readonly
                      placeholder="选择物料后自动填充"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label>物料SKU</label>
                    <input 
                      type="text" 
                      v-model="newBomItem.materialSku" 
                      readonly
                      placeholder="选择物料后自动填充"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label>单位 *</label>
                    <input 
                      type="text" 
                      v-model="newBomItem.unit" 
                      required
                      placeholder="输入单位，如：个、KG、g、L、ml等"
                    >
                    <div class="form-hint">单位变更时会自动换算单价，如：kg→g 价格会自动除以1000</div>
                  </div>
                  
                  <div class="form-group">
                    <label>所需数量 *</label>
                    <input 
                      type="number" 
                      v-model="newBomItem.quantityRequired" 
                      required 
                      min="0.001"
                      step="0.001"
                      placeholder="输入所需数量"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label>单价</label>
                    <input 
                      type="number" 
                      v-model="newBomItem.materialPrice" 
                      min="0"
                      step="0.01"
                      placeholder="输入单价"
                    >
                  </div>
                  
                  <div class="form-group full-width">
                    <button type="button" class="btn btn-secondary" @click="addBomItemToNewBom">
                      添加物料
                    </button>
                  </div>
                </div>
                
                <!-- 已添加的物料列表 -->
                <div class="bom-items-section">
                  <h4>已添加的物料</h4>
                  <div class="table-container">
                    <table class="bom-items-table">
                      <thead>
                        <tr>
                          <th>物料名称</th>
                          <th>物料SKU</th>
                          <th>所需数量</th>
                          <th>单位</th>
                          <th>单价</th>
                          <th>小计</th>
                          <th>操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(item, index) in newBomItems" :key="index">
                          <td>{{ item.materialName }}</td>
                          <td>{{ item.materialSku }}</td>
                          <td>{{ item.quantityRequired }}</td>
                          <td>{{ item.unit }}</td>
                          <td>¥{{ item.materialPrice }}</td>
                          <td>¥{{ (item.quantityRequired * item.materialPrice).toFixed(2) }}</td>
                          <td>
                            <button class="btn-icon btn-delete" @click="removeBomItemFromNewBom(index)" title="删除">
                              <i class="icon">🗑️</i>
                            </button>
                          </td>
                        </tr>
                        <tr v-if="newBomItems.length === 0">
                          <td colspan="7" class="empty-state">
                            <div class="empty-content">
                              <i class="empty-icon">📦</i>
                              <p>暂无BOM物料</p>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colspan="5" class="text-right"><strong>总成本:</strong></td>
                          <td colspan="2">
                            <strong class="total-cost">¥{{ calculateNewBomTotalCost().toFixed(2) }}</strong>
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="showAddBomModal = false">取消</button>
                <button type="submit" class="btn btn-primary">创建BOM</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 编辑BOM模态框 -->
      <div class="modal-overlay" v-if="showEditBomModal" @click="showEditBomModal = false">
        <div class="modal-content large" @click.stop>
          <div class="modal-header">
            <h3>编辑 {{ currentProduct?.name }} 的BOM</h3>
            <button class="modal-close" @click="showEditBomModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="bom-edit-container">
              <!-- BOM物料列表 -->
              <div class="bom-items-section">
                <h4>BOM物料清单</h4>
                <div class="table-container">
                  <table class="bom-items-table">
                    <thead>
                      <tr>
                        <th>物料名称</th>
                        <th>物料SKU</th>
                        <th>所需数量</th>
                        <th>单位</th>
                        <th>单价</th>
                        <th>小计</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="item in currentProduct?.bomItems" :key="item.id">
                        <td>{{ item.materialName || item.material_name }}</td>
                        <td>{{ item.materialSku || item.material_sku }}</td>
                        <td>{{ item.quantityRequired || item.quantity_required }}</td>
                        <td>{{ item.unit }}</td>
                        <td>¥{{ parseFloat((item.materialPrice || item.material_price || 0)).toFixed(4) }}</td>
                        <td>¥{{ parseFloat((item.itemCost || item.item_cost || 0)).toFixed(4) }}</td>
                        <td>
                          <div class="action-buttons">
                            <button class="btn-icon btn-edit" @click="editBomItem(item)" title="编辑">
                              <i class="icon">✏️</i>
                            </button>
                            <button class="btn-icon btn-delete" @click="deleteBomItem(item.id)" title="删除">
                              <i class="icon">🗑️</i>
                            </button>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="!currentProduct || !currentProduct.bomItems || currentProduct.bomItems.length === 0">
                        <td colspan="7" class="empty-state">
                          <div class="empty-content">
                            <i class="empty-icon">📦</i>
                            <p>暂无BOM物料</p>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colspan="5" class="text-right"><strong>总成本:</strong></td>
                        <td colspan="2">
                          <strong class="total-cost">¥{{ parseFloat(calculateTotalCost(currentProduct?.bomItems) || 0).toFixed(4) }}</strong>
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              <!-- 添加/编辑物料表单 -->
              <div class="bom-form-section">
                <h4>{{ editingBomItem ? '编辑物料' : '添加物料' }}</h4>
                <form @submit.prevent="editingBomItem ? updateBomItem() : addBomItem()">
                  <div class="form-grid">
                    <div class="form-group">
                      <label>选择产品 *</label>
                      <select 
                        v-model="selectedMaterialProduct" 
                        @change="onMaterialProductChange"
                        required
                      >
                        <option value="">请选择产品</option>
                        <option 
                          v-for="product in allProducts" 
                          :key="product.id" 
                          :value="product.id"
                        >
                          {{ product.name }} ({{ product.sku }})
                        </option>
                      </select>
                      <div class="form-hint">从现有产品中选择作为物料</div>
                    </div>
                    
                    <div class="form-group">
                      <label>物料名称</label>
                      <input 
                        type="text" 
                        v-model="materialNameModel" 
                        readonly
                        placeholder="选择产品后自动填充"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>物料SKU</label>
                      <input 
                        type="text" 
                        v-model="materialSkuModel" 
                        readonly
                        placeholder="选择产品后自动填充"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>单位 *</label>
                      <input 
                        type="text" 
                        v-model="unitModel" 
                        required
                        placeholder="输入单位，如：个、KG、g、L、ml等"
                      >
                      <div class="form-hint">单位变更时会自动换算单价，如：kg→g 价格会自动除以1000</div>
                    </div>
                    
                    <div class="form-group">
                      <label>所需数量 *</label>
                      <input 
                        type="number" 
                        v-model="quantityRequiredModel" 
                        required 
                        min="0.001"
                        step="0.001"
                        placeholder="输入所需数量"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>单价</label>
                      <input 
                        type="number" 
                        v-model="materialPriceModel" 
                        min="0"
                        step="0.01"
                        placeholder="输入单价"
                      >
                    </div>
                  </div>
                  
                  <div class="form-actions">
                    <button 
                      v-if="editingBomItem" 
                      type="button" 
                      class="btn btn-secondary" 
                      @click="cancelEditBomItem"
                    >
                      取消
                    </button>
                    <button type="submit" class="btn btn-primary">
                      {{ editingBomItem ? '更新物料' : '添加物料' }}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showEditBomModal = false">关闭</button>
          </div>
        </div>
      </div>

      <!-- 添加组合产品BOM模态框 -->
      <div class="modal-overlay" v-if="showAddCompositeBomModal" @click="showAddCompositeBomModal = false">
        <div class="modal-content large" @click.stop>
          <div class="modal-header">
            <h3>添加组合产品BOM</h3>
            <button class="modal-close" @click="showAddCompositeBomModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addCompositeBom">
              <div class="form-grid">
                <div class="form-group full-width">
                  <label>选择现有产品或创建新产品</label>
                  <div class="toggle-switch">
                    <label class="switch">
                      <input 
                        type="checkbox" 
                        v-model="useExistingProductForComposite"
                      >
                      <span class="slider"></span>
                    </label>
                    <span class="switch-label">
                      {{ useExistingProductForComposite ? '选择现有产品' : '创建新产品' }}
                    </span>
                  </div>
                </div>
                
                <template v-if="useExistingProductForComposite">
                  <div class="form-group full-width">
                    <label>选择现有产品 *</label>
                    <div class="searchable-select">
                      <input
                        type="text"
                        v-model="existingProductSearch"
                        placeholder="搜索产品名称或SKU..."
                        class="search-input"
                        @focus="showExistingProductDropdown = true"
                        @blur="hideExistingProductDropdownDelayed"
                        @input="showExistingProductDropdown = true"
                      >
                      <div 
                        class="dropdown-list" 
                        v-show="showExistingProductDropdown && filteredAllProducts.length > 0"
                        @mousedown.prevent
                      >
                        <div
                          v-for="product in filteredAllProducts"
                          :key="product.id"
                          class="dropdown-item"
                          :class="{ disabled: productHasBom(product.id) }"
                          @click="selectExistingProduct(product)"
                        >
                          {{ product.name }} ({{ product.sku }})
                          <span v-if="productHasBom(product.id)" class="already-has-bom">(已有BOM)</span>
                        </div>
                        <div 
                          v-if="filteredAllProducts.length === 0" 
                          class="dropdown-item no-results"
                        >
                          未找到匹配的产品
                        </div>
                      </div>
                    </div>
                    <div class="form-hint">选择一个现有产品作为组合产品，系统将为其添加BOM</div>
                  </div>
                  
                  <div class="form-group full-width" v-if="selectedExistingProduct">
                    <label>已选择产品:</label>
                    <div class="selected-product-info">
                      <strong>{{ selectedExistingProduct.name }}</strong> ({{ selectedExistingProduct.sku }})
                      <span v-if="productHasBom(selectedExistingProduct.id)" class="warning-text">注意：该产品已有BOM，继续操作将添加新的BOM项</span>
                    </div>
                  </div>
                </template>
                
                <template v-else>
                  <div class="form-group full-width">
                    <label>组合产品名称 *</label>
                    <input 
                      type="text" 
                      v-model="compositeBom.name" 
                      placeholder="输入组合产品名称"
                      required
                    >
                  </div>
                  
                  <div class="form-group full-width">
                    <label>组合产品SKU *</label>
                    <input 
                      type="text" 
                      v-model="compositeBom.sku" 
                      placeholder="输入组合产品SKU"
                      required
                    >
                  </div>
                  
                  <div class="form-group full-width">
                    <label>组合产品描述</label>
                    <textarea 
                      v-model="compositeBom.description" 
                      placeholder="输入组合产品描述（可选）" 
                      rows="3"
                    ></textarea>
                  </div>
                </template>
                
                <div class="form-group full-width">
                  <label>包含的产品</label>
                  <div class="composite-products-list">
                    <div 
                      v-for="(product, index) in compositeBom.products" 
                      :key="index"
                      class="composite-product-item"
                    >
                      <span>{{ getProductById(product.product_id)?.name }} ({{ getProductById(product.product_id)?.sku }}) × {{ product.quantity }}</span>
                      <button 
                        type="button" 
                        class="btn btn-danger btn-small"
                        @click="removeCompositeProduct(index)"
                      >
                        删除
                      </button>
                    </div>
                    
                    <div v-if="compositeBom.products.length === 0" class="no-products">
                      暂无产品
                    </div>
                  </div>
                </div>
                
                <div class="form-group full-width composite-product-form">
                  <h4>添加产品到组合</h4>
                  <div class="form-row">
                    <div class="form-group">
                      <label>选择产品</label>
                      <div class="searchable-select">
                        <input
                          type="text"
                          v-model="compositeProductSearch"
                          placeholder="搜索产品名称或SKU..."
                          class="search-input"
                          @focus="showCompositeProductDropdown = true"
                          @blur="hideCompositeProductDropdownDelayed"
                          @input="showCompositeProductDropdown = true"
                        >
                        <div 
                          class="dropdown-list" 
                          v-show="showCompositeProductDropdown && filteredFinishedProducts.length > 0"
                          @mousedown.prevent
                        >
                          <div
                            v-for="product in filteredFinishedProducts"
                            :key="product.id"
                            class="dropdown-item"
                            :class="{ disabled: isProductInComposite(product.id) }"
                            @click="selectCompositeProduct(product)"
                          >
                            {{ product.name }} ({{ product.sku }})
                            <span v-if="isProductInComposite(product.id)" class="already-added">(已添加)</span>
                          </div>
                          <div 
                            v-if="filteredFinishedProducts.length === 0" 
                            class="dropdown-item no-results"
                          >
                            未找到匹配的产品
                          </div>
                        </div>
                      </div>
                      <div class="form-hint">可以选择任何成品，包括已有BOM的成品</div>
                    </div>
                    
                    <div class="form-group">
                      <label>数量</label>
                      <input 
                        type="number" 
                        v-model="newCompositeProduct.quantity" 
                        min="1"
                        step="1"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>&nbsp;</label>
                      <button 
                        type="button" 
                        class="btn btn-secondary"
                        @click="addProductToComposite"
                        :disabled="!newCompositeProduct.product_id || !newCompositeProduct.quantity"
                      >
                        添加
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="showAddCompositeBomModal = false">
                  取消
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="(!useExistingProductForComposite && (!compositeBom.name || !compositeBom.sku)) || compositeBom.products.length === 0"
                >
                  创建组合产品BOM
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { categoryApi, productApi, bomApi } from '@/services/api';

export default {
  name: 'BOM',
  inject: ['showNotification'],
  data() {
    return {
      products: [],
      allProducts: [],
      categoryTree: [],
      searchTerm: '',
      selectedCategory: '',
      showAddBomModal: false,
      showBomDetailModal: false,
      showEditBomModal: false,
      showAddCompositeBomModal: false,
      showViewBomModal: false,
      showCopyBomModal: false,
      showDeleteBomModal: false,
      selectedProduct: null,
      currentProduct: null,
      editingBomItem: null,
      selectedMaterialProduct: '',
      selectedRatioProduct: '',
      
      // 新BOM相关数据
      newBom: {
        product_id: '',
        description: '',
        productQuantity: '',
        productUnit: '',
        productName: '',
        productSku: ''
      },
      newBomItems: [],
      newBomItem: {
        material_id: '',
        materialName: '',
        materialSku: '',
        quantityRequired: 1,
        unit: '个',
        materialPrice: 0
      },
      
      // 比例计算相关数据
      ratioItems: [],
      ratioItem: {
        materialName: '',
        percentage: '',
        unit: ''
      },
      
      // 组合产品BOM相关数据
      compositeBom: {
        name: '',
        sku: '',
        products: [], // 组合产品列表
        description: ''
      },
      newCompositeProduct: {
        product_id: '',
        quantity: 1
      },
      
      // 组合产品搜索相关数据
      compositeProductSearch: '',
      showCompositeProductDropdown: false,
      compositeProductSearchTimeout: null,
      
      // 现有产品选择相关数据
      useExistingProductForComposite: false, // 是否使用现有产品
      existingProductSearch: '',
      showExistingProductDropdown: false,
      existingProductSearchTimeout: null,
      selectedExistingProduct: null,
      
      // 现有BOM数据
      existingBoms: [],
      bomData: [],
      selectedBom: null,
      usageQuantity: 1
    }
  },
  computed: {
    filteredProducts() {
      let filtered = this.products
      
      // 显示所有已配置BOM的产品，不再限制必须是成品
      filtered = filtered.filter(p => p.bomItems && p.bomItems.length > 0)
      
      // 搜索过滤
      if (this.searchTerm) {
        const term = this.searchTerm.toLowerCase()
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(term) || 
          p.sku.toLowerCase().includes(term)
        )
      }
      
      // 分类过滤：选择一级分类时显示该一级及其二级分类下的产品；选择二级分类时只显示该二级分类内的产品
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
        filtered = filtered.filter(p => ids.includes(String(p.category_id)))
      }
      
      return filtered
    },
    
    availableProducts() {
      // 返回还没有BOM的成品分类产品
      return this.products.filter(product => {
        // 检查产品是否为成品
        const isFinished = this.isFinishedProduct(product);
        // 检查产品是否已经有BOM项
        const hasBom = product.bomItems && product.bomItems.length > 0;
        // 返回是成品但还没有BOM的产品
        return isFinished && !hasBom;
      });
    },
    
    // 新增：返回所有成品产品（无论是否有BOM）
    finishedProducts() {
      return this.products.filter(product => this.isFinishedProduct(product));
    },
    
    // 新增：返回过滤后的成品产品（用于组合产品BOM搜索）
    filteredFinishedProducts() {
      if (!this.compositeProductSearch) {
        return this.finishedProducts;
      }
      
      const term = this.compositeProductSearch.toLowerCase();
      return this.finishedProducts.filter(product => 
        product.name.toLowerCase().includes(term) || 
        product.sku.toLowerCase().includes(term)
      );
    },
    
    // 新增：返回过滤后的所有产品（用于选择现有产品作为组合产品）
    filteredAllProducts() {
      if (!this.existingProductSearch) {
        return this.allProducts;
      }
      
      const term = this.existingProductSearch.toLowerCase();
      return this.allProducts.filter(product => 
        product.name.toLowerCase().includes(term) || 
        product.sku.toLowerCase().includes(term)
      );
    },
    
    // 表单模型计算属性
    materialNameModel: {
      get() {
        return this.editingBomItem ? this.editingBomItem.materialName : this.newBomItem.materialName;
      },
      set(value) {
        if (this.editingBomItem) {
          this.editingBomItem.materialName = value;
        } else {
          this.newBomItem.materialName = value;
        }
      }
    },
    
    materialSkuModel: {
      get() {
        return this.editingBomItem ? this.editingBomItem.materialSku : this.newBomItem.materialSku;
      },
      set(value) {
        if (this.editingBomItem) {
          this.editingBomItem.materialSku = value;
        } else {
          this.newBomItem.materialSku = value;
        }
      }
    },
    
    quantityRequiredModel: {
      get() {
        return this.editingBomItem ? this.editingBomItem.quantityRequired : this.newBomItem.quantityRequired;
      },
      set(value) {
        if (this.editingBomItem) {
          this.editingBomItem.quantityRequired = value;
        } else {
          this.newBomItem.quantityRequired = value;
        }
      }
    },
    
    unitModel: {
      get() {
        return this.editingBomItem ? this.editingBomItem.unit : this.newBomItem.unit;
      },
      set(value) {
        if (this.editingBomItem) {
          this.editingBomItem.unit = value;
        } else {
          this.newBomItem.unit = value;
        }
      }
    },
    
    materialPriceModel: {
      get() {
        return this.editingBomItem ? this.editingBomItem.materialPrice : this.newBomItem.materialPrice;
      },
      set(value) {
        if (this.editingBomItem) {
          this.editingBomItem.materialPrice = value;
        } else {
          this.newBomItem.materialPrice = value;
        }
      }
    }
  },
  watch: {
    // 监听单位变更，重新计算价格
    unitModel: {
      handler(newUnit, oldUnit) {
        // 只有在选择了物料产品的情况下才进行价格换算
        if (this.selectedMaterialProduct && newUnit && oldUnit && newUnit !== oldUnit) {
          const selectedProduct = this.allProducts.find(p => p.id == this.selectedMaterialProduct);
          if (selectedProduct) {
            // 重新计算价格
            const newPrice = this.calculateUnitPrice(
              selectedProduct.price || 0,
              selectedProduct.unit || '个',
              newUnit
            );
            
            // 更新价格
            if (this.editingBomItem) {
              this.editingBomItem.materialPrice = newPrice;
            } else {
              this.newBomItem.materialPrice = newPrice;
            }
          }
        }
      }
    },
    
    // 监听使用数量变更，更新组件数量
    usageQuantity: {
      handler() {
        this.updateComponentQuantities();
      }
    },
    
    // 监听产品选择，自动填充产品名称和SKU
    'newBom.product_id': {
      handler(productId) {
        if (productId) {
          const selectedProduct = this.availableProducts.find(p => p.id == productId);
          if (selectedProduct) {
            this.newBom.productName = selectedProduct.name;
            this.newBom.productSku = selectedProduct.sku;
          }
        } else {
          // 清空产品名称和SKU
          this.newBom.productName = '';
          this.newBom.productSku = '';
        }
      }
    }
  },
  mounted() {
    console.log('📋 BOM组件已加载')
    this.loadProducts()
    this.loadCategoryTree()
    this.fetchExistingBoms();
  },
  methods: {
    async fetchExistingBoms() {
      try {
        const response = await bomApi.getBom();
        // 检查响应是否具有success属性，如果没有则是旧格式
        if (response.hasOwnProperty('success')) {
          if (response.success) {
            this.existingBoms = response.data || [];
          } else {
            console.error('获取现有BOM失败:', response.message);
          }
        } else {
          // 兼容旧格式
          this.existingBoms = response || [];
        }
      } catch (error) {
        console.error('获取现有BOM失败:', error);
      }
    },
    
    addSelectedBomComponents() {
      if (!this.selectedBom) return;
        
      const components = this.selectedBom.components || [];
      components.forEach(component => {
        const newComponent = {
          product_id: component.product_id,
          product_name: component.product_name,
          quantity: component.quantity * this.usageQuantity,
          unit: component.unit
        };
          
        // 检查是否已存在相同组件，如果存在则合并数量
        const existingComponent = this.bom.components.find(c => c.product_id === newComponent.product_id);
        if (existingComponent) {
          existingComponent.quantity += newComponent.quantity;
        } else {
          this.bom.components.push(newComponent);
        }
      });
    },
    
    updateComponentQuantities() {
      // 当使用数量改变时，更新所有组件的数量
      if (this.selectedBom && this.usageQuantity > 0) {
        this.bom.components = this.bom.components.map(component => {
            // 只更新从选中BOM添加的组件
            const isFromSelectedBom = this.selectedBom.components.some(
              c => c.product_id === component.product_id
            );
            
            if (isFromSelectedBom) {
              const originalComponent = this.selectedBom.components.find(
                c => c.product_id === component.product_id
              );
              return {
                ...component,
                quantity: originalComponent.quantity * this.usageQuantity
              };
            }
            return component;
          });
      }
    },
    
    async loadProducts() {
      try {
        // 加载BOM数据，使用expand=true参数获取展开的BOM结构
        const bomResponse = await bomApi.getBom({ expand: true });
        // 检查响应是否具有success属性，如果没有则是旧格式
        if (bomResponse.hasOwnProperty('success')) {
          if (bomResponse.success) {
            this.products = bomResponse.data || [];
          } else {
            console.error('加载BOM数据失败:', bomResponse.message);
            this.products = [];
          }
        } else {
          // 兼容旧格式
          this.products = bomResponse || [];
        }
        
        // 加载所有产品用于物料选择
        const productsResponse = await productApi.getProducts();
        // 检查响应是否具有success属性，如果没有则是旧格式
        if (productsResponse.hasOwnProperty('success')) {
          if (productsResponse.success) {
            this.allProducts = productsResponse.data || [];
          } else {
            console.error('加载产品数据失败:', productsResponse.message);
            this.allProducts = [];
          }
        } else {
          // 兼容旧格式
          this.allProducts = productsResponse || [];
        }
      } catch (error) {
        console.error('加载产品数据失败:', error);
        this.products = [];
        this.allProducts = [];
      }
    },
    
    async loadCategoryTree() {
      try {
        const response = await categoryApi.getCategoryTree();
        // 检查响应是否具有success属性，如果没有则是旧格式
        if (response.hasOwnProperty('success')) {
          if (response.success) {
            this.categoryTree = response.data.categories || [];
          } else {
            console.error('获取分类树失败:', response.message);
            this.categoryTree = [];
          }
        } else {
          // 兼容旧格式
          this.categoryTree = response.categories || [];
        }
      } catch (error) {
        console.error('获取分类树失败:', error);
        this.categoryTree = [];
      }
    },
    
    getCategoryPath(categoryId) {
      // 查找分类完整路径
      const findPath = (categories, targetId, path = []) => {
        for (const category of categories) {
          if (category.id === targetId) {
            path.push(category.name)
            return path
          }
          if (category.children && category.children.length > 0) {
            const childPath = findPath(category.children, targetId, [...path, category.name])
            if (childPath) return childPath
          }
        }
        return null
      }

      const path = findPath(this.categoryTree, categoryId)
      return path ? path.join(' > ') : '未分类'
    },
    
    getBomStatus(product) {
      if (!product.bomItems || product.bomItems.length === 0) {
        return 'not-configured'
      }
      return 'configured'
    },
    
    getBomStatusText(product) {
      const status = this.getBomStatus(product)
      const statusMap = {
        'not-configured': '未配置',
        'configured': '已配置'
      }
      return statusMap[status]
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    
    // 判断是否为成品（根据分类信息判断）
    isFinishedProduct(product) {
      // 如果没有分类ID，则不视为成品
      if (!product.category_id) {
        return false;
      }
      
      // 查找产品对应的分类
      const findCategory = (categories, targetId) => {
        for (const category of categories) {
          if (category.id === targetId) {
            return category;
          }
          if (category.children && category.children.length > 0) {
            const found = findCategory(category.children, targetId);
            if (found) return found;
          }
        }
        return null;
      };
      
      // 获取分类信息
      const category = findCategory(this.categoryTree, product.category_id);
      
      // 如果找不到分类信息，则不视为成品
      if (!category) {
        return false;
      }
      
      // 判断是否为成品分类的逻辑：
      // 1. 一级分类名称包含"成品"
      // 2. 二级分类的父分类名称包含"成品"
      if (category.level === 1) {
        return category.name.includes('成品');
      } else if (category.level === 2) {
        // 查找父分类
        const parentCategory = findCategory(this.categoryTree, category.parent_id);
        return parentCategory && parentCategory.name.includes('成品');
      }
      
      return false;
    },
    
    async viewBomDetails(product) {
      try {
        const response = await bomApi.getBom({ product_id: product.id });
        if (response) {
          const data = response;
          
          // 处理BOM项数据
          const processedItems = (data.items || []).map(item => ({
            id: item.id,
            materialName: item.material_name || item.materialName || '未知物料',
            materialSku: item.material_sku || item.materialSku || '',
            unit: item.unit || item.material_unit || '个',
            quantityRequired: parseFloat(item.quantity_required || item.quantityRequired || 0),
            materialPrice: parseFloat(item.material_price || item.materialPrice || 0),
            itemCost: parseFloat(item.item_cost || item.itemCost || 0),
            currentStock: parseFloat(item.current_stock || item.currentStock || 0)
          }));
          
          const productWithBom = {
            ...product,
            bomItems: processedItems,
            totalCost: parseFloat(data.total_cost || 0)
          };
          
          this.selectedProduct = productWithBom;
          this.showBomDetailModal = true;
        } else {
          console.error('获取BOM详情失败:', response);
          // 即使获取失败，也显示产品信息（空的BOM）
          this.selectedProduct = {
            ...product,
            bomItems: [],
            totalCost: 0
          };
          this.showBomDetailModal = true;
        }
      } catch (error) {
        console.error('获取BOM详情出错:', error);
        // 出错时也显示产品信息（空的BOM）
        this.selectedProduct = {
          ...product,
          bomItems: [],
          totalCost: 0
        };
        this.showBomDetailModal = true;
      }
    },
    
    async viewBomDetails(product) {
      try {
        // 使用expand=true参数获取展开的BOM结构
        const response = await bomApi.getBom({ product_id: product.id, expand: true });
        if (response.success) {
          const data = response.data;
          
          // 处理BOM项数据
          const processedItems = (data.items || []).map(item => ({
            id: item.id,
            materialName: item.material_name || item.materialName || '未知物料',
            materialSku: item.material_sku || item.materialSku || '',
            unit: item.unit || item.material_unit || '个',
            quantityRequired: parseFloat(item.quantity_required || item.quantityRequired || 0),
            materialPrice: parseFloat(item.material_price || item.materialPrice || 0),
            itemCost: parseFloat(item.item_cost || item.itemCost || 0),
            currentStock: parseFloat(item.current_stock || item.currentStock || 0)
          }));
          
          const productWithBom = {
            ...product,
            bomItems: processedItems,
            totalCost: parseFloat(data.total_cost || 0)
          };
          
          this.selectedProduct = productWithBom;
          this.showBomDetailModal = true;
        } else {
          console.error('获取BOM详情失败:', response.message);
          // 即使获取失败，也显示产品信息（空的BOM）
          this.selectedProduct = {
            ...product,
            bomItems: [],
            totalCost: 0
          };
          this.showBomDetailModal = true;
        }
      } catch (error) {
        console.error('获取BOM详情出错:', error);
        // 出错时也显示产品信息（空的BOM）
        this.selectedProduct = {
          ...product,
          bomItems: [],
          totalCost: 0
        };
        this.showBomDetailModal = true;
      }
    },
    
    async editBom(product) {
      try {
        // 使用expand=true参数获取展开的BOM结构
        const response = await bomApi.getBom({ product_id: product.id, expand: true });
        if (response.success) {
          const data = response.data;
          
          // 处理BOM项数据
          const processedItems = (data.items || []).map(item => ({
            id: item.id,
            materialName: item.material_name || item.materialName || '未知物料',
            materialSku: item.material_sku || item.materialSku || '',
            unit: item.unit || item.material_unit || '个',
            quantityRequired: parseFloat(item.quantity_required || item.quantityRequired || 0),
            materialPrice: parseFloat(item.material_price || item.materialPrice || 0),
            itemCost: parseFloat(item.item_cost || item.itemCost || 0),
            currentStock: parseFloat(item.current_stock || item.currentStock || 0)
          }));
          
          const productWithBom = {
            ...product,
            bomItems: processedItems,
            totalCost: parseFloat(data.total_cost || 0)
          };
          
          this.currentProduct = productWithBom;
          this.showEditBomModal = true;
        } else {
          console.error('获取BOM详情失败:', response.message);
          this.showNotification('获取BOM详情失败: ' + response.message, 'error');
        }
      } catch (error) {
        console.error('获取BOM详情出错:', error);
        this.showNotification('获取BOM详情出错: ' + (error.message || '未知错误'), 'error');
      }
    },
    
    copyBom(product) {
      // 复制BOM逻辑
      console.log('复制BOM:', product);
      // 这里可以实现复制BOM的具体逻辑
    },
    
    // 生成BOM报表
    generateBomReport() {
      // 跳转到报表页面
      this.$router.push('/reports');
    },
    
    async addNewBom() {
      if (!this.newBom.product_id) {
        this.showNotification('请选择产品', 'error');
        return;
      }
      
      try {
        // 检查是否有物料项
        if (this.newBomItems.length === 0) {
          this.showNotification('请至少添加一个物料项', 'error');
          return;
        }
        
        // 添加BOM物料项（逐个添加）
        let successCount = 0;
        let failMessages = [];
        
        for (const item of this.newBomItems) {
          try {
            console.log('正在添加BOM物料项:', item);
            
            const result = await bomApi.createBomItem({
              product_id: parseInt(this.newBom.product_id),
              material_id: parseInt(item.material_id),
              quantity_required: parseFloat(item.quantityRequired),
              unit_price: parseFloat(item.materialPrice),
              unit: item.unit
            });
            
            // 检查API调用结果
            if (result && (result.id || (result.data && result.data.id))) {
              // API调用成功，增加成功计数
              successCount++;
            } else {
              throw new Error(result.message || result.error || '未知错误');
            }
          } catch (itemError) {
            const errorMsg = `添加物料 ${item.materialName || item.material_id} 时出错: ${itemError.message || itemError}`;
            console.error(errorMsg);
            failMessages.push(errorMsg);
          }
        }
        
        // 检查结果并给出反馈
        if (successCount === this.newBomItems.length) {
          this.showNotification(`成功添加 ${successCount} 个物料项`, 'success');
          
          // 重置表单
          this.newBom = {
            product_id: '',
            description: '',
            productQuantity: '',
            productUnit: '',
            productName: '',
            productSku: ''
          };
          this.newBomItems = [];
          this.ratioItems = [];
          this.showAddBomModal = false;
          
          // 重新加载数据
          this.loadProducts();
        } else {
          // 部分或全部失败
          const failCount = this.newBomItems.length - successCount;
          this.showNotification(`成功添加 ${successCount} 个物料项，${failCount} 个失败。`, 'warning');
          
          // 显示详细错误信息（可以考虑用更友好的方式展示）
          console.error('失败详情:', failMessages.join('\n'));
        }
      } catch (error) {
        console.error('创建BOM时出错:', error);
        this.showNotification(`创建BOM失败: ${error.message || '未知错误'}`, 'error');
      }
    },
    
    // 物料产品选择变更处理
    onMaterialProductChange() {
      if (this.selectedMaterialProduct) {
        const selectedProduct = this.allProducts.find(p => p.id == this.selectedMaterialProduct)
        if (selectedProduct) {
          // 更新物料信息
          if (this.editingBomItem) {
            this.editingBomItem.materialName = selectedProduct.name
            this.editingBomItem.materialSku = selectedProduct.sku
            // 只在单位字段为空时自动填充
            if (!this.editingBomItem.unit) {
              // 使用转换后的单位
              this.editingBomItem.unit = this.convertUnitForBOM(selectedProduct.unit || '个')
            }
            // 根据单位换算自动计算单价
            this.editingBomItem.materialPrice = this.calculateUnitPrice(
              selectedProduct.price || 0, 
              selectedProduct.unit || '个', 
              this.editingBomItem.unit
            )
          } else {
            this.newBomItem.material_id = selectedProduct.id
            this.newBomItem.materialName = selectedProduct.name
            this.newBomItem.materialSku = selectedProduct.sku
            // 只在单位字段为空时自动填充
            if (!this.newBomItem.unit) {
              // 使用转换后的单位
              this.newBomItem.unit = this.convertUnitForBOM(selectedProduct.unit || '个')
            }
            // 根据单位换算自动计算单价
            this.newBomItem.materialPrice = this.calculateUnitPrice(
              selectedProduct.price || 0, 
              selectedProduct.unit || '个', 
              this.newBomItem.unit
            )
          }
        }
      } else {
        // 清空选择时重置物料信息，但保留用户已输入的单位
        if (this.editingBomItem) {
          this.editingBomItem.materialName = ''
          this.editingBomItem.materialSku = ''
          // 不清空单位字段
          this.editingBomItem.materialPrice = 0
        } else {
          this.newBomItem.material_id = ''
          this.newBomItem.materialName = ''
          this.newBomItem.materialSku = ''
          // 不清空单位字段
          this.newBomItem.materialPrice = 0
        }
      }
    },
    
    // 比例计算物料产品选择变更处理
    onRatioProductChange() {
      if (this.selectedRatioProduct) {
        const selectedProduct = this.allProducts.find(p => p.id == this.selectedRatioProduct)
        if (selectedProduct) {
          // 更新物料信息
          this.ratioItem.materialName = selectedProduct.name
          
          // 根据物料原始单位自动换算单位
          const originalUnit = selectedProduct.unit || '个'
          this.ratioItem.unit = this.convertUnitForBOM(originalUnit)
        }
      } else {
        // 清空选择时重置物料信息
        this.ratioItem.materialName = ''
        this.ratioItem.unit = ''
      }
    },
    
    // 根据BOM上下文转换物料单位
    convertUnitForBOM(originalUnit) {
      // 定义单位换算映射关系（大单位转小单位）
      const unitConversionMap = {
        'kg': 'g',
        'kgs': 'g',
        'l': 'ml',
        'L': 'ml',
        'm³': 'ml',
        'kg(s)': 'g',
        'l(s)': 'ml',
        'L(s)': 'ml',
        '吨': 'g',
        '立方米': 'ml'
      }
      
      // 如果有映射关系，则使用映射的单位，否则使用原始单位
      const convertedUnit = unitConversionMap[originalUnit.toLowerCase()] || originalUnit;
      console.log('单位换算:', originalUnit, '->', convertedUnit);
      return convertedUnit;
    },
    
    // 添加物料到新的BOM中
    addBomItemToNewBom() {
      if (!this.newBomItem.materialName || !this.newBomItem.materialSku) {
        alert('请先选择物料')
        return
      }
      
      // 添加物料到新BOM物料列表
      const item = {
        material_id: this.newBomItem.material_id,
        materialName: this.newBomItem.materialName,
        materialSku: this.newBomItem.materialSku,
        quantityRequired: this.newBomItem.quantityRequired,
        unit: this.newBomItem.unit,
        materialPrice: this.newBomItem.materialPrice,
        itemCost: this.newBomItem.quantityRequired * this.newBomItem.materialPrice
      }
      
      this.newBomItems.push(item)
      
      // 重置物料选择和表单
      this.selectedMaterialProduct = ''
      this.resetNewBomItem()
    },
    
    // 从新的BOM中移除物料
    removeBomItemFromNewBom(index) {
      this.newBomItems.splice(index, 1)
    },
    
    // 计算新BOM的总成本
    calculateNewBomTotalCost() {
      if (!this.newBomItems || this.newBomItems.length === 0) return 0
      return this.newBomItems.reduce((total, item) => {
        return total + (item.quantityRequired * item.materialPrice)
      }, 0)
    },
    
    // 添加物料比例项
    addRatioItem() {
      if (!this.ratioItem.materialName || !this.ratioItem.percentage) {
        alert('请填写物料名称和占比')
        return
      }
      
      // 添加物料比例到列表
      const item = {
        material_id: this.selectedRatioProduct,
        materialName: this.ratioItem.materialName,
        percentage: parseFloat(this.ratioItem.percentage),
        unit: this.ratioItem.unit
      }
      
      this.ratioItems.push(item)
      
      // 重置表单和选择
      this.selectedRatioProduct = ''
      this.ratioItem = {
        materialName: '',
        percentage: '',
        unit: ''
      }
    },
    
    // 移除物料比例项
    removeRatioItem(index) {
      this.ratioItems.splice(index, 1)
    },
    
    // 将比例项转换为BOM物料项
    convertRatioToBomItems() {
      if (this.ratioItems.length === 0) {
        alert('没有物料比例项可转换')
        return
      }
      
      // 计算总占比
      const totalPercentage = this.ratioItems.reduce((sum, item) => sum + parseFloat(item.percentage || 0), 0)
      
      // 检查总占比是否为100%
      if (Math.abs(totalPercentage - 100) > 0.01) {
        if (!confirm(`总占比为 ${totalPercentage.toFixed(2)}%，不等于100%。是否继续转换？`)) {
          return
        }
      }
      
      // 转换每个比例项为BOM物料项
      this.ratioItems.forEach(item => {
        const quantity = this.newBom.productQuantity * item.percentage / 100
        
        // 获取物料产品信息以获取价格
        const materialProduct = this.allProducts.find(p => p.id == item.material_id)
        let materialPrice = 0
        let itemCost = 0
        
        if (materialProduct) {
          // 计算物料单价（根据单位换算）
          materialPrice = this.calculateUnitPrice(
            materialProduct.price || 0,
            materialProduct.unit || '个',
            item.unit
          )
          
          // 计算小计金额
          itemCost = parseFloat((quantity * materialPrice).toFixed(2))
        }
        
        const bomItem = {
          material_id: item.material_id,
          materialName: item.materialName,
          materialSku: materialProduct ? materialProduct.sku : '',
          quantityRequired: parseFloat(quantity.toFixed(3)),
          unit: item.unit,
          materialPrice: materialPrice,
          itemCost: itemCost
        }
        
        this.newBomItems.push(bomItem)
      })
      
      // 清空比例项列表
      this.ratioItems = []
      this.selectedRatioProduct = ''
      
      alert('已成功转换为BOM物料项')
    },
    
    editBomItem(item) {
      this.editingBomItem = { ...item }
      this.selectedMaterialProduct = item.material_id || ''
    },
    
    async updateBomItem() {
      // 这里应该调用后端API更新BOM项
      // 暂时使用模拟数据
      const index = this.currentProduct.bomItems.findIndex(item => item.id === this.editingBomItem.id)
      if (index !== -1) {
        this.editingBomItem.itemCost = this.editingBomItem.quantityRequired * this.editingBomItem.materialPrice
        this.currentProduct.bomItems.splice(index, 1, this.editingBomItem)
        this.currentProduct.totalCost = this.calculateTotalCost(this.currentProduct.bomItems)
        this.editingBomItem = null
        this.selectedMaterialProduct = ''
      }
    },
    
    async addBomItem() {
      if (!this.newBomItem.materialName || !this.newBomItem.materialSku) {
        alert('请填写物料名称和SKU')
        return
      }
      
      // 这里应该调用后端API添加BOM项
      // 暂时使用模拟数据
      const item = {
        id: Date.now(),
        ...this.newBomItem,
        itemCost: this.newBomItem.quantityRequired * this.newBomItem.materialPrice
      }
      
      this.currentProduct.bomItems.push(item)
      this.currentProduct.totalCost = this.calculateTotalCost(this.currentProduct.bomItems)
      this.resetNewBomItem()
      this.selectedMaterialProduct = ''
    },
    
    deleteBomItem(itemId) {
      if (confirm('确定要删除这个BOM物料吗？')) {
        // 这里应该调用后端API删除BOM项
        // 暂时使用模拟数据
        const index = this.currentProduct.bomItems.findIndex(item => item.id === itemId)
        if (index !== -1) {
          this.currentProduct.bomItems.splice(index, 1)
          this.currentProduct.totalCost = this.calculateTotalCost(this.currentProduct.bomItems)
        }
      }
    },
    
    cancelEditBomItem() {
      this.editingBomItem = null;
      this.selectedMaterialProduct = '';
    },
    
    // 单位价格换算方法
    calculateUnitPrice(basePrice, baseUnit, targetUnit) {
      // 如果没有基础价格，返回0
      if (!basePrice) return 0;
      
      // 如果单位相同，直接返回基础价格
      if (baseUnit === targetUnit) return basePrice;
      
      // 定义单位换算关系
      const unitConversions = {
        // 重量单位换算 (以g为基准)
        'kg': 1000,
        'g': 1,
        'mg': 0.001,
        
        // 体积单位换算 (以ml为基准)
        'l': 1000,
        'ml': 1,
        'm³': 1000000,
        
        // 其他单位不进行换算
        '个': 1,
        '件': 1,
        '套': 1,
        '箱': 1,
        '包': 1
      };
      
      // 获取基础单位和目标单位的换算系数
      const baseFactor = unitConversions[baseUnit.toLowerCase()] || 1;
      const targetFactor = unitConversions[targetUnit.toLowerCase()] || 1;
      
      // 如果任一单位不在换算表中，返回原价
      if (!unitConversions[baseUnit.toLowerCase()] || !unitConversions[targetUnit.toLowerCase()]) {
        return basePrice;
      }
      
      // 计算换算后的价格
      return (basePrice / baseFactor) * targetFactor;
    },
    
    resetNewBomItem() {
      this.newBomItem = {
        material_id: '',
        materialName: '',
        materialSku: '',
        quantityRequired: 1,
        unit: '个',
        materialPrice: 0
      }
    },
    
    calculateTotalCost(bomItems) {
      if (!bomItems || bomItems.length === 0) return 0
      const total = bomItems.reduce((total, item) => {
        const cost = parseFloat(item.itemCost || item.item_cost || 0)
        return total + cost
      }, 0)
      return parseFloat(total) || 0
    },
    
    getStockStatus(item) {
      if (item.currentStock === 0) {
        return 'out-of-stock'
      } else if (item.currentStock < item.quantityRequired) {
        return 'low-stock'
      } else if (item.currentStock > item.quantityRequired * 10) {
        return 'over-stock'
      }
      return 'normal'
    },
    
    getStockStatusClass(item) {
      const status = this.getStockStatus(item)
      return `stock-${status}`
    },
    
    getStockStatusText(item) {
      const status = this.getStockStatus(item)
      const statusMap = {
        'out-of-stock': '缺货',
        'low-stock': '库存低',
        'over-stock': '库存过高',
        'normal': '正常'
      }
      return statusMap[status]
    },
    
    async deleteBom(productId) {
      if (!confirm('确定要删除这个产品的BOM吗？此操作不可恢复。')) {
        return;
      }
      
      try {
        // 调用后端API删除BOM
        const response = await fetch(`/api/bom/product/${productId}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          alert('BOM删除成功');
          // 重新加载数据
          this.loadProducts();
        } else {
          const errorData = await response.json();
          alert(`删除BOM失败: ${errorData.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('删除BOM时出错:', error);
        alert(`删除BOM失败: ${error.message}`);
      }
    },
    
    // 添加产品到组合
    addProductToComposite() {
      if (this.newCompositeProduct.product_id && this.newCompositeProduct.quantity) {
        this.compositeBom.products.push({
          product_id: this.newCompositeProduct.product_id,
          quantity: parseInt(this.newCompositeProduct.quantity)
        });
        
        // 重置表单
        this.newCompositeProduct.product_id = '';
        this.newCompositeProduct.quantity = 1;
        this.compositeProductSearch = '';
      }
    },
    
    // 从组合中移除产品
    removeCompositeProduct(index) {
      this.compositeBom.products.splice(index, 1);
    },
    
    // 延迟隐藏下拉列表（确保点击事件能正常触发）
    hideCompositeProductDropdownDelayed() {
      clearTimeout(this.compositeProductSearchTimeout);
      this.compositeProductSearchTimeout = setTimeout(() => {
        this.showCompositeProductDropdown = false;
      }, 200);
    },
    
    // 选择组合产品
    selectCompositeProduct(product) {
      if (!this.isProductInComposite(product.id)) {
        this.newCompositeProduct.product_id = product.id;
        this.compositeProductSearch = product.name + ' (' + product.sku + ')';
        this.showCompositeProductDropdown = false;
      }
    },
    
    // 选择现有产品作为组合产品
    selectExistingProduct(product) {
      this.selectedExistingProduct = product;
      this.existingProductSearch = product.name + ' (' + product.sku + ')';
      this.showExistingProductDropdown = false;
    },
    
    // 延迟隐藏现有产品下拉列表
    hideExistingProductDropdownDelayed() {
      clearTimeout(this.existingProductSearchTimeout);
      this.existingProductSearchTimeout = setTimeout(() => {
        this.showExistingProductDropdown = false;
      }, 200);
    },
    
    // 检查产品是否已经有BOM
    productHasBom(productId) {
      const product = this.products.find(p => p.id === productId);
      return product && product.bomItems && product.bomItems.length > 0;
    },
    
    // 检查产品是否已在组合中
    isProductInComposite(productId) {
      return this.compositeBom.products.some(p => p.product_id === productId);
    },
    
    // 根据ID获取产品信息
    getProductById(productId) {
      return this.products.find(p => p.id === parseInt(productId)) || {};
    },
    
    // 添加组合产品BOM
    async addCompositeBom() {
      try {
        let compositeProductId;
        
        if (this.useExistingProductForComposite) {
          // 使用现有产品作为组合产品
          if (!this.selectedExistingProduct) {
            alert('请选择一个现有产品');
            return;
          }
          
          compositeProductId = this.selectedExistingProduct.id;
          
          // 检查产品是否已经是组合产品
          const product = this.products.find(p => p.id === compositeProductId);
          if (product && product.is_composite) {
            if (!confirm('该产品已被标记为组合产品，是否继续添加BOM项？')) {
              return;
            }
          }
          
          // 更新产品为组合产品
          await productApi.updateProduct(compositeProductId, {
            is_composite: true
          });
        } else {
          // 创建新的组合产品
          if (!this.compositeBom.name || !this.compositeBom.sku) {
            alert('请输入组合产品名称和SKU');
            return;
          }
          
          if (this.compositeBom.products.length === 0) {
            alert('请至少添加一个产品到组合中');
            return;
          }
          
          // 创建组合产品
          const compositeProductData = {
            name: this.compositeBom.name,
            sku: this.compositeBom.sku,
            category_id: 0, // 组合产品可以放在特殊分类下
            description: this.compositeBom.description || '',
            quantity: 0, // 组合产品本身无库存
            min_stock: 0,
            price: 0, // 组合产品价格通过BOM计算
            unit: '套',
            is_composite: true // 标记为组合产品
          };
          
          const createdProduct = await productApi.createProduct(compositeProductData);
          compositeProductId = createdProduct.id;
        }
        
        if (!compositeProductId) {
          alert('无法确定组合产品');
          return;
        }
        
        // 为组合产品创建BOM项（每个包含的产品作为一个BOM项）
        for (const product of this.compositeBom.products) {
          const bomItemData = {
            product_id: compositeProductId,
            material_id: product.product_id,
            quantity_required: product.quantity,
            unit: '个' // 默认单位
          };
          
          await bomApi.createBomItem(bomItemData);
        }
        
        alert('组合产品BOM创建成功');
        
        // 重置表单
        this.resetCompositeBomForm();
        
        // 关闭模态框
        this.showAddCompositeBomModal = false;
        
        // 重新加载产品列表
        await this.loadProducts();
      } catch (error) {
        console.error('创建组合产品BOM失败:', error);
        let errorMessage = '未知错误';
        if (error.response && error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.message) {
          errorMessage = error.message;
        }
        alert('创建组合产品BOM失败: ' + errorMessage);
      }
    },
    
    // 重置组合产品BOM表单
    resetCompositeBomForm() {
      this.compositeBom = {
        name: '',
        sku: '',
        products: [],
        description: ''
      };
      this.newCompositeProduct = {
        product_id: '',
        quantity: 1
      };
      this.useExistingProductForComposite = false;
      this.existingProductSearch = '';
      this.selectedExistingProduct = null;
      this.compositeProductSearch = '';
    },
  }
}
</script>

<style scoped>
.bom-page {
  padding: 20px 0;
}

/* 操作栏样式 */
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
  gap: 16px;
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

/* 搜索下拉框样式 */
.searchable-select {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.dropdown-item {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-item.disabled {
  color: #999;
  cursor: not-allowed;
  background-color: #f5f5f5;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.already-added, .already-has-bom {
  color: #999;
  font-size: 12px;
}

.no-results {
  color: #999;
  font-style: italic;
  text-align: center;
}

/* 开关样式 */
.toggle-switch {
  display: flex;
  align-items: center;
  gap: 10px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #007bff;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.switch-label {
  font-size: 14px;
  color: #333;
}

.selected-product-info {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.warning-text {
  color: #dc3545;
  font-size: 12px;
  margin-left: 10px;
}

/* 分区样式 */
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

/* 列宽设置 */
.col-sku {
  width: 120px;
}

.col-name {
  min-width: 200px;
}

.col-category {
  width: 150px;
}

.col-items {
  width: 100px;
}

.col-cost {
  width: 120px;
}

.col-status {
  width: 100px;
}

.col-updated {
  width: 120px;
}

.col-actions {
  width: 160px;
}

/* 表格内容样式 */
.sku-code {
  background: #f8f9fa;
  padding: 6px 10px;
  border-radius: 6px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.85rem;
  color: var(--dark-color);
  font-weight: 500;
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

.category-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
}

.items-count {
  font-weight: 600;
  color: var(--primary-color);
}

.cost-value {
  font-weight: 600;
  color: var(--success-color);
}

.update-time {
  color: var(--secondary-color);
  font-size: 0.85rem;
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

.status-badge.not-configured {
  background: #f5f5f5;
  color: var(--secondary-color);
}

.status-badge.configured {
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

.btn-view {
  background: #e3f2fd;
  color: #1976d2;
}

.btn-edit {
  background: #fff3e0;
  color: #ef6c00;
}

.btn-copy {
  background: #e8f5e8;
  color: #2e7d32;
}

.btn-delete {
  background: #ffebee;
  color: #c62828;
}

/* 空状态 */
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

/* BOM详情模态框 */
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
  max-width: 900px;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
}

/* BOM详情样式 */
.bom-detail-header {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--light-color);
  border-radius: 8px;
}

.bom-edit-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.bom-form-section h4,
.bom-items-section h4 {
  margin-bottom: 16px;
  color: var(--dark-color);
}

.bom-items-table {
  width: 100%;
  border-collapse: collapse;
}

.bom-items-table th,
.bom-items-table td {
  padding: 12px 8px;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
}

.bom-items-table th {
  background: var(--light-color);
  font-weight: 600;
}

.bom-items-table tfoot {
  background: var(--light-color);
  font-weight: bold;
}

/* 库存状态样式 */
.current-stock.stock-out-of-stock {
  color: var(--danger-color);
  font-weight: 600;
}

.current-stock.stock-low-stock {
  color: var(--warning-color);
  font-weight: 600;
}

.status-indicator {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
  display: inline-block;
  min-width: 50px;
}

.status-indicator.out-of-stock {
  background: #ffebee;
  color: #c62828;
}

.status-indicator.low-stock {
  background: #fff3e0;
  color: #ef6c00;
}

.status-indicator.normal {
  background: #e8f5e8;
  color: #2e7d32;
}

/* 表单样式 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.composite-products-list {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 12px;
  min-height: 60px;
}

.composite-product-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.composite-product-item:last-child {
  border-bottom: none;
}

.composite-product-form {
  background: var(--light-color);
  padding: 16px;
  border-radius: 4px;
  margin-top: 16px;
}

.composite-product-form .form-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.composite-product-form .form-group {
  flex: 1;
  margin-bottom: 0;
}

.no-products {
  text-align: center;
  color: var(--secondary-color);
  padding: 16px;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
}

.bom-form-section h4,
.bom-items-section h4 {
  margin-bottom: 16px;
  color: var(--dark-color);
}

.bom-items-table {
  width: 100%;
  border-collapse: collapse;
}

.bom-items-table th,
.bom-items-table td {
  padding: 12px 8px;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
}

.bom-items-table th {
  background: var(--light-color);
  font-weight: 600;
}

.bom-items-table tfoot {
  background: var(--light-color);
  font-weight: bold;
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

.form-hint {
  font-size: 0.85rem;
  color: var(--secondary-color);
  margin-top: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
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

/* 单位选择样式 */
.unit-selection {
  display: flex;
  gap: 16px;
  align-items: center;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 0.95rem;
}

.radio-option input[type="radio"] {
  width: 16px;
  height: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
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
  
  .category-dropdown {
    min-width: auto;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .product-summary {
    flex-direction: column;
    gap: 16px;
  }
  
  .data-table {
    min-width: auto;
  }
  
  .modal-content.large {
    margin: 10px;
  }
}

@media (max-width: 480px) {
  .section {
    padding: 16px;
  }
  
  .modal-body {
    padding: 16px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>