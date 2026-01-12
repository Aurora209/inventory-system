<template>
  <div class="orders-page">
    <div class="container">
      <div class="section">
        <div class="section-header">
          <h3>采购订单列表</h3>
          <button class="btn btn-primary" @click="openAddOrderModal">
            <i class="icon">➕</i> 添加采购订单
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
                <th>供应商</th>
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
                <td class="amount">¥{{ parseFloat(order.total_amount || 0).toFixed(2) }}</td>
                <td>
                  <span :class="['status-badge', `status-${order.status}`]">
                    {{ getStatusText(order.status) }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-secondary" @click="viewOrder(order)">查看</button>
                  <button class="btn btn-sm btn-primary" @click="editOrder(order)">编辑</button>
                  <button class="btn btn-sm btn-info" @click="printOrder(order)">打印</button>
                  <button class="btn btn-sm btn-danger" @click="deleteOrder(order)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 添加订单模态框 -->
      <div class="modal" v-if="showAddModal" @click.self="closeAddOrderModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h4>添加采购订单</h4>
            <button class="close-btn" @click="closeAddOrderModal">&times;</button>
          </div>
          
          <div class="modal-body">
            <div class="form-group">
              <label>订单号 *</label>
              <input type="text" v-model="newOrder.order_number" placeholder="自动生成或手动输入" />
            </div>
            
            <div class="form-group">
              <label>供应商 *</label>
              <input type="text" v-model="newOrder.customer_supplier" required placeholder="输入供应商名称" />
            </div>
            
            <div class="form-group">
              <label>订单日期 *</label>
              <input type="date" v-model="newOrder.order_date" required />
            </div>
            
            <div class="form-group">
              <label>卖家自定义信息</label>
              <textarea v-model="newOrder.seller_note" placeholder="输入备注信息"></textarea>
            </div>
            
            <!-- 订单明细表格 -->
            <div class="section">
              <div class="section-header">
                <h5>订单明细</h5>
              </div>
              
              <div class="table-container">
                <table class="order-items-table">
                  <thead>
                    <tr>
                      <th style="width:30%">产品名称</th>
                      <th style="width:15%">SKU</th>
                      <th style="width:10%">单价</th>
                      <th style="width:8%">单位</th>
                      <th style="width:10%">数量</th>
                      <th style="width:15%">金额</th>
                      <th style="width:10%">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, idx) in newOrder.items" :key="idx">
                      <td>
                        <div class="item-controls">
                          <input
                            type="text"
                            v-model="item.product_name"
                            placeholder="搜索产品..."
                            @input="() => handleProductSearch(idx)"
                            @focus="item.showDropdown = true"
                            @blur="() => hideDropdown(idx)"
                            class="product-search"
                            readonly
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
                        <input type="text" v-model="item.product_sku" :disabled="!!item.product_id" class="order-input" readonly />
                      </td>
                      <td>
                        <input type="number" v-model.number="item.unit_price" @input="calculateTotal" min="0" step="0.01" required class="order-input">
                      </td>
                      <td>
                        <input type="text" v-model="item.unit" :disabled="!!item.product_id" class="order-input" />
                      </td>
                      <td>
                        <input type="number" v-model.number="item.quantity" @input="calculateTotal" min="0" step="1" required class="order-input">
                      </td>
                      <td class="amount-cell">
                        ¥{{ ((item.quantity || 0) * (item.unit_price || 0)).toFixed(2) }}
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
            
            <!-- 快递运费移至订单明细下方 -->
            <div class="form-group">
              <label>快递运费(¥)</label>
              <input type="number" v-model.number="newOrder.shipping_cost" min="0" step="0.01" placeholder="输入快递运费" @input="calculateTotal">
            </div>
            
            <div class="form-group">
              <label>订单总金额</label>
              <div class="form-control-static total-amount">
                ¥{{ parseFloat(newOrder.total_amount || 0).toFixed(2) }}
              </div>
            </div>
            
            <div class="form-group">
              <label>状态</label>
              <select v-model="newOrder.status">
                <option value="pending">待处理</option>
                <option value="completed">已完成</option>
                <option value="cancelled">已取消</option>
              </select>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeAddOrderModal">取消</button>
            <button class="btn btn-primary" @click="createOrder">创建订单</button>
          </div>
        </div>
      </div>

      <!-- 编辑/查看订单模态框 -->
      <div class="modal" v-if="showEditModal" @click.self="closeEditModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h4>{{ isViewMode ? '查看' : '编辑' }}采购订单 - {{ selectedOrder.order_number }}</h4>
            <button class="close-btn" @click="closeEditModal">&times;</button>
          </div>
          
          <div class="modal-body">
            <div class="form-group">
              <label>订单号</label>
              <input type="text" v-model="selectedOrder.order_number" :disabled="isViewMode" />
            </div>
            
            <div class="form-group">
              <label>供应商 *</label>
              <input type="text" v-model="selectedOrder.customer_supplier" :disabled="isViewMode" required />
            </div>
            
            <div class="form-group">
              <label>订单日期 *</label>
              <input type="date" v-model="selectedOrder.order_date" :disabled="isViewMode" required />
            </div>
            
            <div class="form-group">
              <label>卖家自定义信息</label>
              <textarea v-model="selectedOrder.seller_note" :disabled="isViewMode" placeholder="输入备注信息"></textarea>
            </div>
            
            <div class="section">
              <div class="section-header">
                <h5>订单明细</h5>
              </div>
              
              <div class="table-container">
                <table class="order-items-table">
                  <thead>
                    <tr>
                      <th style="width:30%">产品名称</th>
                      <th style="width:15%">SKU</th>
                      <th style="width:10%">单价</th>
                      <th style="width:8%">单位</th>
                      <th style="width:10%">数量</th>
                      <th style="width:15%">金额</th>
                      <th style="width:10%" v-if="!isViewMode">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, idx) in selectedOrder.items" :key="idx">
                      <td>
                        <div v-if="isViewMode">
                          <div>
                            <div>{{ item.product_name || '未指定产品' }}</div>
                          </div>
                        </div>
                        <div class="item-controls" v-else>
                          <input
                            type="text"
                            v-model="item.product_name"
                            placeholder="搜索产品..."
                            @input="() => handleProductSearchForEdit(idx)"
                            @focus="item.showDropdown = true"
                            @blur="() => hideDropdownForEdit(idx)"
                            class="product-search"
                            readonly
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
                          <span>{{ item.product_sku || '' }}</span>
                        </div>
                        <input v-else type="text" v-model="item.product_sku" :disabled="!!item.product_id" class="order-input" readonly />
                      </td>
                      <td>
                        <div v-if="isViewMode">
                          <span>¥{{ (item.unit_price || 0).toFixed(2) }}</span>
                        </div>
                        <input v-else type="number" v-model.number="item.unit_price" @input="calculateTotalForEdit" min="0" step="0.01" required class="order-input">
                      </td>
                      <td>
                        <div v-if="isViewMode">
                          <span>{{ item.unit || '' }}</span>
                        </div>
                        <input v-else type="text" v-model="item.unit" :disabled="!!item.product_id" class="order-input" />
                      </td>
                      <td>
                        <div v-if="isViewMode">
                          <span>{{ item.quantity || 0 }}</span>
                        </div>
                        <input v-else type="number" v-model.number="item.quantity" @input="calculateTotalForEdit" min="0" step="1" required class="order-input">
                      </td>
                      <td class="amount-cell">
                        <div v-if="isViewMode">
                          <span>¥{{ parseFloat((item.quantity || 0) * (item.unit_price || 0)).toFixed(2) }}</span>
                        </div>
                        <input v-else type="number" :value="((item.quantity || 0) * (item.unit_price || 0)).toFixed(2)" disabled class="order-input" />
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
              <label>快递运费(¥)</label>
              <input type="number" v-model.number="selectedOrder.shipping_cost" min="0" step="0.01" :disabled="isViewMode" placeholder="输入快递运费" @input="calculateTotalForEdit">
            </div>
            
            <div class="form-group">
              <label>订单总金额</label>
              <div class="form-control-static total-amount">
                ¥{{ parseFloat(selectedOrder.total_amount || 0).toFixed(2) }}
              </div>
            </div>
            
            <div class="form-group">
              <label>状态</label>
              <select v-model="selectedOrder.status" :disabled="isViewMode">
                <option value="pending">待处理</option>
                <option value="completed">已完成</option>
                <option value="cancelled">已取消</option>
              </select>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeEditModal">关闭</button>
            <button class="btn btn-primary" @click="switchToEditMode" v-if="isViewMode">编辑</button>
            <button class="btn btn-primary" @click="updateOrder" v-else>保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { orderApi, productApi } from '../services/api'

export default {
  name: 'PurchaseOrders',
  data() {
    return {
      orders: [],
      allProducts: [],
      filterStatus: '',
      showAddModal: false,
      showEditModal: false,
      isViewMode: false,
      newOrder: {
        order_type: 'purchase',
        order_number: '',
        customer_supplier: '',
        order_date: new Date().toISOString().split('T')[0],
        shipping_cost: 0,
        seller_note: '',
        items: [{ 
          product_id: '',
          product_name: '', 
          product_sku: '',
          quantity: 0,
          unit_price: 0,
          unit: '个',
          searchTerm: '',
          showDropdown: false,
          filteredProducts: []
        }],
        status: 'pending',
        total_amount: 0
      },
      selectedOrder: {
        id: null,
        order_type: 'purchase',
        order_number: '',
        customer_supplier: '',
        order_date: '',
        shipping_cost: 0,
        seller_note: '',
        items: [],
        status: 'pending',
        total_amount: 0
      }
    }
  },
  computed: {
    filteredOrders() {
      if (!this.filterStatus) {
        return this.orders
      }
      return this.orders.filter(order => order.status === this.filterStatus)
    }
  },
  async mounted() {
    await this.loadOrders()
    await this.loadProducts()
  },
  methods: {
    async loadOrders() {
      try {
        const response = await orderApi.getOrders()
        // 检查是否是新的API格式（包含success字段）
        const responseData = response && response.hasOwnProperty('success') ? 
          (response.success ? response.data : []) : 
          response;
        
        // 确保数值字段被正确解析为数字类型，并在后端未提供总金额时用明细+运费计算
        this.orders = (responseData.orders || responseData || []).map(order => {
          const shipping = parseFloat(order.shipping_cost) || 0
          // 如果后端没有提供总金额，则根据明细计算
          let total = parseFloat(order.total_amount)
          if (isNaN(total)) {
            total = (order.items || []).reduce((sum, item) => 
              sum + (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0), 0) + shipping
          }
          
          return {
            ...order,
            total_amount: total,
            shipping_cost: shipping,
            items: (order.items || []).map(item => ({
              ...item,
              quantity: parseFloat(item.quantity) || 0,
              unit_price: parseFloat(item.unit_price) || 0,
              total_price: parseFloat(item.total_price) || 0,
              // 确保单位字段存在
              unit: item.unit || ''
            }))
          }
        })
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
        
        // 初始化新订单项的过滤产品列表
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
      this.newOrder = {
        order_type: 'purchase',
        order_number: '',
        customer_supplier: '',
        order_date: new Date().toISOString().split('T')[0],
        shipping_cost: 0,
        seller_note: '',
        items: [{ 
          product_id: '',
          product_name: '', 
          product_sku: '',
          quantity: 0,
          unit_price: 0,
          unit: '个',
          searchTerm: '',
          showDropdown: false,
          filteredProducts: [...this.allProducts]
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
    
    addItem() {
      this.newOrder.items.push({
        product_id: '',
        product_name: '',
        product_sku: '',
        quantity: 0,
        unit_price: 0,
        unit: '个',
        searchTerm: '',
        showDropdown: false,
        filteredProducts: [...this.allProducts]
      })
    },
    
    removeItem(index) {
      if (this.newOrder.items.length > 1) {
        this.newOrder.items.splice(index, 1)
      } else {
        this.newOrder.items[0] = {
          product_id: '',
          product_name: '',
          product_sku: '',
          quantity: 0,
          unit_price: 0,
          unit: '个',
          searchTerm: '',
          showDropdown: false,
          filteredProducts: [...this.allProducts]
        }
      }
    },
    
    addItemToEdit() {
      this.selectedOrder.items.push({
        id: null,
        product_id: null,
        product_name: '',
        product_sku: '',
        quantity: 0,
        unit_price: 0,
        unit: '个',
        quantity_per_box: 0,
        searchTerm: '',
        showDropdown: false,
        filteredProducts: [...this.allProducts]
      })
    },
    
    removeItemFromEdit(index) {
      if (this.selectedOrder.items.length > 1) {
        this.selectedOrder.items.splice(index, 1)
      } else {
        this.selectedOrder.items[0] = {
          product_id: '',
          product_name: '',
          product_sku: '',
          quantity: 0,
          unit_price: 0,
          unit: '个',
          searchTerm: '',
          showDropdown: false,
          filteredProducts: [...this.allProducts]
        }
      }
      this.calculateTotalForEdit()
    },
    
    async handleProductSearch(index) {
      const item = this.newOrder.items[index]
      if (item.product_name) {
        try {
          // 使用后端API搜索非复合产品
          const response = await productApi.getNonCompositeProducts({
            q: item.product_name,
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
              product.name.toLowerCase().includes(item.product_name.toLowerCase()) ||
              product.sku.toLowerCase().includes(item.product_name.toLowerCase())
            )
          )
        }
      } else {
        item.filteredProducts = [...this.allProducts]
      }
    },
    
    async handleProductSearchForEdit(index) {
      const item = this.selectedOrder.items[index]
      if (item.product_name) {
        try {
          // 使用后端API搜索非复合产品
          const response = await productApi.getNonCompositeProducts({
            q: item.product_name,
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
              product.name.toLowerCase().includes(item.product_name.toLowerCase()) ||
              product.sku.toLowerCase().includes(item.product_name.toLowerCase())
            )
          )
        }
      } else {
        item.filteredProducts = [...this.allProducts]
      }
    },
    
    hideDropdown(index) {
      // 增加延迟时间，确保用户有足够时间将鼠标移动到下拉选项
      setTimeout(() => {
        this.newOrder.items[index].showDropdown = false
      }, 300)
    },
    
    hideDropdownForEdit(index) {
      // 增加延迟时间，确保用户有足够时间将鼠标移动到下拉选项
      setTimeout(() => {
        this.selectedOrder.items[index].showDropdown = false
      }, 300)
    },
    
    selectProduct(index, product) {
      const item = this.newOrder.items[index]
      item.product_id = product.id
      item.product_name = product.name  // 将产品名称显示在输入框中
      item.product_sku = product.sku
      item.unit = product.unit || '个'  // 自动填充单位，默认值设为'个'
      // 设置默认单价
      if (product.purchase_price) {
        item.unit_price = parseFloat(product.purchase_price)
      } else if (product.cost_price) {
        item.unit_price = parseFloat(product.cost_price)
      }
      item.searchTerm = ''
      item.showDropdown = false
      item.filteredProducts = [] // 清空下拉列表
      this.calculateTotal()
    },
    
    selectProductForEdit(index, product) {
      const item = this.selectedOrder.items[index]
      item.product_id = product.id
      item.product_name = product.name  // 将产品名称显示在输入框中
      item.product_sku = product.sku
      item.unit = product.unit || '个'  // 自动填充单位，默认值设为'个'
      // 设置默认单价
      if (product.purchase_price) {
        item.unit_price = parseFloat(product.purchase_price)
      } else if (product.cost_price) {
        item.unit_price = parseFloat(product.cost_price)
      }
      item.searchTerm = ''
      item.showDropdown = false
      item.filteredProducts = [] // 清空下拉列表
      this.calculateTotalForEdit()
    },
    
    calculateTotal() {
      // 计算产品明细总金额
      const itemsTotal = this.newOrder.items.reduce((total, item) => {
        return total + (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)
      }, 0)
      
      // 加上运费
      this.newOrder.total_amount = itemsTotal + (parseFloat(this.newOrder.shipping_cost) || 0)
    },
    
    async createOrder() {
      try {
        // 验证必填字段
        if (!this.newOrder.customer_supplier.trim()) {
          this.showNotification('请输入供应商名称', 'error')
          return
        }
        
        if (!this.newOrder.order_date) {
          this.showNotification('请选择订单日期', 'error')
          return
        }

        // 验证订单项
        const hasValidItems = this.newOrder.items.some(item => 
          item.product_id && item.quantity > 0 && item.unit_price >= 0
        )

        if (!hasValidItems) {
          this.showNotification('请至少添加一个有效的订单项', 'error')
          return
        }

        // 构造订单数据
        const orderData = {
          order_type: 'purchase',
          order_number: this.newOrder.order_number || this.generateOrderNumber(),
          customer_supplier: this.newOrder.customer_supplier,
          order_date: this.newOrder.order_date,
          shipping_cost: parseFloat(this.newOrder.shipping_cost) || 0,
          seller_note: this.newOrder.seller_note,
          items: this.newOrder.items.map(item => ({
            product_id: item.product_id || null,
            quantity: parseFloat(item.quantity) || 0,
            unit_price: parseFloat(item.unit_price) || 0,
            unit: item.unit || '', // 确保单位字段被发送到后端
            description: item.product_name || '' // 使用产品名称作为描述
          })),
          status: this.newOrder.status
        }

        // 计算总金额
        const itemsTotal = orderData.items.reduce((sum, item) => 
          sum + (item.quantity * item.unit_price), 0)
        orderData.total_amount = itemsTotal + orderData.shipping_cost

        console.log('准备创建订单:', orderData)

        const response = await orderApi.createOrder(orderData)
        
        // 检查是否是新的API格式（包含success字段）
        if (response && response.hasOwnProperty('success')) {
          if (response.success) {
            this.showNotification('采购订单创建成功', 'success')
            this.closeAddOrderModal()
            await this.loadOrders() // 重新加载订单列表
          } else {
            this.showNotification('采购订单创建失败: ' + (response.message || '未知错误'), 'error')
          }
        } else {
          // 兼容旧格式
          this.showNotification('采购订单创建成功', 'success')
          this.closeAddOrderModal()
          await this.loadOrders() // 重新加载订单列表
        }
      } catch (error) {
        console.error('创建订单失败:', error)
        this.showNotification('创建订单失败: ' + (error.message || '网络错误'), 'error')
      }
    },

    generateOrderNumber() {
      const now = new Date()
      const year = now.getFullYear().toString().slice(2)
      const month = (now.getMonth() + 1).toString().padStart(2, '0')
      const day = now.getDate().toString().padStart(2, '0')
      const hours = now.getHours().toString().padStart(2, '0')
      const minutes = now.getMinutes().toString().padStart(2, '0')
      const seconds = now.getSeconds().toString().padStart(2, '0')
      return `PO-${year}${month}${day}-${hours}${minutes}${seconds}`
    },

    showNotification(message, type = 'info') {
      // 创建通知元素
      const notification = document.createElement('div')
      notification.textContent = message
      notification.style.position = 'fixed'
      notification.style.top = '20px'
      notification.style.right = '20px'
      notification.style.padding = '10px 20px'
      notification.style.borderRadius = '4px'
      notification.style.color = 'white'
      notification.style.zIndex = '9999'
      notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)'
      
      // 根据类型设置背景      
      switch(type) {
        case 'success':
          notification.style.backgroundColor = '#4CAF50'
          break
        case 'error':
          notification.style.backgroundColor = '#f44336'
          break
        case 'warning':
          notification.style.backgroundColor = '#ff9800'
          break
        default:
          notification.style.backgroundColor = '#2196F3'
      }

      document.body.appendChild(notification)

      // 3秒后自动消失
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification)
        }
      }, 3000)
    },

    viewOrder(order) {
      this.isViewMode = true
      // 深拷贝订单数据以避免修改原始数据
      this.selectedOrder = {
        ...JSON.parse(JSON.stringify(order)),
        total_amount: parseFloat(order.total_amount) || 0,
        shipping_cost: parseFloat(order.shipping_cost) || 0,
        items: (order.items || []).map(item => {
          // 确保所有必要字段都存在
          const itemCopy = {
            ...item,
            quantity: parseFloat(item.quantity) || 0,
            unit_price: parseFloat(item.unit_price) || 0,
            total_price: parseFloat(item.total_price) || 0,
            // 确保单位字段存在，优先使用item.unit，如果不存在则从产品中查找
            unit: item.unit || ''
          }
          
          // 确保产品名称和SKU字段正确设置
          if (!itemCopy.product_name && itemCopy.product_id) {
            // 如果有product_id但没有product_name，尝试从allProducts中查找
            const product = this.allProducts.find(p => p.id === itemCopy.product_id)
            if (product) {
              itemCopy.product_name = product.name
              itemCopy.product_sku = product.sku
              // 确保单位也被设置
              if (!itemCopy.unit && product.unit) {
                itemCopy.unit = product.unit
              }
            }
          }
          
          // 如果仍然没有产品名称，使用描述作为产品名称
          if (!itemCopy.product_name && itemCopy.description) {
            itemCopy.product_name = itemCopy.description
          }
          
          // 设置搜索字段
          itemCopy.searchTerm = itemCopy.product_name || ''
          itemCopy.filteredProducts = [...this.allProducts]
          itemCopy.showDropdown = false
          
          return itemCopy
        })
      }
      
      this.openEditModal()
    },

    editOrder(order) {
      this.isViewMode = false
      // 确保数值字段被正确解析为数字类别
      this.selectedOrder = {
        ...JSON.parse(JSON.stringify(order)),
        total_amount: parseFloat(order.total_amount) || 0,
        shipping_cost: parseFloat(order.shipping_cost) || 0,
        items: (order.items || []).map(item => {
          // 确保所有必要字段都存在
          const itemCopy = {
            ...item,
            quantity: parseFloat(item.quantity) || 0,
            unit_price: parseFloat(item.unit_price) || 0,
            total_price: parseFloat(item.total_price) || 0,
            // 确保单位字段存在，优先使用item.unit，如果不存在则从产品中查找
            unit: item.unit || ''
          }
          
          // 确保产品名称和SKU字段正确设置
          if (!itemCopy.product_name && itemCopy.product_id) {
            // 如果有product_id但没有product_name，尝试从allProducts中查找
            const product = this.allProducts.find(p => p.id === itemCopy.product_id)
            if (product) {
              itemCopy.product_name = product.name
              itemCopy.product_sku = product.sku
              // 确保单位也被设置
              if (!itemCopy.unit && product.unit) {
                itemCopy.unit = product.unit
              }
            }
          }
          
          // 如果仍然没有产品名称，使用描述作为产品名称
          if (!itemCopy.product_name && itemCopy.description) {
            itemCopy.product_name = itemCopy.description
          }
          
          // 设置搜索字段
          itemCopy.searchTerm = itemCopy.product_name || ''
          itemCopy.filteredProducts = [...this.allProducts]
          itemCopy.showDropdown = false
          
          return itemCopy
        })
      }
      
      this.openEditModal()
    },

    // 新增方法：从查看模式切换到编辑模式
    switchToEditMode() {
      this.isViewMode = false
    },
    
    calculateTotalForEdit() {
      if (this.selectedOrder && this.selectedOrder.items) {
        // 计算产品明细总金额
        const itemsTotal = this.selectedOrder.items.reduce((total, item) => {
          return total + (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)
        }, 0)
        
        // 加上运费
        this.selectedOrder.total_amount = itemsTotal + (parseFloat(this.selectedOrder.shipping_cost) || 0)
      }
    },
    
    async updateOrder() {
      try {
        // 验证必填字段
        if (!this.selectedOrder.customer_supplier.trim()) {
          this.showNotification('请输入供应商名称', 'error')
          return
        }
        
        if (!this.selectedOrder.order_date) {
          this.showNotification('请选择订单日期', 'error')
          return
        }

        // 验证订单项
        const hasValidItems = this.selectedOrder.items.some(item => 
          item.product_id && item.quantity > 0 && item.unit_price >= 0
        )

        if (!hasValidItems) {
          this.showNotification('请至少添加一个有效的订单项', 'error')
          return
        }

        // 构造订单数据
        const orderData = {
          order_type: 'purchase',
          order_number: this.selectedOrder.order_number,
          customer_supplier: this.selectedOrder.customer_supplier,
          order_date: this.selectedOrder.order_date,
          shipping_cost: parseFloat(this.selectedOrder.shipping_cost) || 0,
          seller_note: this.selectedOrder.seller_note,
          items: this.selectedOrder.items.map(item => ({
            product_id: item.product_id,
            quantity: parseFloat(item.quantity) || 0,
            unit_price: parseFloat(item.unit_price) || 0,
            unit: item.unit || '', // 确保单位字段被发送到后端
            description: item.product_name || '' // 使用产品名称作为描述
          })),
          status: this.selectedOrder.status
        }

        // 计算总金额
        const itemsTotal = orderData.items.reduce((sum, item) => 
          sum + (item.quantity * item.unit_price), 0)
        orderData.total_amount = itemsTotal + orderData.shipping_cost

        console.log('准备更新订单:', orderData)

        const response = await orderApi.updateOrder(this.selectedOrder.id, orderData)
        
        // 检查是否是新的API格式（包含success字段）
        if (response && response.hasOwnProperty('success')) {
          if (response.success) {
            this.showNotification('采购订单更新成功', 'success')
            this.closeEditModal()
            await this.loadOrders() // 重新加载订单列表
          } else {
            this.showNotification('采购订单更新失败: ' + (response.message || '未知错误'), 'error')
          }
        } else {
          // 兼容旧格式
          this.showNotification('采购订单更新成功', 'success')
          this.closeEditModal()
          await this.loadOrders() // 重新加载订单列表
        }
      } catch (error) {
        console.error('更新订单失败:', error)
        this.showNotification('更新订单失败: ' + (error.message || '网络错误'), 'error')
      }
    },

    async deleteOrder(order) {
      if (!confirm(`确定要删除订单 ${order.order_number} 吗？`)) {
        return
      }
      
      try {
        const response = await orderApi.deleteOrder(order.id)
        
        // 检查是否是新的API格式（包含success字段）
        if (response && response.hasOwnProperty('success')) {
          if (response.success) {
            this.showNotification('采购订单删除成功', 'success')
            await this.loadOrders() // 重新加载订单列表
          } else {
            this.showNotification('采购订单删除失败: ' + (response.message || '未知错误'), 'error')
          }
        } else {
          // 兼容旧格式
          this.showNotification('采购订单删除成功', 'success')
          await this.loadOrders() // 重新加载订单列表
        }
      } catch (error) {
        console.error('删除订单失败:', error)
        this.showNotification('删除订单失败: ' + (error.message || '网络错误'), 'error')
      }
    },

    printOrder(order) {
      // 创建打印窗口
      const printWindow = window.open('', '_blank')
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>采购订单 - ${order.order_number}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 20px; }
            .order-info { display: flex; justify-content: space-between; margin-bottom: 20px; }
            .info-section { flex: 1; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .total { text-align: right; font-weight: bold; }
            .footer { margin-top: 30px; text-align: center; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>采购订单</h1>
            <p>订单号: ${order.order_number}</p>
          </div>
          
          <div class="order-info">
            <div class="info-section">
              <h3>供应商信息</h3>
              <table>
                <tr>
                  <td>订单号</td>
                  <td>${order.order_number || '未填'}</td>
                  <td>供应商</td>
                  <td>${order.customer_supplier || '未填'}</td>
                </tr>
                <tr>
                  <td>订单日期</td>
                  <td>${this.formatDate(order.order_date)}</td>
                  <td>订单状态</td>
                  <td>${this.getStatusText(order.status)}</td>
                </tr>
              </table>
            </div>
          </div>
          
          <h3>订单明细</h3>
          <table>
            <thead>
              <tr>
                <th>产品名称</th>
                <th>SKU</th>
                <th>单价</th>
                <th>单位</th>
                <th>数量</th>
                <th>金额</th>
              </tr>
            </thead>
            <tbody>
              ${(order.items || []).map(item => `
                <tr>
                  <td>${item.product_name || item.description || '未指定'}</td>
                  <td>${item.product_sku || ''}</td>
                  <td>¥${parseFloat(item.unit_price || 0).toFixed(2)}</td>
                  <td>${item.unit || ''}</td>
                  <td>${item.quantity || 0}</td>
                  <td>¥${(parseFloat(item.quantity || 0) * parseFloat(item.unit_price || 0)).toFixed(2)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
          
          <div class="total">
            <p>运费: ¥${parseFloat(order.shipping_cost || 0).toFixed(2)}</p>
            <p>总计: ¥${parseFloat(order.total_amount || 0).toFixed(2)}</p>
          </div>
          
          <div class="footer">
            <p>卖家备注: ${order.seller_note || '无'}</p>
            <p>打印时间: ${new Date().toLocaleString('zh-CN')}</p>
          </div>
        </body>
        </html>
      `)
      
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
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.section-header h3,
.section-header h5 {
  margin: 0;
  color: #333;
}

.filters {
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.table-container {
  overflow-x: auto;
  padding: 20px;
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
  color: #555;
}

.order-number {
  font-weight: 600;
  color: #007bff;
}

.amount {
  font-weight: 600;
  color: #28a745;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
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

.btn {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 5px;
  transition: background-color 0.2s;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #1e7e34;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-info:hover {
  background-color: #117a8b;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h4 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.form-control-static {
  padding: 8px 12px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.total-amount {
  font-size: 18px;
  font-weight: 600;
  color: #28a745;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid #eee;
  gap: 10px;
}

/* 订单明细表格样式 */
.order-items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.order-items-table th,
.order-items-table td {
  padding: 10px;
  border: 1px solid #ddd;
  vertical-align: top;
}

.order-items-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
  text-align: center;
}

.order-items-table tbody tr:hover {
  background-color: #f9f9f9;
}

.order-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
}

.order-input:disabled {
  background-color: #f8f9fa;
  color: #666;
}

.order-input[readonly] {
  background-color: #f8f9fa;
  cursor: pointer;
}

.amount-cell {
  font-weight: 600;
  color: #28a745;
  text-align: center;
  vertical-align: middle;
}

.item-controls {
  position: relative;
}

.product-search {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
  background-color: #f8f9fa;
  cursor: pointer;
}

.product-search:focus {
  background-color: white;
}

.product-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 100;
  max-height: 200px;
  overflow-y: auto;
}

.product-option {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.product-option:last-child {
  border-bottom: none;
}

.product-option:hover {
  background-color: #f8f9fa;
}

.icon {
  margin-right: 5px;
}
</style>