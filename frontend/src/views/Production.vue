<template>
  <div class="container">
    <div class="production-page">
      <!-- BOM物料计算器 -->
      <div class="section">
        <div class="section-header">
          <h3>BOM物料计算器</h3>
          <div class="calculator-actions">
            <button class="btn btn-secondary" @click="resetCalculator">
              <i class="icon">🔄</i> 重置
            </button>
          </div>
        </div>
        
        <div class="calculator-form">
          <div class="form-row">
            <div class="form-group">
              <label>选择产品</label>
              <select 
                v-model="selectedProduct" 
                @change="onProductSelect"
                class="product-select"
              >
                <option value="">请选择产品</option>
                <option v-for="product in products" :key="product.id" :value="product">
                  {{ product.name }} ({{ product.sku }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>生产数量</label>
              <div class="quantity-input-group">
                <input 
                  type="number" 
                  v-model.number="productionQuantity" 
                  min="1"
                  placeholder="输入生产数量"
                  class="quantity-input"
                  @input="calculateMaterialRequirements"
                >
                <span v-if="selectedProduct" class="quantity-unit">{{ selectedProduct.unit }}</span>
              </div>
            </div>
          </div>

          <!-- BOM信息显示 -->
          <div v-if="selectedProduct && bomItems && bomItems.length > 0" class="bom-info">
            <div class="bom-header">
              <h4>{{ selectedProduct.name }} 的BOM清单</h4>
              <div class="bom-header-actions">
                <div class="total-cost">
                  预估物料成本: <span class="cost-value">¥{{ totalMaterialCost.toFixed(2) }}</span>
                </div>
                <button class="btn btn-secondary" @click="printMaterialRequirements">
                  <i class="icon">🖨️</i> 打印
                </button>
              </div>
            </div>
            
            <div class="material-requirements">
              <h5>物料需求计算</h5>
              <div class="requirements-grid">
                <div 
                  v-for="(item, index) in materialRequirements" 
                  :key="item.id || item.material_id || index" 
                  class="requirement-item"
                >
                  <div class="material-info">
                    <div class="material-name">{{ item.material_name || item.materialName || '未知物料' }}</div>
                    <div class="material-sku">SKU: {{ item.material_sku || item.materialSku || '未知SKU' }}</div>
                  </div>
                  
                  <div class="requirement-details">
                    <div class="detail-row">
                      <span class="label">单位用量:</span>
                      <span class="value">{{ (item.quantity_required !== undefined ? item.quantity_required : item.quantityRequired || 0).toFixed(2) }} {{ item.unit || item.material_unit || '个' }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">需求数量:</span>
                      <span class="value requirement-quantity">
                        {{ typeof item.required_quantity_display !== 'undefined' ? item.required_quantity_display : (item.required_quantity || 0).toFixed(2) }}
                        {{ typeof item.required_unit_display !== 'undefined' ? item.required_unit_display : (item.unit || item.material_unit || '个') }}
                      </span>
                    </div>
                    <div class="detail-row">
                      <span class="label">当前库存:</span>
                      <span :class="['value', getStockStatusClass(item)]">
                        {{ (item.current_stock !== undefined ? item.current_stock : item.currentStock || 0).toFixed(2) }} {{ item.unit || item.material_unit || '个' }}
                      </span>
                    </div>
                    <div class="detail-row">
                      <span class="label">物料单价:</span>
                      <span class="value">¥{{ parseFloat(item.material_price !== undefined ? item.material_price : item.materialPrice || 0).toFixed(4) }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">需求成本:</span>
                      <span class="value cost">¥{{ parseFloat(item.required_cost !== undefined ? item.required_cost : item.requiredCost || 0).toFixed(4) }}</span>
                    </div>
                  </div>
                  
                  <div class="stock-status">
                    <div :class="['status-indicator', getRequirementStatus(item)]">
                      {{ getRequirementStatusText(item) }}
                    </div>
                    <div v-if="(item.shortage || 0) > 0" class="shortage-amount">
                      缺货: {{ typeof item.shortage_display !== 'undefined' ? item.shortage_display : (item.shortage || 0).toFixed(2) }}
                      {{ typeof item.shortage_unit !== 'undefined' ? item.shortage_unit : (item.unit || '个') }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div v-else-if="selectedProduct" class="no-bom-info">
            <div class="empty-state">
              <i class="empty-icon">📋</i>
              <h4>暂无BOM信息</h4>
              <p>该产品还没有设置物料清单(BOM)</p>
              <button class="btn btn-primary" @click="goToBOM">
                <i class="icon">⚙️</i> 去设置BOM
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 生产计划 -->
      <div class="section">
        <div class="section-header">
          <h3>生产计划</h3>
          <button class="btn btn-primary" @click="showCreatePlanModal = true">
            <i class="icon">➕</i> 新建生产计划
          </button>
        </div>
        
        <div class="production-plans">
          <!-- 空状态 -->
          <div v-if="productionPlans.length === 0" class="empty-state">
            <i class="empty-icon">🏭</i>
            <h4>暂无生产计划</h4>
            <p>还没有创建任何生产计划</p>
            <button class="btn btn-primary" @click="showCreatePlanModal = true">
              创建第一个生产计划
            </button>
          </div>
          
          <!-- 生产计划列表 -->
          <div v-else class="plans-grid">
            <div 
              v-for="plan in productionPlans" 
              :key="plan.id" 
              :class="['plan-card', `status-${plan.status}`]"
            >
              <div class="plan-header">
                <div class="plan-title">
                  <h4>{{ plan.product_name }}</h4>
                  <span class="plan-id">计划号: {{ plan.plan_number }}</span>
                </div>
                <div :class="['plan-status', `status-${plan.status}`]">
                  {{ getStatusText(plan.status) }}
                </div>
              </div>
              
              <div class="plan-details">
                <div class="detail-item">
                  <span class="label">计划数量:</span>
                  <span class="value">{{ plan.quantity }} {{ plan.unit }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">开始日期:</span>
                  <span class="value">{{ formatDate(plan.start_date) }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">完成日期:</span>
                  <span class="value">{{ formatDate(plan.end_date) }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">负责人:</span>
                  <span class="value">{{ plan.manager }}</span>
                </div>
              </div>
              
              <div class="plan-progress">
                <div class="progress-info">
                  <span class="progress-label">完成进度</span>
                  <span class="progress-value">{{ plan.progress }}%</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: plan.progress + '%' }"></div>
                </div>
              </div>
              
              <div class="plan-actions">
                <button class="btn btn-sm btn-info" @click="viewPlanDetails(plan)">
                  <i class="icon">👁️</i> 详情
                </button>
                <button class="btn btn-sm btn-warning" @click="editPlan(plan)">
                  <i class="icon">✏️</i> 编辑
                </button>
                <button class="btn btn-sm btn-danger" @click="deletePlan(plan.id)">
                  <i class="icon">🗑️</i> 删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 新建生产计划模态框 -->
      <div class="modal-overlay" v-if="showCreatePlanModal" @click="showCreatePlanModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>新建生产计划</h3>
            <button class="modal-close" @click="showCreatePlanModal = false">×</button>
          </div>
          
          <div class="modal-body">
            <form @submit.prevent="createProductionPlan">
              <div class="form-grid">
                <div class="form-group">
                  <label>选择产品 *</label>
                  <select 
                    v-model="newPlan.product_id" 
                    @change="onProductSelectForPlan" 
                    required
                  >
                    <option value="">请选择产品</option>
                    <option v-for="product in products" :key="product.id" :value="product.id">
                      {{ product.name }} ({{ product.sku }})
                    </option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label>计划数量 *</label>
                  <input 
                    type="number" 
                    v-model.number="newPlan.quantity" 
                    min="1" 
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label>开始日期 *</label>
                  <input 
                    type="date" 
                    v-model="newPlan.start_date" 
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label>完成日期 *</label>
                  <input 
                    type="date" 
                    v-model="newPlan.end_date" 
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label>负责人</label>
                  <input 
                    type="text" 
                    v-model="newPlan.manager" 
                    placeholder="输入负责人姓名"
                  >
                </div>
                
                <div class="form-group full-width">
                  <label>计划说明</label>
                  <textarea 
                    v-model="newPlan.description" 
                    placeholder="输入生产计划说明（可选）" 
                    rows="3"
                  ></textarea>
                </div>
              </div>
              
              <!-- 物料需求预览 -->
              <div v-if="planMaterialRequirements && planMaterialRequirements.length > 0" class="material-preview">
                <h4>物料需求预览</h4>
                <div class="preview-list">
                  <div 
                    v-for="item in planMaterialRequirements" 
                    :key="item.id || item.material_id" 
                    class="preview-item"
                  >
                    <span class="material-name">{{ item.material_name || item.name }}</span>
                    <span class="required-quantity">
                      {{ formatQuantity((item.quantity_required || 0) * (newPlan.quantity || 0)) }}
                      {{ item.unit || item.material_unit || '个' }}
                    </span>
                    <span 
                      class="stock-status" 
                      :class="getStockStatusClass(item)"
                    >
                      {{ getStockStatusText(item) }}
                    </span>
                  </div>
                </div>
              </div>
              <div v-else-if="newPlan.product_id && planMaterialRequirements.length === 0" class="material-preview">
                <h4>物料需求预览</h4>
                <p class="no-materials">该产品暂无物料需求信息</p>
              </div>
              
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="showCreatePlanModal = false">
                  取消
                </button>
                <button type="submit" class="btn btn-primary">创建计划</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- 查看生产计划详情模态框 -->
      <div class="modal-overlay" v-if="showPlanDetailModal" @click="showPlanDetailModal = false">
        <div class="modal-content large" @click.stop>
          <div class="modal-header">
            <h3>生产计划详情 - {{ selectedPlan?.plan_number }}</h3>
            <button class="modal-close" @click="showPlanDetailModal = false">×</button>
          </div>
          <div class="modal-body" v-if="selectedPlan">
            <div class="plan-detail-section">
              <h4>基本信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>产品名称:</label>
                  <span>{{ selectedPlan.product_name }}</span>
                </div>
                <div class="detail-item">
                  <label>产品SKU:</label>
                  <span>{{ selectedPlan.product_sku }}</span>
                </div>
                <div class="detail-item">
                  <label>计划数量:</label>
                  <span>{{ selectedPlan.quantity }} {{ selectedPlan.unit }}</span>
                </div>
                <div class="detail-item">
                  <label>已完成数量:</label>
                  <span>{{ selectedPlan.produced_quantity || 0 }} {{ selectedPlan.unit }}</span>
                </div>
                <div class="detail-item">
                  <label>开始日期:</label>
                  <span>{{ formatDate(selectedPlan.start_date) }}</span>
                </div>
                <div class="detail-item">
                  <label>完成日期:</label>
                  <span>{{ formatDate(selectedPlan.end_date) }}</span>
                </div>
                <div class="detail-item">
                  <label>负责人:</label>
                  <span>{{ selectedPlan.manager }}</span>
                </div>
                <div class="detail-item">
                  <label>状态:</label>
                  <span>{{ getStatusText(selectedPlan.status) }}</span>
                </div>
              </div>
            </div>
            
            <div class="plan-detail-section" v-if="selectedPlan.description || selectedPlan.notes">
              <h4>备注说明</h4>
              <div class="detail-notes">
                {{ selectedPlan.description || selectedPlan.notes }}
              </div>
            </div>
            
            <div class="plan-detail-section">
              <h4>进度信息</h4>
              <div class="progress-info">
                <div class="progress-bar-container">
                  <div class="progress-label">完成进度</div>
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: (selectedPlan.progress || 0) + '%' }"
                    ></div>
                  </div>
                  <div class="progress-percent">{{ selectedPlan.progress || 0 }}%</div>
                </div>
                
                <div class="progress-update">
                  <label>已完成数量:</label>
                  <div class="quantity-update">
                    <input 
                      type="number" 
                      v-model.number="selectedPlan.produced_quantity" 
                      min="0" 
                      :max="selectedPlan.quantity"
                      class="quantity-input"
                    >
                    <span class="unit">{{ selectedPlan.unit }}</span>
                    <button 
                      @click="updateProductionProgress(selectedPlan.id, selectedPlan.produced_quantity || 0)" 
                      class="btn btn-primary btn-sm"
                    >
                      更新
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showPlanDetailModal = false">关闭</button>
          </div>
        </div>
      </div>
      
      <!-- 编辑生产计划模态框 -->
      <div class="modal-overlay" v-if="showEditPlanModal" @click="showEditPlanModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>编辑生产计划 - {{ selectedPlan?.plan_number }}</h3>
            <button class="modal-close" @click="showEditPlanModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateProductionPlan">
              <div class="form-grid">
                <div class="form-group">
                  <label>产品</label>
                  <input 
                    type="text" 
                    :value="selectedPlan?.product_name" 
                    disabled
                  >
                </div>
                
                <div class="form-group">
                  <label>计划数量 *</label>
                  <input 
                    type="number" 
                    v-model.number="newPlan.quantity" 
                    min="1" 
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label>开始日期 *</label>
                  <input 
                    type="date" 
                    v-model="newPlan.start_date" 
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label>完成日期 *</label>
                  <input 
                    type="date" 
                    v-model="newPlan.end_date" 
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label>负责人</label>
                  <input 
                    type="text" 
                    v-model="newPlan.manager" 
                    placeholder="输入负责人姓名"
                  >
                </div>
                
                <div class="form-group full-width">
                  <label>备注说明</label>
                  <textarea 
                    v-model="newPlan.description" 
                    placeholder="输入计划备注说明"
                    rows="3"
                  ></textarea>
                </div>
              </div>
              
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="showEditPlanModal = false">
                  取消
                </button>
                <button type="submit" class="btn btn-primary">更新计划</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { productApi, productionApi } from '@/services/api'

export default {
  name: 'Production',
  data() {
    return {
      products: [],
      selectedProduct: null,
      productionQuantity: 100,
      bomItems: [],
      materialRequirements: [],
      productionPlans: [],
      showCreatePlanModal: false,
      showPlanDetailModal: false,
      showEditPlanModal: false,
      selectedPlan: null,
      newPlan: {
        product_id: '',
        product_name: '',
        quantity: 100,
        start_date: this.getTodayDate(),
        end_date: this.getNextWeekDate(),
        manager: '',
        description: ''
      },
      planMaterialRequirements: [] // 确保初始化为数组
    }
  },
  computed: {
    totalMaterialCost() {
      if (!this.materialRequirements || this.materialRequirements.length === 0) {
        return 0;
      }
      
      return this.materialRequirements.reduce((sum, item) => {
        const cost = item.required_cost !== undefined ? item.required_cost : item.requiredCost || 0;
        return sum + cost;
      }, 0);
    }
  },
  mounted() {
    console.log('🏭 Production组件已加载')
    this.loadProducts()
    this.loadProductionPlans()
  },
  methods: {
    async loadProducts() {
      try {
        const response = await productApi.getProducts()
        if (response.success) {
          this.products = response.data || []
        } else {
          console.error('获取产品数据失败:', response.message)
          this.products = []
        }
      } catch (error) {
        console.error('获取产品数据出错:', error)
        this.products = []
      }
    },
    
    async loadProductionPlans() {
      try {
        const response = await productionApi.getProductionPlans()
        if (response.success) {
          this.productionPlans = response.data.map(plan => ({
            ...plan,
            plan_number: plan.id ? `PP-${new Date(plan.created_at || new Date()).getFullYear()}${String(plan.id).padStart(4, '0')}` : `PP-${new Date().getFullYear()}0000`,
            start_date: plan.scheduled_date || plan.start_date,
            end_date: plan.end_date || plan.scheduled_date,
            manager: plan.manager || '',
            description: plan.description || plan.notes || '',
            unit: plan.unit || '个',
            progress: plan.quantity > 0 ? Math.round((plan.produced_quantity || 0) / plan.quantity * 100) : 0
          }))
        } else {
          console.error('获取生产计划失败:', response.message)
          this.productionPlans = []
        }
      } catch (error) {
        console.error('加载生产计划失败:', error)
        this.productionPlans = []
      }
    },

    async loadProductBOM() {
      if (!this.selectedProduct) {
        this.bomItems = []
        this.materialRequirements = []
        return
      }
      
      try {
        // 添加expand=true参数以获取展开的BOM信息（包含原材料）
        // 如果需要考虑快递费用，可以添加shipping_cost参数
        let apiUrl = `/api/bom?product_id=${this.selectedProduct.id}&expand=true`;
        
        // 如果有采购订单且包含快递费用，可以在这里添加
        // 这里暂时使用0作为默认值，实际应用中应该从采购订单中获取
        const shippingCost = 0;
        if (shippingCost > 0) {
          apiUrl += `&shipping_cost=${shippingCost}`;
        }
        
        const response = await fetch(apiUrl)
        if (response.ok) {
          const data = await response.json()
          console.log('获取到的展开BOM数据:', data) // 调试信息
          // 正确处理API返回的数据格式
          // API返回格式: { items: [...], total_cost: 0 }
          this.bomItems = data.items || []
          console.log('处理后的bomItems:', this.bomItems) // 调试信息
          this.calculateMaterialRequirements()
        } else {
          console.error('获取BOM数据失败:', response.status)
          this.bomItems = []
        }
      } catch (error) {
        console.error('获取BOM数据出错:', error)
        this.bomItems = []
      }
    },

    calculateMaterialRequirements() {
      console.log('开始计算物料需求:', {
        selectedProduct: this.selectedProduct,
        bomItems: this.bomItems,
        productionQuantity: this.productionQuantity
      });
      
      if (!this.selectedProduct || !this.bomItems || this.bomItems.length === 0) {
        this.materialRequirements = []
        console.log('没有BOM项目，清空物料需求')
        return
      }

      // 即使生产数量为0或未设置，也应进行计算（默认为0）
      const quantity = this.productionQuantity || 0

      this.materialRequirements = this.bomItems.map(item => {
        console.log('处理BOM项目:', item); // 调试信息
        
        // 确保使用正确的字段名
        const quantityRequired = item.quantity_required !== undefined ? item.quantity_required : item.quantityRequired || 0;
        const materialPrice = item.material_price !== undefined ? item.material_price : item.materialPrice || 0;
        const currentStock = item.current_stock !== undefined ? item.current_stock : item.currentStock || 0;
        const unit = item.unit || '个';
        
        const requiredQuantity = quantityRequired * quantity
        const requiredCost = requiredQuantity * materialPrice
        const shortage = Math.max(0, requiredQuantity - currentStock)
        
        // 转换为大单位显示
        const { displayQuantity, displayUnit } = this.convertToLargerUnit(requiredQuantity, unit)
        const { displayQuantity: displayShortage, displayUnit: shortageUnit } = this.convertToLargerUnit(shortage, unit)

        const result = {
          ...item,
          quantity_required: quantityRequired,
          material_price: materialPrice,
          current_stock: currentStock,
          unit: unit,
          required_quantity: requiredQuantity,
          required_quantity_display: displayQuantity,
          required_unit_display: displayUnit,
          required_cost: requiredCost,
          shortage: shortage,
          shortage_display: displayShortage,
          shortage_unit: shortageUnit
        }
        
        console.log('处理后的物料需求项:', result); // 调试信息
        return result
      })
      
      console.log('最终物料需求:', this.materialRequirements); // 调试信息
    },
    
    // 转换为大单位显示
    convertToLargerUnit(quantity, unit) {
      console.log('单位转换:', { quantity, unit }); // 简化调试信息
      
      // 定义单位换算关系（小单位到大单位）
      const unitConversions = {
        // 重量单位换算
        'mg': { larger: 'g', factor: 1000 },
        'g': { larger: 'kg', factor: 1000 },
        
        // 体积单位换算
        'ml': { larger: 'l', factor: 1000 },
        
        // 数量单位换算
        '个': { larger: '包', factor: 10 },
        '件': { larger: '箱', factor: 12 }
      }
      
      // 如果有定义转换关系且数量大于转换因子，则转换为大单位
      if (unitConversions[unit] && Math.abs(quantity) >= unitConversions[unit].factor) {
        const conversion = unitConversions[unit]
        const convertedQuantity = quantity / conversion.factor
        const result = {
          displayQuantity: parseFloat(convertedQuantity.toFixed(2)), // 四舍五入保留2位小数
          displayUnit: conversion.larger
        }
        console.log('单位转换结果(大单位):', result); // 调试信息
        return result
      }
      
      // 否则使用原始单位，四舍五入保留2位小数
      const result = {
        displayQuantity: parseFloat(quantity.toFixed(2)), // 四舍五入保留2位小数
        displayUnit: unit
      }
      console.log('单位转换结果(原始单位):', result); // 调试信息
      return result
    },

    getRequirementStatus(item) {
      // 确保item对象存在
      if (!item) {
        return ''
      }
      
      const currentStock = item.current_stock !== undefined ? item.current_stock : item.currentStock || 0;
      const requiredQuantity = item.required_quantity !== undefined ? item.required_quantity : item.quantity_required || item.quantityRequired || 0;
      
      if (currentStock === 0) {
        return 'out-of-stock'
      } else if (requiredQuantity > currentStock) {
        return 'insufficient'
      } else {
        return 'sufficient'
      }
    },

    getRequirementStatusText(item) {
      // 确保item对象存在
      if (!item) {
        return '未知'
      }
      
      const currentStock = item.current_stock !== undefined ? item.current_stock : item.currentStock || 0;
      const requiredQuantity = item.required_quantity !== undefined ? item.required_quantity : item.quantity_required || item.quantityRequired || 0;
      
      if (currentStock === 0) {
        return '缺货'
      } else if (requiredQuantity > currentStock) {
        return '库存不足'
      } else {
        return '库存充足'
      }
    },

    getStockStatusClass(item) {
      // 确保item对象存在
      if (!item) {
        return ''
      }
      
      const currentStock = item.current_stock !== undefined ? item.current_stock : item.currentStock || 0;
      const requiredQuantity = item.required_quantity !== undefined ? item.required_quantity : item.quantity_required || item.quantityRequired || 0;
      
      if (currentStock === 0) {
        return 'stock-out-of-stock'
      } else if (requiredQuantity > currentStock) {
        return 'stock-insufficient'
      } else {
        return 'stock-sufficient'
      }
    },

    getStockStatusText(item) {
      // 确保item对象存在
      if (!item) {
        return '未知'
      }
      
      const requiredQuantity = (item.quantity_required || 0) * (this.newPlan.quantity || 0);
      const currentStock = item.current_stock !== undefined ? item.current_stock : 0;
      
      if (currentStock === 0) {
        return '缺货'
      } else if (requiredQuantity > currentStock) {
        return '库存不足'
      } else {
        return '库存充足'
      }
    },

    resetCalculator() {
      this.selectedProduct = null
      this.productionQuantity = 100
      this.bomItems = []
      this.materialRequirements = []
    },

    goToBOM() {
      this.$router.push('/bom')
    },

    onProductSelect() {
      console.log('选择的产品:', this.selectedProduct); // 调试信息
      if (this.selectedProduct && this.selectedProduct.id) {
        this.loadProductBOM();
      } else {
        this.selectedProduct = null;
        this.bomItems = [];
        this.materialRequirements = [];
      }
    },

    async onProductSelectForPlan() {
      const selectedProduct = this.products.find(p => p.id == this.newPlan.product_id)
      if (selectedProduct) {
        this.newPlan.product_name = selectedProduct.name
        this.newPlan.unit = selectedProduct.unit
        
        // 加载产品的BOM物料需求，使用expand=true参数展开组合产品结构
        try {
          const response = await fetch(`/api/bom?product_id=${selectedProduct.id}&expand=true`)
          if (response.ok) {
            const data = await response.json()
            console.log('获取到的BOM数据:', data) // 调试信息
            this.planMaterialRequirements = data.items || []
          } else {
            console.error('获取产品BOM失败:', response.status)
            this.planMaterialRequirements = []
          }
        } catch (error) {
          console.error('获取产品BOM出错:', error)
          this.planMaterialRequirements = []
        }
      } else {
        this.newPlan.product_name = ''
        this.planMaterialRequirements = []
      }
    },

    async createProductionPlan() {
      if (!this.newPlan.product_id) {
        alert('请选择产品')
        return
      }
      
      try {
        const planData = {
          product_id: this.newPlan.product_id,
          quantity: this.newPlan.quantity,
          scheduled_date: this.newPlan.start_date,
          notes: this.newPlan.description
        }
      
        const response = await productionApi.createProductionPlan(planData)
      
        // 将新计划添加到列表中
        this.productionPlans.unshift({
          ...response.data || response,
          plan_number: response.id ? `PP-${new Date().getFullYear()}${String(response.id).padStart(4, '0')}` : `PP-${new Date().getFullYear()}0000`,
          product_name: this.newPlan.product_name,
          unit: this.products.find(p => p.id == this.newPlan.product_id)?.unit || '个',
          start_date: this.newPlan.start_date,
          end_date: this.newPlan.end_date,
          manager: this.newPlan.manager,
          status: 'pending',
          progress: 0,
          description: this.newPlan.description
        })
      
        this.showCreatePlanModal = false
        this.resetNewPlan()
      } catch (error) {
        console.error('创建生产计划出错:', error)
        alert(`创建生产计划时发生错误: ${error.message || '未知错误'}`)
      }
    },

    viewPlanDetails(plan) {
      this.selectedPlan = { 
        ...plan,
        progress: plan.quantity > 0 ? Math.round((plan.produced_quantity || 0) / plan.quantity * 100) : 0
      };
      this.showPlanDetailModal = true;
    },

    editPlan(plan) {
      this.selectedPlan = { 
        ...plan,
        progress: plan.quantity > 0 ? Math.round((plan.produced_quantity || 0) / plan.quantity * 100) : 0
      };
      // 填充编辑表单数据
      this.newPlan = {
        ...plan,
        product_id: plan.product_id,
        product_name: plan.product_name,
        quantity: plan.quantity,
        start_date: plan.start_date || this.getTodayDate(),
        end_date: plan.end_date || this.getNextWeekDate(),
        manager: plan.manager,
        description: plan.description || plan.notes
      };
      this.showEditPlanModal = true;
    },

    async deletePlan(planId) {
      if (confirm('确定要删除这个生产计划吗？')) {
        try {
          await productionApi.deleteProductionPlan(planId)
          // 确保删除成功后再更新本地状态
          this.productionPlans = this.productionPlans.filter(plan => plan.id !== planId)
        } catch (error) {
          console.error('删除生产计划出错:', error)
          alert(`删除生产计划时发生错误: ${error.message || '未知错误'}`)
        }
      }
    },

    async updateProductionPlan() {
      if (!this.newPlan.product_id) {
        alert('请选择产品')
        return
      }
      
      try {
        const planData = {
          product_id: this.newPlan.product_id,
          quantity: this.newPlan.quantity,
          scheduled_date: this.newPlan.start_date,
          notes: this.newPlan.description
        }
        
        const response = await productionApi.updateProductionPlan(this.selectedPlan.id, planData)
        
        // 更新本地数据
        const planIndex = this.productionPlans.findIndex(p => p.id === this.selectedPlan.id)
        if (planIndex !== -1) {
          this.productionPlans[planIndex] = {
            ...this.productionPlans[planIndex],
            ...response,
            start_date: this.newPlan.start_date,
            end_date: this.newPlan.end_date,
            manager: this.newPlan.manager,
            description: this.newPlan.description
          }
        }
        
        this.showEditPlanModal = false
        this.selectedPlan = null
        alert('生产计划更新成功')
      } catch (error) {
        console.error('更新生产计划出错:', error)
        alert(`更新生产计划时发生错误: ${error.message || '未知错误'}`)
      }
    },

    async updateProductionProgress(planId, producedQuantity) {
      try {
        const planData = {
          produced_quantity: producedQuantity
        };

        const response = await productionApi.updateProductionPlan(planId, planData);
        
        // 更新本地数据
        const planIndex = this.productionPlans.findIndex(p => p.id === planId);
        if (planIndex !== -1) {
          this.productionPlans[planIndex] = {
            ...this.productionPlans[planIndex],
            ...response,
            progress: response.quantity > 0 ? Math.round((response.produced_quantity || 0) / response.quantity * 100) : 0
          };
        }
        
        // 如果正在查看或编辑该计划，也更新选中的计划数据
        if (this.selectedPlan && this.selectedPlan.id === planId) {
          this.selectedPlan = {
            ...this.selectedPlan,
            ...response,
            progress: response.quantity > 0 ? Math.round((response.produced_quantity || 0) / response.quantity * 100) : 0
          };
        }
        
        alert('生产进度更新成功');
      } catch (error) {
        console.error('更新生产进度出错:', error);
        alert(`更新生产进度时发生错误: ${error.message || '未知错误'}`);
      }
    },

    getStatusText(status) {
      const statusMap = {
        'planned': '计划中',
        'in_progress': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return statusMap[status] || status
    },

    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('zh-CN')
    },

    formatQuantity(quantity) {
      if (quantity === undefined || quantity === null || isNaN(quantity)) return '0.00';
      return parseFloat(quantity).toFixed(2);
    },

    getTodayDate() {
      return new Date().toISOString().split('T')[0]
    },

    getNextWeekDate() {
      const nextWeek = new Date()
      nextWeek.setDate(nextWeek.getDate() + 7)
      return nextWeek.toISOString().split('T')[0]
    },

    resetNewPlan() {
      this.newPlan = {
        product_id: '',
        product_name: '',
        quantity: 100,
        start_date: this.getTodayDate(),
        end_date: this.getNextWeekDate(),
        manager: '',
        description: ''
      }
      this.planMaterialRequirements = []
    },

    printMaterialRequirements() {
      if (!this.selectedProduct || this.materialRequirements.length === 0) {
        alert('没有可打印的数据');
        return;
      }

      // 添加调试信息
      console.log('打印数据:', {
        selectedProduct: this.selectedProduct,
        materialRequirements: this.materialRequirements,
        totalMaterialCost: this.totalMaterialCost,
        productionQuantity: this.productionQuantity
      });

      // 创建打印窗口
      const printWindow = window.open('', '_blank');
      const printContent = this.generatePrintContent();
      
      // 添加调试信息
      console.log('生成的打印内容:', printContent);
      
      // 使用单引号和字符串拼接替代模板字符串
      printWindow.document.write(
        '<!DOCTYPE html>' +
        '<html>' +
        '<head>' +
        '  <title>物料需求清单 - ' + this.selectedProduct.name + '</title>' +
        '  <style>' +
        '    body {' +
        '      font-family: Arial, sans-serif;' +
        '      margin: 20px;' +
        '      line-height: 1.6;' +
        '    }' +
        '    .header {' +
        '      text-align: center;' +
        '      border-bottom: 2px solid #333;' +
        '      padding-bottom: 10px;' +
        '      margin-bottom: 20px;' +
        '    }' +
        '    .product-info {' +
        '      display: flex;' +
        '      justify-content: space-between;' +
        '      margin-bottom: 20px;' +
        '    }' +
        '    .info-item {' +
        '      font-weight: bold;' +
        '    }' +
        '    table {' +
        '      width: 100%;' +
        '      border-collapse: collapse;' +
        '      margin-bottom: 20px;' +
        '    }' +
        '    th, td {' +
        '      border: 1px solid #ddd;' +
        '      padding: 12px;' +
        '      text-align: left;' +
        '    }' +
        '    th {' +
        '      background-color: #f2f2f2;' +
        '      font-weight: bold;' +
        '    }' +
        '    .text-right {' +
        '      text-align: right;' +
        '    }' +
        '    .total-row {' +
        '      font-weight: bold;' +
        '    }' +
        '    .footer {' +
        '      margin-top: 30px;' +
        '      text-align: right;' +
        '      font-style: italic;' +
        '    }' +
        '    @media print {' +
        '      body {' +
        '        margin: 0;' +
        '        padding: 20px;' +
        '      }' +
        '    }' +
        '  </style>' +
        '</head>' +
        '<body>' +
        printContent +
        '  <sc' + 'ript>' +
        '    window.onload = function() {' +
        '      window.print();' +
        '      window.onafterprint = function() {' +
        '        window.close();' +
        '      }' +
        '    }' +
        '  </sc' + 'ript>' +
        '</body>' +
        '</html>'
      );
      
      printWindow.document.close();
    },

    generatePrintContent() {
      const product = this.selectedProduct;
      const quantity = this.productionQuantity;
      const requirements = this.materialRequirements;
      const totalCost = this.totalMaterialCost;

      let tableRows = '';
      let totalQuantity = 0;
      
      requirements.forEach(item => {
        const requiredQuantity = typeof item.required_quantity_display !== 'undefined' 
          ? item.required_quantity_display 
          : parseFloat(item.required_quantity || 0).toFixed(2);
        const requiredUnit = typeof item.required_unit_display !== 'undefined' 
          ? item.required_unit_display 
          : item.unit;
        const unitPrice = parseFloat(item.material_price || 0).toFixed(4);
        const requiredCost = parseFloat(item.required_cost || 0).toFixed(2); // 保留2位小数
        const currentStock = parseFloat(item.current_stock || 0).toFixed(2);
        
        // 累加需求数量（使用原始需求数量进行累加，确保总计正确）
        const rawQty = parseFloat(item.required_quantity || 0);
        totalQuantity += rawQty;

        tableRows += 
          '<tr>' +
          '  <td>' + item.material_name + '</td>' +
          '  <td>' + item.material_sku + '</td>' +
          '  <td class="text-right">' + parseFloat(item.quantity_required || 0).toFixed(2) + ' ' + item.unit + '</td>' +
          '  <td class="text-right">' + currentStock + ' ' + item.unit + '</td>' +
          '  <td class="text-right">¥' + unitPrice + '</td>' +
          '  <td class="text-right">¥' + requiredCost + '</td>' +
          '  <td class="text-right">' + requiredQuantity + ' ' + requiredUnit + '</td>' +
          '</tr>';
      });

      // 修复返回语句，确保正确返回拼接的字符串
      return '<div class="header">' +
        '  <h1>物料需求清单</h1>' +
        '</div>' +
        '<div class="product-info">' +
        '  <div class="info-item">产品名称: ' + product.name + '</div>' +
        '  <div class="info-item">产品SKU: ' + product.sku + '</div>' +
        '  <div class="info-item">生产数量: ' + quantity + ' ' + product.unit + '</div>' +
        '</div>' +
        '<table>' +
        '  <thead>' +
        '    <tr>' +
        '      <th>物料名称</th>' +
        '      <th>物料SKU</th>' +
        '      <th>单位用量</th>' +
        '      <th>当前库存</th>' +
        '      <th>物料单价</th>' +
        '      <th>需求成本</th>' +
        '      <th>需求数量</th>' +
        '    </tr>' +
        '  </thead>' +
        '  <tbody>' +
        tableRows +
        '    <tr class="total-row">' +
        '      <td>总计</td>' +
        '      <td colspan="4"></td>' +
        '      <td class="text-right">¥' + totalCost.toFixed(2) + '</td>' +
        '      <td class="text-right">' + (totalQuantity / 1000).toFixed(2) + ' l</td>' +
        '    </tr>' +
        '  </tbody>' +
        '</table>';
    }
  }
}
</script>

<style scoped>
.production-page {
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

.calculator-actions {
  display: flex;
  gap: 12px;
}

/* 计算器表单 */
.calculator-form {
  max-width: 100%;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--dark-color);
}

.product-select,
.quantity-input {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.product-select:focus,
.quantity-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.quantity-input-group {
  position: relative;
  display: flex;
}

.quantity-input {
  flex: 1;
  padding-right: 60px;
}

.quantity-unit {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary-color);
  font-size: 0.9rem;
}

/* BOM信息 */
.bom-info {
  margin-top: 30px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.bom-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--light-color);
  border-bottom: 1px solid var(--border-color);
}

.bom-header h4 {
  margin: 0;
  color: var(--dark-color);
}

.bom-header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.total-cost {
  font-weight: 600;
  color: var(--dark-color);
}

.cost-value {
  color: var(--success-color);
  font-size: 1.1rem;
}

.material-requirements {
  padding: 20px;
}

.material-requirements h5 {
  margin: 0 0 16px 0;
  color: var(--dark-color);
  font-size: 1.1rem;
}

.requirements-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.requirement-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.2s ease;
}

.requirement-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.material-info {
  flex: 1;
}

.material-name {
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--dark-color);
}

.material-sku {
  font-size: 0.85rem;
  color: var(--secondary-color);
}

.requirement-details {
  flex: 2;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-row .label {
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.detail-row .value {
  font-weight: 500;
}

.requirement-quantity {
  color: var(--primary-color);
  font-weight: 600;
}

.cost {
  color: var(--success-color);
  font-weight: 600;
}

.stock-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  min-width: 120px;
}

.status-indicator {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
  min-width: 80px;
}

.status-indicator.sufficient {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-indicator.insufficient {
  background: #fff3e0;
  color: #ef6c00;
}

.status-indicator.out-of-stock {
  background: #ffebee;
  color: #c62828;
}

.shortage-amount {
  font-size: 0.8rem;
  color: var(--danger-color);
  font-weight: 500;
}

/* 库存状态样式 */
.stock-sufficient {
  color: var(--success-color);
}

.stock-insufficient {
  color: var(--warning-color);
}

.stock-out-of-stock {
  color: var(--danger-color);
}

/* 空状态 */
.no-bom-info {
  text-align: center;
  padding: 40px 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h4 {
  margin-bottom: 8px;
  color: var(--dark-color);
}

.empty-state p {
  margin-bottom: 20px;
  color: var(--secondary-color);
}

/* 生产计划样式 */
.production-plans {
  min-height: 200px;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.plan-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.plan-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.plan-card.status-in_progress {
  border-left: 4px solid var(--info-color);
}

.plan-card.status-planned {
  border-left: 4px solid var(--warning-color);
}

.plan-card.status-completed {
  border-left: 4px solid var(--success-color);
}

.plan-card.status-cancelled {
  border-left: 4px solid var(--danger-color);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.plan-title h4 {
  margin: 0 0 4px 0;
  color: var(--dark-color);
}

.plan-id {
  font-size: 0.85rem;
  color: var(--secondary-color);
}

.plan-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.plan-status.status-in_progress {
  background: #e3f2fd;
  color: #1976d2;
}

.plan-status.status-planned {
  background: #fff3e0;
  color: #ef6c00;
}

.plan-status.status-completed {
  background: #e8f5e8;
  color: #2e7d32;
}

.plan-status.status-cancelled {
  background: #ffebee;
  color: #c62828;
}

.plan-details {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.detail-item .label {
  color: var(--secondary-color);
}

.detail-item .value {
  font-weight: 500;
  color: var(--dark-color);
}

.plan-progress {
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.progress-label {
  color: var(--secondary-color);
}

.progress-value {
  font-weight: 600;
  color: var(--primary-color);
}

.progress-bar {
  height: 6px;
  background: var(--light-color);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar .progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.plan-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
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
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--dark-color);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--secondary-color);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--light-color);
  color: var(--dark-color);
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--dark-color);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

/* 计划详情样式 */
.plan-detail-section {
  margin-bottom: 24px;
}

.plan-detail-section h4 {
  margin: 0 0 16px 0;
  color: var(--dark-color);
  font-size: 1.1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item label {
  font-weight: 500;
  color: var(--secondary-color);
  margin-bottom: 4px;
  font-size: 0.9rem;
}

.detail-item span {
  font-weight: 500;
  color: var(--dark-color);
}

.detail-notes {
  background: var(--light-color);
  padding: 16px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  white-space: pre-wrap;
  min-height: 60px;
}

/* 进度条容器 */
.progress-bar-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  height: 8px;
  background: var(--light-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar .progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-label {
  font-weight: 500;
  color: var(--secondary-color);
}

.progress-percent {
  font-weight: 600;
  color: var(--primary-color);
  text-align: right;
}

/* 物料需求预览 */
.material-preview {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.material-preview h4 {
  margin: 0 0 15px 0;
  color: var(--dark-color);
  font-size: 1rem;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.material-name {
  flex: 1;
  font-weight: 500;
}

.required-quantity {
  font-weight: 600;
  color: var(--primary-color);
}

.stock-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.stock-status.stock-ok {
  background: #e8f5e8;
  color: #2e7d32;
}

.stock-status.stock-low {
  background: #fff3e0;
  color: #ef6c00;
}

.stock-status.stock-out {
  background: #ffebee;
  color: #c62828;
}

.no-materials {
  text-align: center;
  color: var(--secondary-color);
  font-style: italic;
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .requirement-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .requirement-details {
    grid-template-columns: 1fr;
  }
  
  .stock-status {
    align-items: flex-start;
  }
  
  .plans-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .plan-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .plan-actions {
    justify-content: flex-start;
  }
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

@media print {
  .print-container {
    font-size: 8px !important; /* 减小字体 */
    line-height: 1.2 !important; /* 紧凑行距 */
  }
  
  .demand-item {
    margin-bottom: 2px !important; /* 减小间距 */
    padding: 2px !important;
  }
  
  .demand-number {
    font-size: 7px !important; /* 数字字体更小 */
    white-space: nowrap !important; /* 防止数字换行 */
  }
  
  .table th,
  .table td {
    font-size: 7px !important;
    padding: 0.2rem !important; /* 减小单元格内边距 */
  }
}
</style>
