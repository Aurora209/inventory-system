 <template>
  <div class="orders-page">
    <div class="container">
  <div class="section">
        <div class="section-header">
          <h3>订单列表</h3>
          <button class="btn btn-primary" @click="openAddOrderModal">
            <i class="icon">➕</i> 添加订单
          </button>
        </div>

        <div class="filters">
          <select v-model="filterType">
            <option value="">所有类型</option>
            <option value="purchase">采购订单</option>
            <option value="sale">销售订单</option>
          </select>
        </div>
        

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>订单号</th>
                <th>类型</th>
                <th>客户/供应商</th>
                <th>日期</th>
                <th>总金额</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.id">
                <td class="order-number">{{ order.order_number }}</td>
                <td>
                  <span :class="['order-type', `type-${order.order_type}`]">
                    {{ order.order_type === 'purchase' ? '采购' : '销售' }}
                  </span>
                </td>
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
                <td colspan="7" class="empty-state">暂无订单数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 创建订单模态框 -->
      <div class="modal-overlay" v-if="showAddModal" @click="closeAddOrderModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>创建订单</h3>
            <button class="modal-close" @click="closeAddOrderModal">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createOrder">
              <div class="form-group">
                <label>订单号</label>
                <input type="text" v-model="newOrder.order_number" placeholder="输入订单号（可手动填写）" />
              </div>

              <div class="form-group">
                <label>订单类型 *</label>
                <select v-model="newOrder.order_type" required>
                  <option value="">请选择订单类型</option>
                  <option value="purchase">采购订单</option>
                  <option value="sale">销售订单</option>
                </select>
              </div>

              <div class="form-group">
                <label>客户/供应商 *</label>
                <input type="text" v-model="newOrder.customer_supplier" required placeholder="输入客户或供应商名称">
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
              
              <!-- 明细表格：横向表格展示订单明细，含表头 -->
              <div class="form-group">
                <label>订单明细</label>
                <div class="order-items">
                  <table class="order-items-table">
                    <thead>
                      <tr>
                        <th style="width:28%">产品（搜索/选择）</th>
                        <th style="width:28%">描述</th>
                        <th style="width:10%">数量</th>
                        <th style="width:12%">单价</th>
                        <th style="width:12%">每箱数量</th>
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
                              @input="filterProducts(idx)"
                              @focus="item.showDropdown = true"
                              @blur="hideDropdown(idx)"
                              class="product-search"
                            />
                            <div v-if="item.showDropdown && item.filteredProducts.length" class="product-dropdown">
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
                          <input
                            type="text"
                            v-model="item.description"
                            placeholder="产品描述"
                            :disabled="!!item.product_id"
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            v-model.number="item.quantity"
                            placeholder="数量"
                            min="1"
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            v-model.number="item.unit_price"
                            placeholder="单价"
                            min="0"
                            step="0.01"
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            v-model.number="item.units_per_box"
                            placeholder="每箱数量"
                            min="1"
                          />
                        </td>
                        <td>
                          <button type="button" class="btn btn-danger btn-sm" @click="removeNewItem(idx)">删除</button>
                        </td>
                      </tr>
                      <tr v-if="!newOrder.items || newOrder.items.length === 0">
                        <td colspan="6" class="empty-state">暂无明细项</td>
                      </tr>
                    </tbody>
                  </table>

                  <div style="margin-top:10px">
                    <button type="button" class="btn btn-secondary" @click="addNewItem">+ 添加明细项</button>
                  </div>
                </div>
              </div>
              
              <div class="form-group">
                <label>状态</label>
                <select v-model="newOrder.status">
                  <option value="pending">待处理</option>
                  <option value="processing">处理中</option>
                  <option value="completed">已完成</option>
                </select>
              </div>
              
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="closeAddOrderModal">取消</button>
                <button type="submit" class="btn btn-primary">创建订单</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 发票查看/打印模态 -->
      <div class="modal-overlay invoice-overlay" v-if="selectedOrder" @click="closeInvoice">
        <div class="modal-content invoice-content" @click.stop>
          <div class="modal-header">
            <h3>商业发票 Invoice</h3>
            <div>
              <button class="btn btn-secondary" @click="printInvoice">打印</button>
              <button class="modal-close" @click="closeInvoice">×</button>
            </div>
          </div>
          <div class="modal-body invoice-body">
            <div class="invoice" v-if="selectedOrder">
              <!-- 调试信息 -->
              <!--
              <div v-if="false" style="margin-top: 20px; padding: 10px; background: #f0f0f0; border-radius: 4px;">
                <h4>调试信息</h4>
                <p>selectedOrder: {{ selectedOrder }}</p>
                <p>invoiceItems: {{ invoiceItems }}</p>
                <p>hasItems: {{ hasItems }}</p>
              </div>
              -->
              
              <div class="invoice-header">
                <div class="seller">
                  <h4>{{ selectedOrder.seller_name || '' }}</h4>
                  <div>{{ selectedOrder.seller_address || '' }}</div>
                  <div>电话: {{ selectedOrder.seller_phone || '' }}</div>
                  <div>税号: {{ selectedOrder.seller_taxNo || '' }}</div>
                  <div v-if="selectedOrder.seller_note" style="margin-top:6px;white-space:pre-wrap">{{ selectedOrder.seller_note }}</div>
                </div>
                <div class="invoice-meta">
                  <div><strong>发票号：</strong>{{ selectedOrder.order_number || '--' }}</div>
                  <div><strong>类型：</strong>{{ selectedOrder.order_type === 'purchase' ? '采购' : '销售' }}</div>
                  <div><strong>日期：</strong>{{ formatDate(selectedOrder.order_date) }}</div>
                  <div><strong>状态：</strong>{{ getStatusText(selectedOrder.status) }}</div>
                </div>
              </div>
              
              <div class="bill-to">
                <strong>收/付款方：</strong>
                <div>{{ selectedOrder.customer_supplier }}</div>
                <div v-if="selectedOrder.buyer_note" style="margin-top:6px;white-space:pre-wrap">{{ selectedOrder.buyer_note }}</div>
              </div>

              <table class="invoice-table">
                <thead>
                  <tr>
                    <th>序号</th>
                    <th>描述</th>
                    <th>数量</th>
                    <th>单价</th>
                    <th>小计</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!hasItems">
                    <td colspan="5" class="empty-state">无明细项，显示订单总额</td>
                  </tr>
                  <tr v-for="(item, idx) in invoiceItems" :key="idx">
                    <td>{{ idx + 1 }}</td>
                    <td>{{ item.description }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>¥{{ Number(item.unit_price).toFixed(2) }}</td>
                    <td>¥{{ (Number(item.quantity) * Number(item.unit_price)).toFixed(2) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="4" class="text-right">小计</td>
                    <td>¥{{ subTotal.toFixed(2) }}</td>
                  </tr>
                  <tr>
                    <td colspan="4" class="text-right">税 ({{ taxRate * 100 }}%)</td>
                    <td>¥{{ taxAmount.toFixed(2) }}</td>
                  </tr>
                  <tr class="grand-total">
                    <td colspan="4" class="text-right"><strong>总计</strong></td>
                    <td><strong>¥{{ grandTotal.toFixed(2) }}</strong></td>
                  </tr>
                </tfoot>
              </table>
              
              <div class="invoice-foot">
                <div>备注: {{ selectedOrder.note || '—' }}</div>
                <div class="signatures">
                  <div>经办: _____________</div>
                  <div>签字: _____________</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 装箱单模态框 -->
      <div class="modal-overlay" v-if="showPackingModal" @click="closePackingModal">
        <div class="modal-content" @click.stop>
          <packing-list 
            :order="packingOrder" 
            @close="closePackingModal"
            @saved="handlePackingSaved"
          />
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { productApi, orderApi } from '@/services/api.js'
import PackingList from './PackingList.vue'

export default {
  name: 'Orders',
  components: {
    PackingList
  },
  data() {
    return {
      orders: [],
      products: [],
      filterType: '',
      filterStatus: '',
      showAddModal: false,
      showPackingModal: false,
      selectedOrder: null,
      packingOrder: null,
      newOrder: {
        order_number: '',
        order_type: '',
        customer_supplier: '',
        buyer_note: '',
        order_date: '',
        total_amount: 0,
        status: 'pending',
        items: [],
        seller_note: ''
      },
      seller: {
        name: '示例公司',
        address: '上海市浦东新区示例路1234号',
        phone: '021-12345678',
        taxNo: '123456789012345'
      },
      taxRate: 0.13,
      invoiceItems: []
    }
  },
  async mounted() {
    try {
      // 使用 Promise.all 并行加载数据，提高加载效率
      await Promise.all([
        this.loadOrders(),
        this.loadProducts()
      ])
    } catch (error) {
      console.error('❌ 页面初始化失败:', error)
      // 即使部分数据加载失败，也要确保界面可用
      this.orders = []
      this.products = []
    }
  },
  computed: {
    invoiceItems() {
      if (!this.selectedOrder) return []
      const items = this.selectedOrder.items
      return items && Array.isArray(items) ? items : []
    },
    hasItems() {
      const items = this.selectedOrder && this.selectedOrder.items
      return items && Array.isArray(items) && items.length > 0
    },
    subTotal() {
      if (!this.hasItems) {
        return Number((this.selectedOrder && this.selectedOrder.total_amount) || 0)
      }
      if (!this.invoiceItems || !Array.isArray(this.invoiceItems)) {
        return 0
      }
      return this.invoiceItems.reduce((s, it) => {
        const quantity = Number(it.quantity || 0)
        const unitPrice = Number(it.unit_price || 0)
        return s + (quantity * unitPrice)
      }, 0)
    },
    taxAmount() {
      return this.subTotal * this.taxRate
    },
    grandTotal() {
      return this.subTotal + this.taxAmount
    },
    filteredOrders() {
      // 添加订单过滤功能，确保显示正确的订单列表
      let result = this.orders || []
      
      // 根据订单类型过滤
      if (this.filterType) {
        result = result.filter(order => order.order_type === this.filterType)
      }
      
      // 根据订单状态过滤
      if (this.filterStatus) {
        result = result.filter(order => order.status === this.filterStatus)
      }
      
      return result
    }
  },
  methods: {
    async loadOrders() {
      try {
        const response = await orderApi.getOrders()
        
        // 检查响应格式
        if (!response) {
          this.orders = []
          return
        }
        
        // 根据新的API响应格式处理数据
        if (response.success) {
          // 处理 {success: true, data: [...]} 结构
          this.orders = Array.isArray(response.data) ? [...response.data] : []
        } else {
          console.error('获取订单数据失败:', response.message)
          this.orders = []
        }
      } catch (error) {
        console.error('获取订单数据出错:', error)
        this.orders = []
      }
    },
    
    async loadProducts() {
      try {
        console.log('开始加载产品列表...')
        const response = await productApi.getProducts()
        console.log('产品列表响应:', response)
        
        // 根据新的API响应格式处理数据
        if (response.success) {
          this.products = Array.isArray(response.data) ? [...response.data] : []
        } else {
          console.error('获取产品数据失败:', response.message)
          this.products = []
        }
        console.log('处理后的产品列表:', this.products)
      } catch (error) {
        console.error('获取产品数据出错:', error)
        console.error('错误详情:', {
          message: error.message,
          response: error.response,
          status: error.response?.status
        })
        this.products = []
      }
    },

    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString('zh-CN')
    },

    getStatusText(status) {
      const statusMap = {
        pending: '待处理',
        processing: '处理中',
        completed: '已完成'
      }
      return statusMap[status] || status
    },

    filterProducts(idx) {
      const item = this.newOrder.items[idx]
      const term = (item.searchTerm || '').toString().trim().toLowerCase()

      if (!term) {
        // 当没有输入时，显示前10个产品以便用户快速选择
        item.filteredProducts = (this.products || []).slice(0, 10)
        item.showDropdown = item.filteredProducts.length > 0
        return
      }

      item.filteredProducts = (this.products || []).filter(product => {
        const name = (product.name || '').toString().toLowerCase()
        const sku = (product.sku || '').toString().toLowerCase()
        return name.includes(term) || sku.includes(term)
      }).slice(0, 10)

      item.showDropdown = item.filteredProducts.length > 0
    },

    selectProduct(idx, product) {
      const item = this.newOrder.items[idx]
      item.product_id = product.id
      item.description = `${product.name} (${product.sku})`
      item.unit_price = product.price || 0
      item.units_per_box = product.units_per_box || 1
      item.searchTerm = ''
      item.showDropdown = false
      
      // 触发Vue更新 - 在Vue 3中不需要使用$set
      // this.$set(this.newOrder.items, idx, item)
      this.newOrder.items[idx] = item
    },

    hideDropdown(idx) {
      // 延迟隐藏下拉框，确保点击选项时不会立即隐藏
      setTimeout(() => {
        if (this.newOrder.items[idx]) {
          this.newOrder.items[idx].showDropdown = false
        }
      }, 200)
    },

    async createOrder() {
      try {
        // 创建订单数据副本以避免修改原始响应数据
        const orderToAdd = JSON.parse(JSON.stringify(this.newOrder || {}))
        
        // 确保必需字段存在
        if (!orderToAdd.order_type) {
          alert('请选择订单类型')
          return
        }
        if (!orderToAdd.customer_supplier) {
          alert('请输入客户/供应商')
          return
        }
        if (!orderToAdd.order_date) {
          alert('请选择订单日期')
          return
        }
        
        // 规范化明细项字段，确保每项都有数量、单价和每箱数
        if (orderToAdd.items && orderToAdd.items.length) {
          orderToAdd.items = orderToAdd.items.map(it => ({
            product_id: it.product_id || null,
            description: it.description || '',
            quantity: Number(it.quantity || 0),
            unit_price: Number(it.unit_price || 0),
            units_per_box: Number(it.units_per_box || 1),
            packaging: it.packaging || ''
          }))
          orderToAdd.total_amount = orderToAdd.items.reduce((s, it) => s + (Number(it.quantity || 0) * Number(it.unit_price || 0)), 0)
        } else {
          orderToAdd.items = []
          orderToAdd.total_amount = Number(orderToAdd.total_amount || 0)
        }
        
        // 检查是创建还是更新订单
        let response
        if (orderToAdd.id) {
          // 更新现有订单
          response = await orderApi.updateOrder(orderToAdd.id, orderToAdd)
        } else {
          // 发送到后端创建订单
          response = await orderApi.createOrder(orderToAdd)
        }

        // 兼容 api 客户端返回的不同结构（可能直接返回对象或 {data: ...}）
        const created = response?.data || response
        if (created) {
          // 显示成功消息
          alert('订单保存成功')

          // 将刚创建/更新的订单设为 selectedOrder，以便可以立即创建装箱单或打印发票
          this.selectedOrder = created
          // 兼容后端字段名 notes -> 前端使用的 note / buyer_note
          this.selectedOrder.note = this.selectedOrder.note || this.selectedOrder.notes || ''
          this.selectedOrder.buyer_note = this.selectedOrder.buyer_note || this.selectedOrder.notes || ''

          // 重新加载订单列表以确保数据同步
          try {
            await this.loadOrders()
          } catch (error) {
            console.error('刷新订单列表失败:', error)
          }
        }

        // 关闭模态框
        this.showAddModal = false

        // 重置创建表单为初始状态
        this.resetNewOrder()
      } catch (error) {
        // 即使出错也关闭模态框
        this.showAddModal = false
        console.error('保存订单失败:', error)
        const errorMsg = error.response?.data?.message || error.message
        // 显示错误消息
        alert('保存订单失败: ' + errorMsg)
        // 出错时也重置表单
        this.resetNewOrder()
      }
    },

    resetNewOrder() {
      const today = new Date().toISOString().split('T')[0]
      this.newOrder = {
        order_number: '',
        order_type: '',
        customer_supplier: '',
        buyer_note: '',
        order_date: today,
        total_amount: 0,
        status: 'pending',
        items: [{
          product_id: '',
          description: '',
          quantity: 1,
          unit_price: 0,
          units_per_box: 1,
          searchTerm: '',
          filteredProducts: [],
          showDropdown: false
        }],
        seller_note: ''
      }
    },
    forceUpdateOrders() {
      // 强制更新订单列表
      console.log('强制更新订单列表')
      this.$forceUpdate()
    },
    
    async testLoadOrders() {
      console.log('手动测试加载订单列表')
      this.loadOrders()
    },

    testViewOrder() {
      if (this.orders && this.orders.length > 0) {
        console.log('测试查看第一个订单')
        this.viewOrder(this.orders[0])
      } else {
        console.log('没有可用的订单进行测试')
      }
    },

    showTestInvoice() {
      if (this.orders && this.orders.length > 0) {
        console.log('直接设置selectedOrder以显示发票')
        this.selectedOrder = JSON.parse(JSON.stringify(this.orders[0]))
        console.log('selectedOrder已设置:', this.selectedOrder)
      } else {
        console.log('没有可用的订单进行测试')
        // 创建一个测试订单用于调试
        const testOrder = {
          id: 1,
          order_number: 'TEST20251102001',
          order_type: 'purchase',
          customer_supplier: '测试供应商',
          order_date: '2025-11-02',
          total_amount: 100.00,
          status: 'pending',
          items: [
            {
              id: 1,
              product_id: 1,
              description: '测试产品',
              quantity: 2,
              unit_price: 50.00,
              units_per_box: 1
            }
          ]
        }
        this.selectedOrder = testOrder
        console.log('使用测试订单:', this.selectedOrder)
      }
    },

    addNewItem() {
      this.newOrder.items.push({ 
        product_id: '', 
        description: '', 
        quantity: 1, 
        unit_price: 0, 
        units_per_box: 1,
        searchTerm: '',
        filteredProducts: [],
        showDropdown: false
      })
    },

    removeNewItem(idx) {
      this.newOrder.items.splice(idx, 1)
    },

    openAddOrderModal() { 
      this.resetNewOrder()
      this.showAddModal = true 
    },
    closeAddOrderModal() { 
      this.showAddModal = false 
    },
    
    async viewOrder(order) {
      try {
        // 总是从后端获取完整的订单信息，确保包含订单项
        const response = await orderApi.getOrder(order.id)
        if (response && response.data) {
          this.selectedOrder = response.data
          // 兼容后端字段名 notes -> 前端使用的 note / buyer_note
          this.selectedOrder.note = this.selectedOrder.note || this.selectedOrder.notes || ''
          this.selectedOrder.buyer_note = this.selectedOrder.buyer_note || this.selectedOrder.notes || ''
          
          // 确保每个订单项都有packing属性
          if (this.selectedOrder.items && Array.isArray(this.selectedOrder.items)) {
            this.selectedOrder.items.forEach(item => {
              if (item.packing === undefined) {
                item.packing = [];
              }
            });
          } else {
            this.selectedOrder.items = [];
          }
        } else {
          // 如果后端获取失败，使用传入的订单数据
          this.selectedOrder = JSON.parse(JSON.stringify(order || {}))
          if (!this.selectedOrder.items) {
            this.selectedOrder.items = []
          }
          
          // 确保每个订单项都有packing属性
          this.selectedOrder.items.forEach(item => {
            if (item.packing === undefined) {
              item.packing = [];
            }
          });
        }
      } catch (error) {
        console.error('查看订单失败:', error)
        // 出错时使用传入的订单数据
        const orderCopy = JSON.parse(JSON.stringify(order || {}))
        if (!orderCopy.items) {
          orderCopy.items = []
        }
        
        // 确保每个订单项都有packing属性
        orderCopy.items.forEach(item => {
          if (item.packing === undefined) {
            item.packing = [];
          }
        });
        
        this.selectedOrder = orderCopy
      }
    },

    editOrder(order) {
      // 编辑订单
      this.newOrder = {
        ...order,
        // 兼容不同字段命名
        buyer_note: order.buyer_note || order.notes || '',
        // 确保 items 存在并且格式正确
        items: Array.isArray(order.items) 
          ? order.items.map(item => ({...item})) 
          : []
      }
      
      // 确保每个订单项都有必要的字段
      if (this.newOrder.items && this.newOrder.items.length) {
        this.newOrder.items = this.newOrder.items.map(item => {
          // 确保每个订单项都有这些字段
          return {
            product_id: item.product_id || null,
            description: item.description || '',
            quantity: Number(item.quantity || 0),
            unit_price: Number(item.unit_price || 0),
            units_per_box: Number(item.units_per_box || 1),
            packaging: item.packaging || '',
            notes: item.notes || '',
            ...item  // 保留其他字段
          }
        })
      } else {
        // 确保至少有一个空项
        this.newOrder.items = [{
          product_id: '',
          description: '',
          quantity: 1,
          unit_price: 0,
          units_per_box: 1,
          packaging: '',
          notes: ''
        }]
      }
      
      // 打开编辑模态框
      this.showAddModal = true
    },

    showPackingList(order) {
      // 显示装箱单编辑界面
      this.packingOrder = JSON.parse(JSON.stringify(order));
      this.showPackingModal = true;
    },

    closePackingModal() {
      this.showPackingModal = false;
      this.packingOrder = null;
    },

    handlePackingSaved(updatedOrder) {
      // 处理装箱单保存后的逻辑
      // 更新订单列表中的订单
      const index = this.orders.findIndex(o => o.id === updatedOrder.id);
      if (index !== -1) {
        this.orders[index] = updatedOrder;
      }
      
      // 如果当前查看的订单是同一个，则也更新它
      if (this.selectedOrder && this.selectedOrder.id === updatedOrder.id) {
        this.selectedOrder = updatedOrder;
      }
      
      this.closePackingModal();
    },

    closeInvoice() { this.selectedOrder = null },

    printInvoice() {
      // 使用基于数据的自包含打印模板，避免依赖 DOM 克隆或外部 scoped 样式导致空白
      if (!this.selectedOrder) {
        window.print()
        return
      }

      const order = this.selectedOrder
      const items = (order.items && order.items.length) ? order.items : []

      const subTotal = items.reduce((s, it) => s + (Number(it.quantity || 0) * Number(it.unit_price || 0)), 0) || Number(order.total_amount || 0)
      const taxAmount = +(subTotal * this.taxRate).toFixed(2)
      const grandTotal = +(subTotal + taxAmount).toFixed(2)

      // 内联样式，确保在新窗口/打印时可见
      const style = `
        body{font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial;padding:16px;color:#111}
        .inv-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px}
        .inv-title{font-size:20px;font-weight:700}
        table{width:100%;border-collapse:collapse;margin-top:8px}
        th,td{border:1px solid #ddd;padding:8px;text-align:left}
        th{background:#f6f6f6}
        .totals{margin-top:12px;display:flex;justify-content:flex-end}
        .totals table{width:300px}
        @media print{body{padding:8mm} .no-print{display:none!important}}
      `

      const itemsRows = items.map(it => `
        <tr>
          <td>${(it.description || '')}</td>
          <td style="width:80px;text-align:right">${Number(it.quantity || 0)}</td>
          <td style="width:120px;text-align:right">${Number(it.unit_price || 0).toFixed(2)}</td>
          <td style="width:120px;text-align:right">${(Number(it.quantity || 0) * Number(it.unit_price || 0)).toFixed(2)}</td>
        </tr>
      `).join('\n')

      const invoiceHtml = `<!doctype html><html><head><meta charset="utf-8"><title>发票 - ${order.order_number || ''}</title><style>${style}</style></head><body>
            <div class="inv-header">
          <div>
            <div style="font-weight:700">${order.seller_name || ''}</div>
            <div>${order.seller_address || ''}</div>
            <div>${order.seller_phone || ''}</div>
            <div>税号: ${order.seller_taxNo || ''}</div>
          </div>
          <div style="text-align:right">
            <div class="inv-title">商业发票 / Invoice</div>
            <div>订单号: ${order.order_number || ''}</div>
            <div>日期: ${this.formatDate(order.order_date) || ''}</div>
          </div>
        </div>

        <div>
          <strong>收货方 / Bill To</strong>
          <div>${order.customer_supplier || ''}</div>
        </div>

        <table aria-label="items">
          <thead>
            <tr><th>描述</th><th style="width:80px">数量</th><th style="width:120px">单价</th><th style="width:120px">小计</th></tr>
          </thead>
          <tbody>
            ${itemsRows || `<tr><td colspan="4">（无明细，显示总价）</td></tr>`}
          </tbody>
        </table>

        <div class="totals">
          <table>
            <tbody>
              <tr><td>小计</td><td style="text-align:right">${subTotal.toFixed(2)}</td></tr>
              <tr><td>税 (${(this.taxRate*100).toFixed(0)}%)</td><td style="text-align:right">${taxAmount.toFixed(2)}</td></tr>
              <tr><td style="font-weight:700">总计</td><td style="text-align:right;font-weight:700">${grandTotal.toFixed(2)}</td></tr>
            </tbody>
          </table>
        </div>

        <div style="margin-top:20px;font-size:12px;color:#666">此发票由系统生成，供内部记录使用。</div>
      </body></html>`

      const w = window.open('', '_blank')
      if (!w) {
        // 无法弹窗时回退
        console.warn('打印失败：浏览器阻止弹窗，退回到 window.print()')
        window.print()
        return
      }
      w.document.open()
      w.document.write(invoiceHtml)
      w.document.close()
      w.focus()
      // 给新窗口一点时间渲染后打印
      setTimeout(() => {
        try { w.print() } catch (e) { console.error('print error', e) }
        // 不强制关闭，浏览器可能拦截；但尝试关闭
        try { w.close() } catch (e) {}
      }, 400)
    },

    printPackingList() {
      // 生成自包含的装箱单 HTML 并在新窗口打印
      if (!this.selectedOrder) {
        window.print()
        return
      }

      const order = this.selectedOrder
      const items = (order.items && order.items.length) ? order.items : []

      const style = `
        body{font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial;padding:16px;color:#111}
        .pl-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px}
        .pl-title{font-size:20px;font-weight:700}
        table{width:100%;border-collapse:collapse;margin-top:8px}
        th,td{border:1px solid #ddd;padding:8px;text-align:left}
        th{background:#f6f6f6}
        @media print{body{padding:8mm} .no-print{display:none!important}}
      `

      // 生成装箱计划：按每箱数量拆箱，输出每箱明细
      const itemSummaries = items.map((it, idx) => {
        // 使用手动编辑的装箱信息（如果有）
        if (it.packing && Array.isArray(it.packing) && it.packing.length > 0) {
          const boxes = it.packing.map((box, boxIndex) => ({
            boxNo: boxIndex + 1,
            qty: box.quantity
          }));
          
          return {
            idx: idx + 1,
            description: it.description || '',
            qty: boxes.reduce((sum, box) => sum + box.qty, 0),
            perBox: it.units_per_box || 1,
            fullBoxes: boxes.length,
            remainder: boxes.length > 0 ? boxes[boxes.length - 1].qty : 0,
            totalBoxes: boxes.length,
            boxes
          }
        }
        
        // 否则使用自动计算的装箱信息
        const qty = Number(it.quantity || 0)
        const perBox = Number(it.units_per_box || 1) || 1
        const fullBoxes = Math.floor(qty / perBox)
        const remainder = qty % perBox
        const totalBoxes = Math.ceil(qty / perBox)

        // 生成每箱内容的数组
        const boxes = []
        for (let b = 1; b <= fullBoxes; b++) {
          boxes.push({ boxNo: b, qty: perBox })
        }
        if (remainder > 0) {
          boxes.push({ boxNo: fullBoxes + 1, qty: remainder })
        }

        return {
          idx: idx + 1,
          description: it.description || '',
          qty,
          perBox,
          fullBoxes,
          remainder,
          totalBoxes,
          boxes
        }
      })

      const summaryRows = itemSummaries.map(s => `
        <tr>
          <td style="width:60px;text-align:center">${s.idx}</td>
          <td>${s.description}</td>
          <td style="width:100px;text-align:right">${s.qty}</td>
          <td style="width:120px;text-align:right">${s.perBox}</td>
          <td style="width:120px;text-align:right">${s.totalBoxes}</td>
        </tr>
      `).join('\n')

      // 每箱明细（按商品分组列出每箱数量）
      const boxesHtml = itemSummaries.map(s => `
        <div style="margin-top:12px">
          <div style="font-weight:600;margin-bottom:6px">${s.idx}. ${s.description} — 共 ${s.qty} 件， 每箱 ${s.perBox} 件， 箱数 ${s.totalBoxes}</div>
          <table style="margin-bottom:8px">
            <thead><tr><th style="width:80px">箱号</th><th>数量</th></tr></thead>
            <tbody>
              ${s.boxes.map(b => `<tr><td style="text-align:center">${b.boxNo}</td><td style="text-align:right">${b.qty}</td></tr>`).join('')}
            </tbody>
          </table>
        </div>
      `).join('\n')

      const plHtml = `<!doctype html><html><head><meta charset="utf-8"><title>装箱单 - ${order.order_number || ''}</title><style>${style}</style></head><body>
            <div class="pl-header">
          <div>
            <div style="font-weight:700">${order.seller_name || ''}</div>
            <div>${order.seller_address || ''}</div>
            <div>${order.seller_phone || ''}</div>
          </div>
          <div style="text-align:right">
            <div class="pl-title">装箱单 / Packing List</div>
            <div>订单号: ${order.order_number || ''}</div>
            <div>日期: ${this.formatDate(order.order_date) || ''}</div>
          </div>
        </div>

        <div style="margin-bottom:8px"><strong>收货方：</strong>${order.customer_supplier || ''}</div>

        <div>
          <table aria-label="packing-summary">
            <thead><tr><th style="width:60px">#</th><th>描述</th><th style="width:100px">数量</th><th style="width:120px">每箱</th><th style="width:120px">箱数</th></tr></thead>
            <tbody>
              ${summaryRows || `<tr><td colspan="5">（无明细）</td></tr>`}
            </tbody>
          </table>
        </div>

        ${boxesHtml}

        <div style="margin-top:18px;font-size:12px;color:#666">备注: 请按装箱单核对货物件数与包装。</div>
      </body></html>`

      const w = window.open('', '_blank')
      if (!w) { window.print(); return }
      w.document.open()
      w.document.write(plHtml)
      w.document.close()
      w.focus()
      setTimeout(() => {
        try { w.print() } catch (e) { console.error('print error', e) }
        try { w.close() } catch (e) {}
      }, 300)
    },

    async deleteOrder(order) {
      if (!confirm('确定要删除此订单吗？')) return
      
      try {
        await orderApi.deleteOrder(order.id)
        this.orders = this.orders.filter(o => o.id !== order.id)
        if (this.selectedOrder && this.selectedOrder.id === order.id) this.selectedOrder = null
      } catch (error) {
        console.error('删除订单失败:', error)
        alert('删除订单失败: ' + (error.response?.data?.message || error.message))
      }
    },

    resetPacking(item) {
      // 重置为自动分箱
      this.$delete(item, 'packing');
    },

    addBox(item) {
      // 添加新箱子
      if (!item.packing) {
        item.packing = [];
      }
      item.packing.push({ quantity: item.units_per_box || 1 });
    },

    removeBox(item, index) {
      // 删除箱子
      if (item.packing && item.packing.length > index) {
        item.packing.splice(index, 1);
        // 如果没有箱子了，删除packing属性
        if (item.packing.length === 0) {
          item.packing = [];
        }
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
  font-size: 2rem;
}

.page-header p {
  color: var(--secondary-color);
  margin-bottom: 0;
  font-size: 1.1rem;
}

.section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
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

/* 订单类型和状态标签 */
.order-type,
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  text-align: center;
}

.order-type.type-purchase {
  background-color: var(--info-color);
  color: white;
}

.order-type.type-sale {
  background-color: var(--success-color);
  color: white;
}

.status-badge.status-pending {
  background-color: var(--warning-color);
  color: white;
}

.status-badge.status-processing {
  background-color: var(--info-color);
  color: white;
}

.status-badge.status-completed {
  background-color: var(--success-color);
  color: white;
}

.order-number {
  font-weight: 600;
  color: var(--primary-color);
}

.amount {
  font-weight: 600;
  color: var(--success-color);
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
  border-radius: 8px;
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
  padding: 20px;
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
  padding: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.form-group label {
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--dark-color);
}

.form-group input,
.form-group select {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.95rem;
}

.form-group input:focus,
.form-group select:focus {
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

.order-item {
  margin-bottom: 15px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.item-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
  padding: 8px;
  border: 1px solid #eee;
  border-radius: 4px;
  flex-wrap: wrap;
}

.order-items {
  margin-bottom: 16px;
}

.item-controls {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.product-search {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

.product-search:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
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
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.product-option {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}

.product-option:hover {
  background-color: #f5f5f5;
}

.product-option:last-child {
  border-bottom: none;
}

/* 订单明细表格样式 */
.order-items-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}
.order-items-table th,
.order-items-table td {
  border: 1px solid #e6e6e6;
  padding: 8px 10px;
  text-align: left;
  vertical-align: middle;
}
.order-items-table thead th {
  background: #f7f7f7;
  font-weight: 600;
}
.order-items-table input {
  width: 100%;
  box-sizing: border-box;
  padding: 6px 8px;
}

.item-product {
  flex: 1;
  min-width: 150px;
  padding: 8px;
}

.item-description {
  flex: 2;
  min-width: 150px;
  padding: 8px;
}

.item-quantity,
.item-price,
.item-per-box {
  padding: 8px;
  min-width: 80px;
}

.item-quantity {
  width: 100px;
}

.item-price {
  width: 100px;
}

.item-per-box {
  width: 100px;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .data-table {
    min-width: auto;
  }
  
  .data-table th,
  .data-table td {
    padding: 8px 10px;
    font-size: 0.9rem;
  }
  
  .modal-content {
    margin: 10px;
    max-width: calc(100% - 20px);
  }
  
  .modal-body {
    padding: 16px;
  }
  
  .item-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .product-selector,
  .item-description,
  .item-quantity,
  .item-price,
  .item-per-box {
    min-width: auto;
    width: 100%;
  }
}

/* 产品搜索下拉样式 */
.item-controls {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.product-search {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

.product-search:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
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
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.product-option {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}

.product-option:hover {
  background-color: #f5f5f5;
}

.product-option:last-child {
  border-bottom: none;
}

/* 发票样式 */
.invoice {
  font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
  color: #222;
}

/* 装箱单编辑样式 */
.packing-edit-section {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.packing-item {
  margin-bottom: 15px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: white;
}

.packing-item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.packing-auto {
  color: #666;
  font-style: italic;
  padding: 10px 0;
}

.packing-boxes {
  margin-top: 10px;
}

.packing-box-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.box-quantity-input {
  width: 80px;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 3px;
}
.invoice-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
.invoice-header .seller h4 {
  margin: 0 0 6px;
}
.invoice-meta div {
  margin-bottom: 6px;
}
.bill-to {
  margin: 12px 0 18px;
}
.invoice-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12px;
}
.invoice-table th,
.invoice-table td {
  border: 1px solid #e6e6e6;
  padding: 8px 10px;
  text-align: left;
}
.invoice-table thead th {
  background: #f7f7f7;
}
.invoice-table tfoot td {
  border-top: 2px solid #ddd;
}
.text-right { text-align: right }
.grand-total td { background: #fafafa; font-size: 1.05rem }
.invoice-foot { margin-top: 18px; display:flex; justify-content:space-between }
.signatures div { margin-top: 10px }

/* 打印相关 */
@media print {
  /* 隐藏页面上不需要打印的 UI 元素 */
  body * { visibility: hidden }
  /* 不在 scoped 规则中显示原始 overlay，使用克隆容器打印 */
  .invoice-overlay { display: none !important }
  /* 隐藏 modal 的关闭按钮和其他非内容控件 */
  .modal-close, .btn-secondary, .btn-sm, .filters, .section-header button { display: none !important }
  .invoice-content { box-shadow: none !important }
}
</style>

<!-- 全局打印规则：确保打印时只输出发票内容 -->
<style>
@media print {
  /* 隐藏页面上不需要打印的 UI 元素（使用 visibility 更可靠） */
  html, body { height: 100%; }
  body * { visibility: hidden !important; }

  /* 隐藏原始 overlay（我们打印克隆的 .print-invoice） */
  .invoice-overlay { display: none !important; }
  /* 确保打印克隆容器可见 */
  .print-invoice, .print-invoice * { visibility: visible !important; display: block !important }

  /* 让发票内容固定占满页面并可分页 */
  .invoice-overlay {
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    width: 100% !important;
    height: 100% !important;
    visibility: visible !important;
    background: white !important;
    z-index: 9999 !important;
  }

  /* 隐藏操作按钮和其他非内容控件 */
  .modal-close, .btn-secondary, .btn-sm, .filters, .section-header button { display: none !important; }

  /* 去掉阴影和边框，使打印更清晰 */
  .invoice-content { box-shadow: none !important; background: white !important; }

  /* 确保表格在打印时不会被截断太短 */
  .invoice-table th, .invoice-table td { page-break-inside: avoid }
}
</style>