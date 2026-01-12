<template>
  <div class="orders-page">
    <div class="container"> 
      <div class="section">
        <div class="section-header">
          <h3>销售订单列表</h3>
          <button class="btn btn-primary" @click="openAddOrderModal">
            <i class="icon">➕</i> 添加销售订单
          </button>
        </div>

        <div class="filters">
          <select v-model="filterStatus">
            <option value="">所有状态</option>
            <option value="pending">待处理</option>
            <option value="completed">已完成</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>订单号</th>
                <th>客户</th>
                <th>日期</th>
                <th>总金额</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.id">
                <td class="order-number">{{ order.order_number }}</td>
                <td>{{ order.customer_supplier }}</td>
                <td>{{ formatDate(order.order_date) }}</td>
                <td class="amount">¥{{ (order.total_amount || 0).toFixed(2) }}</td>
                <td>
                  <span :class="['status-badge', `status-${order.status}`]">
                    {{ getStatusText(order.status) }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-secondary" @click="viewOrder(order)">查看</button>
                  <button class="btn btn-sm btn-primary" @click="editOrder(order)">编辑</button>
                  <button class="btn btn-sm btn-info" @click="showPackingList(order)">装箱单</button>
                  <button class="btn btn-sm btn-danger" @click="deleteOrder(order)">删除</button>
                </td>
              </tr>
              <tr v-if="!filteredOrders || filteredOrders.length === 0">
                <td colspan="6" class="empty-state">暂无销售订单数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 创建销售订单模态框 -->
      <div class="modal-overlay" v-if="showAddModal" @click="closeAddOrderModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>创建销售订单</h3>
            <button class="modal-close" @click="closeAddOrderModal">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createOrder">
              <div class="form-group">
                <label>订单号</label>
                <input type="text" v-model="newOrder.order_number" placeholder="输入订单号（可手动填写）" />
              </div>

              <div class="form-group">
                <label>客户 *</label>
                <input type="text" v-model="newOrder.customer_supplier" required placeholder="输入客户名称">
                <label style="margin-top:8px">买方自定义信息</label>
                <textarea v-model="newOrder.buyer_note" rows="3" placeholder="可输入买方详细信息或备注（多行）"></textarea>
              </div>

              <div class="form-group">
                <label>订单日期 *</label>
                <input type="date" v-model="newOrder.order_date" required>
              </div>

              <div class="form-group">
                <label>卖方自定义信息</label>
                <textarea v-model="newOrder.seller_note" rows="3" placeholder="可输入卖方详细信息或备注（多行）"></textarea>
              </div>
              
              <!-- 明细表格 -->
              <div class="form-group">
                <label>订单明细</label>
                <div class="order-items">
                  <table class="order-items-table">
                    <thead>
                      <tr>
                        <th style="width:25%">产品名称</th>
                        <th style="width:15%">SKU</th>
                        <th style="width:15%">单价</th>
                        <th style="width:15%">数量</th>
                        <th style="width:20%">金额</th>
                        <th style="width:10%">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, idx) in newOrder.items" :key="idx">
                        <td>
                          <div class="item-controls">
                            <input
                              type="text"
                              v-model="item.searchTerm"
                              placeholder="搜索产品..."
                              @input="async () => await filterProducts(idx)"
                              @focus="item.showDropdown = true"
                              @blur="hideDropdown(idx)"
                              class="product-search"
                            />
                            <div 
                              v-if="item.showDropdown && item.filteredProducts.length" 
                              class="product-dropdown"
                              @mouseenter="item.showDropdown = true"
                              @mouseleave="item.showDropdown = false"
                            >
                              <div
                                v-for="product in item.filteredProducts"
                                :key="product.id"
                                @click="selectProduct(idx, product)"
                                class="product-option"
                              >
                                {{ product.name }} - {{ product.sku }}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <input type="text" v-model="item.product_sku" :disabled="!!item.product_id" />
                        </td>
                        <td>
                          <input type="number" v-model.number="item.unit_price" @input="calculateTotal" min="0" step="0.01" required>
                        </td>
                        <td>
                          <input type="number" v-model.number="item.quantity" @input="calculateTotal" min="0" step="1" required>
                        </td>
                        <td>
                          <input type="number" :value="(item.quantity * item.unit_price || 0).toFixed(2)" disabled />
                        </td>
                        <td>
                          <button type="button" class="btn btn-sm btn-danger" @click="removeItem(idx)">删除</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <button type="button" class="btn btn-secondary" @click="addItem">添加明细</button>
                </div>
              </div>

              <div class="form-group">
                <label>总金额: ¥{{ newOrder.total_amount?.toFixed(2) || '0.00' }}</label>
              </div>

              <div class="form-group">
                <label>状态</label>
                <select v-model="newOrder.status">
                  <option value="pending">待处理</option>
                  <option value="completed">已完成</option>
                  <option value="cancelled">已取消</option>
                </select>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="closeAddOrderModal">取消</button>
                <button type="submit" class="btn btn-primary">创建销售订单</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 查看/编辑订单模态框 -->
      <div class="modal-overlay" v-if="showEditModal" @click="closeEditModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ isViewMode ? '查看销售订单' : '编辑销售订单' }}</h3>
            <button class="modal-close" @click="closeEditModal">×</button>
          </div>
          <div class="modal-body" v-if="selectedOrder">
            <form @submit.prevent="updateOrder">
              <div class="form-group">
                <label>订单号</label>
                <input type="text" v-model="selectedOrder.order_number" :disabled="isViewMode" />
              </div>

              <div class="form-group">
                <label>客户 *</label>
                <input type="text" v-model="selectedOrder.customer_supplier" required :disabled="isViewMode" />
                <label style="margin-top:8px">买方自定义信息</label>
                <textarea v-model="selectedOrder.buyer_note" rows="3" :disabled="isViewMode" placeholder="可输入买方详细信息或备注（多行）"></textarea>
              </div>

              <div class="form-group">
                <label>订单日期 *</label>
                <input type="date" v-model="selectedOrder.order_date" required :disabled="isViewMode" />
              </div>

              <div class="form-group">
                <label>卖方自定义信息</label>
                <textarea v-model="selectedOrder.seller_note" rows="3" :disabled="isViewMode" placeholder="可输入卖方详细信息或备注（多行）"></textarea>
              </div>
              
              <!-- 明细表格 -->
              <div class="form-group">
                <label>订单明细</label>
                <div class="order-items">
                  <table class="order-items-table">
                    <thead>
                      <tr>
                        <th style="width:25%">产品名称</th>
                        <th style="width:15%">SKU</th>
                        <th style="width:15%">单价</th>
                        <th style="width:15%">数量</th>
                        <th style="width:20%">金额</th>
                        <th style="width:10%" v-if="!isViewMode">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, idx) in selectedOrder.items" :key="idx">
                        <td>
                          <div v-if="isViewMode">
                            <span v-if="item.product_name">{{ item.product_name }}</span>
                            <span v-else>未指定产品</span>
                          </div>
                          <div class="item-controls" v-else>
                            <input
                              type="text"
                              v-model="item.searchTerm"
                              placeholder="搜索产品..."
                              @input="async () => await filterProductsForEdit(idx)"
                              @focus="item.showDropdown = true"
                              @blur="hideDropdownForEdit(idx)"
                              class="product-search"
                            />
                            <div 
                              v-if="item.showDropdown && item.filteredProducts.length" 
                              class="product-dropdown"
                              @mouseenter="item.showDropdown = true"
                              @mouseleave="item.showDropdown = false"
                            >
                              <div
                                v-for="product in item.filteredProducts"
                                :key="product.id"
                                @click="selectProductForEdit(idx, product)"
                                class="product-option"
                              >
                                {{ product.name }} - {{ product.sku }}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div v-if="isViewMode">
                            <span v-if="item.product_sku">{{ item.product_sku }}</span>
                            <span v-else>-</span>
                          </div>
                          <input v-else type="text" v-model="item.product_sku" :disabled="!!item.product_id" />
                        </td>
                        <td>
                          <div v-if="isViewMode">
                            <span>¥{{ (item.unit_price || 0).toFixed(2) }}</span>
                          </div>
                          <input v-else type="number" v-model.number="item.unit_price" @input="calculateTotalForEdit" min="0" step="0.01" required>
                        </td>
                        <td>
                          <div v-if="isViewMode">
                            <span>{{ item.quantity || 0 }}</span>
                          </div>
                          <input v-else type="number" v-model.number="item.quantity" @input="calculateTotalForEdit" min="0" step="1" required>
                        </td>
                        <td>
                          <div v-if="isViewMode">
                            <span>¥{{ ((item.quantity || 0) * (item.unit_price || 0)).toFixed(2) }}</span>
                          </div>
                          <input v-else type="number" :value="((item.quantity || 0) * (item.unit_price || 0)).toFixed(2)" disabled />
                        </td>
                        <td v-if="!isViewMode">
                          <button type="button" class="btn btn-sm btn-danger" @click="removeItemFromEdit(idx)">删除</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <button type="button" class="btn btn-secondary" @click="addItemToEdit" v-if="!isViewMode">添加明细</button>
                </div>
              </div>

              <div class="form-group">
                <label>总金额: ¥{{ selectedOrder.total_amount?.toFixed(2) || '0.00' }}</label>
              </div>

              <div class="form-group">
                <label>状态</label>
                <select v-model="selectedOrder.status" :disabled="isViewMode">
                  <option value="pending">待处理</option>
                  <option value="completed">已完成</option>
                  <option value="cancelled">已取消</option>
                </select>
              </div>

              <div class="form-actions" v-if="!isViewMode">
                <button type="button" class="btn btn-secondary" @click="closeEditModal">取消</button>
                <button type="submit" class="btn btn-primary">更新销售订单</button>
              </div>
              <div class="form-actions" v-if="isViewMode">
                <button type="button" class="btn btn-secondary" @click="closeEditModal">关闭</button>
                <button type="button" class="btn btn-primary" @click="switchToEditMode">编辑</button>
                <button type="button" class="btn btn-info" @click="printOrder(selectedOrder)">打印</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 装箱单模态框 -->
      <div class="modal-overlay" v-if="showPackingListModal" @click="closePackingListModal">
        <div class="modal-content packing-list-modal" @click.stop>
          <div class="modal-header">
            <h3>装箱单</h3>
            <button class="modal-close" @click="closePackingListModal">×</button>
          </div>
          <div class="modal-body" v-if="selectedOrder">
            <div class="packing-list-header">
              <h4>订单号: {{ selectedOrder.order_number }}</h4>
              <p>客户: {{ selectedOrder.customer_supplier }}</p>
              <p>日期: {{ formatDate(selectedOrder.order_date) }}</p>
            </div>
            
            <table class="packing-list-table">
              <thead>
                <tr>
                  <th>产品</th>
                  <th>描述</th>
                  <th>数量</th>
                  <th>每箱数量</th>
                  <th>箱数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in selectedOrder.items" :key="idx">
                  <td>{{ item.product_name }} - {{ item.product_sku }}</td>
                  <td>{{ item.description }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>{{ item.quantity_per_box || 0 }}</td>
                  <td>{{ item.quantity_per_box ? Math.ceil(item.quantity / item.quantity_per_box) : 0 }}</td>
                </tr>
              </tbody>
            </table>
            
            <div class="packing-list-summary">
              <p>总箱数: {{ calculateTotalBoxes() }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { orderApi, productApi } from '../services/api'

export default {
  name: 'SalesOrders',
  data() {
    return {
      orders: [],
      filterStatus: '',
      showAddModal: false,
      showEditModal: false,
      showPackingListModal: false,
      isViewMode: false,
      selectedOrder: null,
      newOrder: {
        order_type: 'sale', // 固定为销售订单
        order_number: '',
        customer_supplier: '',
        order_date: new Date().toISOString().split('T')[0],
        buyer_note: '',
        seller_note: '',
        items: [{ 
          product_id: '', 
          product_name: '', 
          product_sku: '',
          description: '', 
          quantity: 0, 
          unit_price: 0,
          searchTerm: '',
          showDropdown: false,
          filteredProducts: []
        }],
        status: 'pending',
        total_amount: 0
      },
      allProducts: []
    }
  },
  computed: {
    filteredOrders() {
      let result = this.orders.filter(order => order.order_type === 'sale')
      if (this.filterStatus) {
        result = result.filter(order => order.status === this.filterStatus)
      }
      return result
    }
  },
  mounted() {
    this.loadOrders()
    this.loadProducts()
  },
  methods: {
    async loadOrders() {
      try {
        const response = await orderApi.getOrders()
        this.orders = response.orders || []
      } catch (error) {
        console.error('获取订单数据出错:', error)
        this.orders = []
      }
    },
    
    async loadProducts() {
      try {
        const response = await productApi.getNonCompositeProducts()
        // 检查是否是新的API格式（包含success字段）
        const responseData = response && response.hasOwnProperty('success') ? 
          (response.success ? response.data : []) : 
          response;
          
        this.allProducts = Array.isArray(responseData) ? responseData : []
        // 确保allProducts中不包含复合产品
        this.allProducts = this.allProducts.filter(product => product.is_composite !== 1);
        // 初始化所有明细行的过滤产品列表
        this.newOrder.items.forEach(item => {
          item.filteredProducts = [...this.allProducts]
        })
      } catch (error) {
        console.error('获取产品数据出错:', error)
        this.allProducts = []
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    
    getStatusText(status) {
      const statusMap = {
        pending: '待处理',
        completed: '已完成',
        cancelled: '已取消'
      }
      return statusMap[status] || '未知'
    },
    
    openAddOrderModal() {
      // 重置表单
      this.newOrder = {
        order_type: 'sale',
        order_number: '',
        customer_supplier: '',
        order_date: new Date().toISOString().split('T')[0],
        buyer_note: '',
        seller_note: '',
        items: [{ 
          product_id: '', 
          product_name: '', 
          product_sku: '',
          description: '', 
          quantity: 0, 
          unit_price: 0,
          searchTerm: '',
          showDropdown: false,
          filteredProducts: this.allProducts ? this.allProducts.filter(p => p.is_composite !== 1) : []
        }],
        status: 'pending',
        total_amount: 0
      }
      this.showAddModal = true
    },
    
    closeAddOrderModal() {
      this.showAddModal = false
    },
    
    openEditModal() {
      this.showEditModal = true
    },
    
    closeEditModal() {
      this.showEditModal = false
      this.isViewMode = false
      this.selectedOrder = null
    },
    
    openPackingListModal() {
      this.showPackingListModal = true
    },
    
    closePackingListModal() {
      this.showPackingListModal = false
    },
    
    addItem() {
      this.newOrder.items.push({
        product_id: '',
        product_name: '',
        product_sku: '',
        description: '',
        quantity: 0,
        unit_price: 0,
        searchTerm: '',
        showDropdown: false,
        filteredProducts: this.allProducts ? this.allProducts.filter(p => p.is_composite !== 1) : []
      })
    },
    
    removeItem(index) {
      if (this.newOrder.items.length > 1) {
        this.newOrder.items.splice(index, 1)
      } else {
        // 如果只剩一项，重置该项
        this.newOrder.items[0] = {
          product_id: '',
          product_name: '',
          product_sku: '',
          description: '',
          quantity: 0,
          unit_price: 0,
          searchTerm: '',
          showDropdown: false,
          filteredProducts: this.allProducts ? this.allProducts.filter(p => p.is_composite !== 1) : []
        }
      }
      this.calculateTotal()
    },
    
    async filterProducts(index) {
      const item = this.newOrder.items[index]
      if (item.searchTerm) {
        try {
          // 使用后端API搜索非复合产品
          const response = await productApi.getNonCompositeProducts({
            q: item.searchTerm,
            limit: 20
          })
          
          // 检查是否是新的API格式（包含success字段）
          const responseData = response && response.hasOwnProperty('success') ? 
            (response.success ? response.data : []) : 
            response;
            
          item.filteredProducts = Array.isArray(responseData) ? responseData : []
        } catch (error) {
          console.error('搜索产品出错:', error)
          // 出错时回退到本地过滤，但仍然过滤掉复合产品
          item.filteredProducts = this.allProducts.filter(product =>
            product.is_composite !== 1 && (
              product.name.toLowerCase().includes(item.searchTerm.toLowerCase()) ||
              product.sku.toLowerCase().includes(item.searchTerm.toLowerCase())
            )
          )
        }
      } else {
        item.filteredProducts = this.allProducts ? this.allProducts.filter(p => p.is_composite !== 1) : []
      }
    },
    
    hideDropdown(index) {
      // 增加延迟时间，确保用户有足够时间将鼠标移动到下拉选项上
      setTimeout(() => {
        this.newOrder.items[index].showDropdown = false
      }, 300)
    },
    
    selectProduct(index, product) {
      const item = this.newOrder.items[index]
      item.product_id = product.id
      item.product_name = product.name
      item.product_sku = product.sku
      item.description = product.description || ''
      item.searchTerm = product.name + ' - ' + product.sku
      item.showDropdown = false
      this.calculateTotal()
    },
    
    calculateTotal() {
      this.newOrder.total_amount = this.newOrder.items.reduce((total, item) => {
        return total + (item.quantity || 0) * (item.unit_price || 0)
      }, 0)
    },
    
    async createOrder() {
      try {
        // 过滤掉空的产品明细
        const validItems = this.newOrder.items.filter(item => 
          item.product_id || item.description.trim()
        )
        
        if (validItems.length === 0) {
          alert('请至少添加一个产品明细')
          return
        }
        
        // 构造订单数据
        const orderData = {
          order_type: 'sale',
          order_number: this.newOrder.order_number,
          customer_supplier: this.newOrder.customer_supplier,
          order_date: this.newOrder.order_date,
          buyer_note: this.newOrder.buyer_note,
          seller_note: this.newOrder.seller_note,
          status: this.newOrder.status,
          items: validItems.map(item => ({
            product_id: item.product_id || null,
            description: item.description,
            quantity: item.quantity || 0,
            unit_price: item.unit_price || 0
          }))
        }
        
        await orderApi.createOrder(orderData)
        this.closeAddOrderModal()
        this.loadOrders()
        alert('销售订单创建成功')
      } catch (error) {
        console.error('创建订单失败:', error)
        alert('创建订单失败: ' + (error.message || '未知错误'))
      }
    },
    
    viewOrder(order) {
      this.isViewMode = true
      this.selectedOrder = JSON.parse(JSON.stringify(order))
      // 初始化过滤产品列表并确保产品信息正确显示
      if (this.selectedOrder.items) {
        this.selectedOrder.items.forEach(item => {
          // 确保产品名称和SKU信息被正确设置
          if (item.product_name && item.product_sku) {
            item.searchTerm = item.product_name + ' - ' + item.product_sku
          } else if (item.product_name) {
            item.searchTerm = item.product_name
          } else {
            item.searchTerm = ''
          }
          item.filteredProducts = [...this.allProducts]
        })
      }
      this.openEditModal()
    },
    
    editOrder(order) {
      this.isViewMode = false
      this.selectedOrder = JSON.parse(JSON.stringify(order))
      // 初始化过滤产品列表并确保产品信息正确处理
      if (this.selectedOrder.items) {
        this.selectedOrder.items.forEach(item => {
          // 确保产品名称和SKU信息被正确设置
          if (item.product_name && item.product_sku) {
            item.searchTerm = item.product_name + ' - ' + item.product_sku
          } else if (item.product_name) {
            item.searchTerm = item.product_name
          } else {
            item.searchTerm = ''
          }
          item.filteredProducts = [...this.allProducts]
        })
      }
      this.openEditModal()
    },
    
    switchToEditMode() {
      this.isViewMode = false
    },
    
    addItemToEdit() {
      this.selectedOrder.items.push({
        product_id: '',
        product_name: '',
        product_sku: '',
        description: '',
        quantity: 0,
        unit_price: 0,
        searchTerm: '',
        showDropdown: false,
        filteredProducts: this.allProducts ? this.allProducts.filter(p => p.is_composite !== 1) : []
      })
    },
    
    removeItemFromEdit(index) {
      if (this.selectedOrder.items.length > 1) {
        this.selectedOrder.items.splice(index, 1)
      } else {
        // 如果只剩一项，重置该项
        this.selectedOrder.items[0] = {
          product_id: '',
          product_name: '',
          product_sku: '',
          description: '',
          quantity: 0,
          unit_price: 0,
          searchTerm: '',
          showDropdown: false,
          filteredProducts: this.allProducts ? this.allProducts.filter(p => p.is_composite !== 1) : []
        }
      }
      this.calculateTotalForEdit()
    },
    
    async filterProductsForEdit(index) {
      const item = this.selectedOrder.items[index]
      if (item.searchTerm) {
        try {
          // 使用后端API搜索非复合产品
          const response = await productApi.getNonCompositeProducts({
            q: item.searchTerm,
            limit: 20
          })
          
          // 检查是否是新的API格式（包含success字段）
          const responseData = response && response.hasOwnProperty('success') ? 
            (response.success ? response.data : []) : 
            response;
            
          item.filteredProducts = Array.isArray(responseData) ? responseData : []
        } catch (error) {
          console.error('搜索产品出错:', error)
          // 出错时回退到本地过滤，但仍然过滤掉复合产品
          item.filteredProducts = this.allProducts.filter(product =>
            product.is_composite !== 1 && (
              product.name.toLowerCase().includes(item.searchTerm.toLowerCase()) ||
              product.sku.toLowerCase().includes(item.searchTerm.toLowerCase())
            )
          )
        }
      } else {
        item.filteredProducts = this.allProducts ? this.allProducts.filter(p => p.is_composite !== 1) : []
      }
    },
    
    hideDropdownForEdit(index) {
      // 增加延迟时间，确保用户有足够时间将鼠标移动到下拉选项上
      setTimeout(() => {
        this.selectedOrder.items[index].showDropdown = false
      }, 300)
    },
    
    selectProductForEdit(index, product) {
      const item = this.selectedOrder.items[index]
      item.product_id = product.id
      item.product_name = product.name
      item.product_sku = product.sku
      item.description = product.description || ''
      item.searchTerm = product.name + ' - ' + product.sku
      item.showDropdown = false
      this.calculateTotalForEdit()
    },
    
    calculateTotalForEdit() {
      if (this.selectedOrder && this.selectedOrder.items) {
        this.selectedOrder.total_amount = this.selectedOrder.items.reduce((total, item) => {
          return total + (item.quantity || 0) * (item.unit_price || 0)
        }, 0)
      }
    },
    
    async updateOrder() {
      try {
        if (!this.selectedOrder || !this.selectedOrder.id) {
          alert('订单信息不完整')
          return
        }
        
        // 过滤掉空的产品明细
        const validItems = this.selectedOrder.items.filter(item => 
          item.product_id || item.description.trim()
        )
        
        if (validItems.length === 0) {
          alert('请至少添加一个产品明细')
          return
        }
        
        // 构造订单数据
        const orderData = {
          order_type: 'sale',
          order_number: this.selectedOrder.order_number,
          customer_supplier: this.selectedOrder.customer_supplier,
          order_date: this.selectedOrder.order_date,
          buyer_note: this.selectedOrder.buyer_note,
          seller_note: this.selectedOrder.seller_note,
          status: this.selectedOrder.status,
          items: validItems.map(item => ({
            id: item.id, // 包含明细项ID，用于更新
            product_id: item.product_id || null,
            description: item.description,
            quantity: item.quantity || 0,
            unit_price: item.unit_price || 0
          }))
        }
        
        await orderApi.updateOrder(this.selectedOrder.id, orderData)
        this.closeEditModal()
        this.loadOrders()
        alert('销售订单更新成功')
      } catch (error) {
        console.error('更新订单失败:', error)
        alert('更新订单失败: ' + (error.message || '未知错误'))
      }
    },
    
    async deleteOrder(order) {
      if (!confirm(`确定要删除销售订单 ${order.order_number} 吗？`)) {
        return
      }
      
      try {
        await orderApi.deleteOrder(order.id)
        this.loadOrders()
        alert('订单删除成功')
      } catch (error) {
        console.error('删除订单失败:', error)
        alert('删除订单失败: ' + (error.message || '未知错误'))
      }
    },
    
    showPackingList(order) {
      this.selectedOrder = order
      this.openPackingListModal()
    },
    
    calculateTotalBoxes() {
      if (!this.selectedOrder || !this.selectedOrder.items) return 0
      
      return this.selectedOrder.items.reduce((total, item) => {
        if (item.quantity_per_box > 0) {
          return total + Math.ceil(item.quantity / item.quantity_per_box)
        }
        return total
      }, 0)
    },
    
    printOrder(order) {
      // 创建打印窗口
      const printWindow = window.open('', '_blank', 'width=800,height=600')
      
      // 构建打印内容
      const printContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>销售订单 - ${order.order_number}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .print-header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 10px; }
            .print-header h1 { margin: 0; color: #333; }
            .order-info { margin-bottom: 20px; }
            .order-info table { width: 100%; border-collapse: collapse; }
            .order-info td { padding: 8px; border: 1px solid #ddd; }
            .order-info td:first-child { font-weight: bold; background-color: #f5f5f5; width: 20%; }
            .order-items { margin-bottom: 20px; }
            .order-items table { width: 100%; border-collapse: collapse; }
            .order-items th, .order-items td { padding: 10px; border: 1px solid #ddd; text-align: left; }
            .order-items th { background-color: #f5f5f5; font-weight: bold; }
            .order-summary { margin-top: 20px; text-align: right; }
            .order-summary p { margin: 5px 0; font-size: 16px; }
            .total-amount { font-size: 18px; font-weight: bold; color: #e74c3c; }
            .notes { margin-top: 30px; }
            .notes h3 { margin-bottom: 10px; }
            .notes-content { border: 1px solid #ddd; padding: 10px; min-height: 80px; }
            @media print {
              body { margin: 0; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          <div class="print-header">
            <h1>销售订单</h1>
          </div>
          
          <div class="order-info">
            <table>
              <tr>
                <td>订单号</td>
                <td>${order.order_number || '未填写'}</td>
                <td>客户</td>
                <td>${order.customer_supplier || '未填写'}</td>
              </tr>
              <tr>
                <td>订单日期</td>
                <td>${this.formatDate(order.order_date)}</td>
                <td>订单状态</td>
                <td>${this.getStatusText(order.status)}</td>
              </tr>
            </table>
          </div>
          
          <div class="order-items">
            <h3>订单明细</h3>
            <table>
              <thead>
                <tr>
                  <th>产品名称</th>
                  <th>SKU</th>
                  <th>单价</th>
                  <th>数量</th>
                  <th>金额</th>
                </tr>
              </thead>
              <tbody>
                ${order.items && order.items.length > 0 ? order.items.map(item => `
                  <tr>
                    <td>${item.product_name || ''}</td>
                    <td>${item.product_sku || ''}</td>
                    <td>¥${(item.unit_price || 0).toFixed(2)}</td>
                    <td>${item.quantity || 0}</td>
                    <td>¥${((item.quantity || 0) * (item.unit_price || 0)).toFixed(2)}</td>
                  </tr>
                `).join('') : '<tr><td colspan="5" style="text-align:center;">暂无订单明细</td></tr>'}
              </tbody>
            </table>
          </div>
          
          <div class="order-summary">
            <p class="total-amount">总金额: ¥${(order.total_amount || 0).toFixed(2)}</p>
          </div>
          
          <div class="notes">
            <h3>买方自定义信息</h3>
            <div class="notes-content">${order.buyer_note || '无'}</div>
          </div>
          
          <div class="no-print" style="margin-top: 20px; text-align: center;">
            <button onclick="window.print()" style="padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">打印</button>
            <button onclick="window.close()" style="padding: 10px 20px; background: #95a5a6; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 10px;">关闭</button>
          </div>
        </body>
        </html>
      `
      
      // 写入打印内容
      printWindow.document.write(printContent)
      printWindow.document.close()
      
      // 等待内容加载完成后自动触发打印
      printWindow.onload = function() {
        setTimeout(() => {
          printWindow.print()
        }, 500)
      }
    }
  }
}
</script>

<style scoped>
.orders-page {
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
}

.section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: var(--dark-color);
  font-size: 1.5rem;
}

.filters {
  margin-bottom: 20px;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: var(--dark-color);
}

.order-number {
  font-weight: 600;
  color: var(--primary-color);
}

.amount {
  font-weight: 600;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-completed {
  background-color: #d4edda;
  color: #155724;
}

.status-cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--secondary-color);
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: var(--dark-color);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: var(--dark-color);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.order-items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 10px;
}

.order-items-table th,
.order-items-table td {
  padding: 8px;
  text-align: left;
  border: 1px solid #ddd;
}

.order-items-table th {
  background-color: #f8f9fa;
}

.item-controls {
  position: relative;
}

.product-search {
  width: 100%;
}

.product-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
}

.product-option {
  padding: 8px 12px;
  cursor: pointer;
}

.product-option:hover {
  background-color: #f8f9fa;
}

.packing-list-modal {
  max-width: 600px;
}

.packing-list-header {
  margin-bottom: 20px;
}

.packing-list-header h4 {
  margin: 0 0 10px 0;
}

.packing-list-header p {
  margin: 5px 0;
}

.packing-list-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.packing-list-table th,
.packing-list-table td {
  padding: 10px;
  text-align: left;
  border: 1px solid #ddd;
}

.packing-list-table th {
  background-color: #f8f9fa;
}

.packing-list-summary {
  text-align: right;
  font-weight: bold;
}
</style>