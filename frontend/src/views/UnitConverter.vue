<template>
  <div class="container">
    <div class="unit-converter-page">
      <!-- 国际通用单位转换 -->
      <div class="section">
        <div class="section-header">
          <h3>国际通用单位转换</h3>
          <div class="converter-tabs">
            <button 
              v-for="category in unitCategories" 
              :key="category.id"
              :class="['tab-btn', { active: activeCategory === category.id }]"
              @click="switchCategory(category.id)"
            >
              {{ category.name }}
            </button>
          </div>
        </div>

        <div class="converter-container">
          <div class="converter-form">
            <div class="form-group">
              <label>数值:</label>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model="inputValue" 
                  @input="convertUnits" 
                  step="any" 
                  placeholder="输入数值"
                  class="value-input"
                >
                <span class="input-hint">支持小数输入</span>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>从单位:</label>
                <select v-model="fromUnit" @change="convertUnits" class="unit-select">
                  <option v-for="unit in getCurrentUnits()" :key="unit.value" :value="unit.value">
                    {{ unit.name }} ({{ unit.symbol }})
                  </option>
                </select>
              </div>

              <div class="swap-button">
                <button class="btn-swap" @click="swapUnits" title="交换单位">
                  <i class="icon">🔄</i>
                </button>
              </div>

              <div class="form-group">
                <label>转换为:</label>
                <select v-model="toUnit" @change="convertUnits" class="unit-select">
                  <option v-for="unit in getCurrentUnits()" :key="unit.value" :value="unit.value">
                    {{ unit.name }} ({{ unit.symbol }})
                  </option>
                </select>
              </div>
            </div>

            <div class="conversion-result">
              <label>转换结果:</label>
              <div class="result-value">
                <span class="result-number">{{ convertedValue }}</span>
                <span class="result-unit">{{ getUnitSymbol(toUnit) }}</span>
              </div>
              <div class="result-formula" v-if="conversionFormula">
                {{ conversionFormula }}
              </div>
            </div>
          </div>

          <div class="conversion-reference">
            <h4>常用转换参考</h4>
            <div class="reference-grid">
              <div class="reference-item" v-for="ref in getCurrentReferences()" :key="ref.id">
                <span class="ref-equation">{{ ref.equation }}</span>
                <span class="ref-value">≈ {{ ref.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 产品自定义单位转换 -->
      <div class="section">
        <div class="section-header">
          <h3>产品自定义单位转换</h3>
          <div class="actions">
            <select v-model="selectedProduct" @change="loadProductConversions" class="product-select">
              <option value="">选择产品</option>
              <option v-for="product in products" :key="product.id" :value="product">
                {{ product.sku }} - {{ product.name }}
              </option>
            </select>
            <button class="btn btn-primary" @click="openCustomModal">
              <i class="icon">➕</i> 添加转换规则
            </button>
          </div>
        </div>

        <div class="custom-converter">
          <div class="custom-converter-container" v-if="selectedProduct">
            <div class="converter-header">
              <h4>{{ selectedProduct.name }} 的单位转换</h4>
              <button class="btn btn-primary" @click="openCustomModal">
                <i class="icon">➕</i> 添加转换规则
              </button>
            </div>
            <div class="product-conversions">
              <div class="conversion-rules">
                <h4>转换规则</h4>
                <div v-if="productConversions.length > 0" class="rules-list">
                  <div v-for="rule in productConversions" :key="rule.id" class="rule-item">
                    <div class="rule-info">
                      <span class="rule-from">1 {{ rule.from_unit }}</span>
                      <span class="rule-equals">=</span>
                      <span class="rule-to">{{ rule.conversion_rate }} {{ rule.to_unit }}</span>
                    </div>
                    <div class="rule-actions">
                      <button class="btn-icon btn-edit" @click="editCustomRule(rule)" title="编辑">
                        <i class="icon">✏️</i>
                      </button>
                      <button class="btn-icon btn-delete" @click="deleteCustomRule(rule.id)" title="删除">
                        <i class="icon">🗑️</i>
                      </button>
                    </div>
                  </div>
                </div>
                <div v-else class="no-rules">
                  <p>该产品还没有设置自定义单位转换规则</p>
                  <button class="btn btn-primary" @click="openCustomModal">
                    添加转换规则
                  </button>
                </div>
              </div>

              <div class="custom-converter-form">
                <h4>自定义转换计算</h4>
                <div class="form-row">
                  <div class="form-group">
                    <label>数值:</label>
                    <input 
                      type="number" 
                      v-model="customInputValue" 
                      @input="convertCustomUnits" 
                      step="any" 
                      placeholder="输入数值"
                    >
                  </div>
                  <div class="form-group">
                    <label>从单位:</label>
                    <select v-model="customFromUnit" @change="convertCustomUnits" class="unit-select">
                      <option value="">选择单位</option>
                      <option v-for="unit in getProductUnits()" :key="unit" :value="unit">
                        {{ unit }}
                      </option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>转换为:</label>
                    <select v-model="customToUnit" @change="convertCustomUnits" class="unit-select">
                      <option value="">选择单位</option>
                      <option v-for="unit in getProductUnits()" :key="unit" :value="unit">
                        {{ unit }}
                      </option>
                    </select>
                  </div>
                </div>
              
                <div v-if="customConvertedValue !== null" class="custom-result">
                  <div class="result-value">
                    {{ customInputValue }} {{ customFromUnit }} = 
                    <strong>{{ customConvertedValue }} {{ customToUnit }}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="!selectedProduct" class="no-product-selected">
              <div class="empty-state">
                <i class="empty-icon">📦</i>
                <h4>请选择产品</h4>
                <p>选择产品后可以管理其自定义单位转换规则</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加自定义转换模态框 -->
      <div class="modal-overlay" v-if="showCustomModal" @click="showCustomModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ editingRule ? '编辑转换规则' : '添加自定义转换' }}</h3>
            <button class="modal-close" @click="closeCustomModal">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveCustomRule">
              <div class="form-grid">
                <div class="form-group">
                  <label>选择产品 *</label>
                  <select v-model="newRule.product_id" required :disabled="!!editingRule">
                    <option value="">请选择产品</option>
                    <option v-for="product in products" :key="product.id" :value="product.id">
                      {{ product.name }} ({{ product.sku }})
                    </option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label>源单位 *</label>
                  <input 
                    type="text" 
                    v-model="newRule.from_unit" 
                    required 
                    placeholder="例如: 箱"
                  >
                </div>
                
                <div class="form-group">
                  <label>目标单位 *</label>
                  <input 
                    type="text" 
                    v-model="newRule.to_unit" 
                    required 
                    placeholder="例如: 个"
                  >
                </div>
                
                <div class="form-group">
                  <label>转换率 *</label>
                  <input 
                    type="number" 
                    v-model.number="newRule.conversion_rate" 
                    step="any" 
                    min="0.0001" 
                    required 
                    placeholder="例如: 24"
                  >
                  <small class="form-hint">1个源单位 = ? 个目标单位</small>
                </div>
                
                <div class="form-group full-width">
                  <label>规则描述</label>
                  <textarea 
                    v-model="newRule.description" 
                    placeholder="输入转换规则的描述（可选）"
                    rows="2"
                  ></textarea>
                </div>
              </div>

              <div class="rule-preview" v-if="newRule.from_unit && newRule.to_unit && newRule.conversion_rate">
                <h4>规则预览</h4>
                <div class="preview-equation">
                  1 {{ newRule.from_unit }} = {{ newRule.conversion_rate }} {{ newRule.to_unit }}
                </div>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="closeCustomModal">取消</button>
                <button type="submit" class="btn btn-primary">
                  {{ editingRule ? '更新规则' : '添加规则' }}
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
export default {
  name: 'UnitConverter',
  data() {
    return {
      // 国际单位转换相关
      activeCategory: 'length',
      inputValue: 1,
      fromUnit: 'm',
      toUnit: 'cm',
      convertedValue: '100.00',
      conversionFormula: '',
      
      // 产品自定义转换相关
      selectedProduct: null,
      customInputValue: 1,
      customFromUnit: '',
      customToUnit: '',
      customConvertedValue: null,
      showCustomModal: false,
      editingRule: null,
      
      // 数据
      unitCategories: [
        { id: 'length', name: '长度', icon: '📏' },
        { id: 'weight', name: '重量', icon: '⚖️' },
        { id: 'volume', name: '体积', icon: '🧪' },
        { id: 'area', name: '面积', icon: '📐' },
        { id: 'temperature', name: '温度', icon: '🌡️' }
      ],
      
      units: {
        length: [
          { value: 'mm', name: '毫米', symbol: 'mm' },
          { value: 'cm', name: '厘米', symbol: 'cm' },
          { value: 'm', name: '米', symbol: 'm' },
          { value: 'km', name: '千米', symbol: 'km' },
          { value: 'in', name: '英寸', symbol: 'in' },
          { value: 'ft', name: '英尺', symbol: 'ft' },
          { value: 'yd', name: '码', symbol: 'yd' },
          { value: 'mi', name: '英里', symbol: 'mi' }
        ],
        weight: [
          { value: 'mg', name: '毫克', symbol: 'mg' },
          { value: 'g', name: '克', symbol: 'g' },
          { value: 'kg', name: '千克', symbol: 'kg' },
          { value: 't', name: '吨', symbol: 't' },
          { value: 'oz', name: '盎司', symbol: 'oz' },
          { value: 'lb', name: '磅', symbol: 'lb' }
        ],
        volume: [
          { value: 'ml', name: '毫升', symbol: 'ml' },
          { value: 'cl', name: '厘升', symbol: 'cl' },
          { value: 'l', name: '升', symbol: 'l' },
          { value: 'm3', name: '立方米', symbol: 'm³' },
          { value: 'floz', name: '液量盎司', symbol: 'fl oz' },
          { value: 'cup', name: '杯', symbol: 'cup' },
          { value: 'pt', name: '品脱', symbol: 'pt' },
          { value: 'gal', name: '加仑', symbol: 'gal' }
        ],
        area: [
          { value: 'mm2', name: '平方毫米', symbol: 'mm²' },
          { value: 'cm2', name: '平方厘米', symbol: 'cm²' },
          { value: 'm2', name: '平方米', symbol: 'm²' },
          { value: 'ha', name: '公顷', symbol: 'ha' },
          { value: 'km2', name: '平方公里', symbol: 'km²' },
          { value: 'in2', name: '平方英寸', symbol: 'in²' },
          { value: 'ft2', name: '平方英尺', symbol: 'ft²' },
          { value: 'ac', name: '英亩', symbol: 'ac' }
        ],
        temperature: [
          { value: 'c', name: '摄氏度', symbol: '°C' },
          { value: 'f', name: '华氏度', symbol: '°F' },
          { value: 'k', name: '开尔文', symbol: 'K' }
        ]
      },
      
      references: {
        length: [
          { id: 1, equation: '1 米 = 100 厘米', value: '100 cm' },
          { id: 2, equation: '1 千米 = 1000 米', value: '1000 m' },
          { id: 3, equation: '1 英寸 = 2.54 厘米', value: '2.54 cm' },
          { id: 4, equation: '1 英尺 = 30.48 厘米', value: '30.48 cm' },
          { id: 5, equation: '1 英里 = 1.609 千米', value: '1.609 km' }
        ],
        weight: [
          { id: 1, equation: '1 千克 = 1000 克', value: '1000 g' },
          { id: 2, equation: '1 吨 = 1000 千克', value: '1000 kg' },
          { id: 3, equation: '1 盎司 = 28.35 克', value: '28.35 g' },
          { id: 4, equation: '1 磅 = 453.59 克', value: '453.59 g' },
          { id: 5, equation: '1 磅 = 16 盎司', value: '16 oz' }
        ],
        volume: [
          { id: 1, equation: '1 升 = 1000 毫升', value: '1000 ml' },
          { id: 2, equation: '1 立方米 = 1000 升', value: '1000 L' },
          { id: 3, equation: '1 加仑 = 3.785 升', value: '3.785 L' },
          { id: 4, equation: '1 品脱 = 473.18 毫升', value: '473.18 ml' },
          { id: 5, equation: '1 杯 = 236.59 毫升', value: '236.59 ml' }
        ],
        area: [
          { id: 1, equation: '1 平方米 = 10000 平方厘米', value: '10000 cm²' },
          { id: 2, equation: '1 公顷 = 10000 平方米', value: '10000 m²' },
          { id: 3, equation: '1 平方公里 = 100 公顷', value: '100 ha' },
          { id: 4, equation: '1 英亩 = 4046.86 平方米', value: '4046.86 m²' },
          { id: 5, equation: '1 平方英尺 = 929.03 平方厘米', value: '929.03 cm²' }
        ],
        temperature: [
          { id: 1, equation: '°C 转 °F', value: '°F = °C × 1.8 + 32' },
          { id: 2, equation: '°F 转 °C', value: '°C = (°F - 32) ÷ 1.8' },
          { id: 3, equation: '°C 转 K', value: 'K = °C + 273.15' },
          { id: 4, equation: 'K 转 °C', value: '°C = K - 273.15' }
        ]
      },
      
      products: [],
      
      productConversions: [],
      customConversionRules: [],
      
      newRule: {
        product_id: '',
        from_unit: '',
        to_unit: '',
        conversion_rate: 1,
        description: ''
      }
    }
  },
  mounted() {
    console.log('📐 UnitConverter组件已加载')
    this.convertUnits()
    this.loadProducts()
  },
  methods: {
    // 加载产品数据
    async loadProducts() {
      try {
        const response = await fetch('/api/products')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const products = await response.json()
        this.products = products
      } catch (error) {
        console.error('加载产品数据失败:', error)
        // 出错时使用空数组
        this.products = []
      }
    },
    
    // 加载产品转换规则
    async loadProductConversions() {
      if (!this.selectedProduct) {
        this.productConversions = []
        return
      }
      
      try {
        const response = await fetch(`/api/products/${this.selectedProduct.id}/conversions`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const conversions = await response.json()
        this.productConversions = conversions
      } catch (error) {
        console.error('加载产品转换规则失败:', error)
        // 出错时使用空数组
        this.productConversions = []
      }
    },
    
    // 国际单位转换方法
    switchCategory(categoryId) {
      this.activeCategory = categoryId
      // 重置为默认单位
      const defaultUnits = this.getDefaultUnits(categoryId)
      this.fromUnit = defaultUnits.from
      this.toUnit = defaultUnits.to
      this.convertUnits()
    },
    
    getDefaultUnits(category) {
      const defaults = {
        length: { from: 'm', to: 'cm' },
        weight: { from: 'kg', to: 'g' },
        volume: { from: 'l', to: 'ml' },
        area: { from: 'm2', to: 'cm2' },
        temperature: { from: 'c', to: 'f' }
      }
      return defaults[category] || defaults.length
    },
    
    getCurrentUnits() {
      return this.units[this.activeCategory] || []
    },
    
    getCurrentReferences() {
      return this.references[this.activeCategory] || []
    },
    
    getUnitSymbol(unitValue) {
      const unit = this.getCurrentUnits().find(u => u.value === unitValue)
      return unit ? unit.symbol : unitValue
    },
    
    convertUnits() {
      const value = parseFloat(this.inputValue) || 0
      
      if (this.fromUnit === this.toUnit) {
        this.convertedValue = value.toFixed(6)
        this.conversionFormula = ''
        return
      }
      
      // 转换为基本单位（米、千克、升等）
      let baseValue = this.toBaseUnit(value, this.fromUnit)
      
      // 从基本单位转换为目标单位
      const result = this.fromBaseUnit(baseValue, this.toUnit)
      
      this.convertedValue = result.value.toFixed(6)
      this.conversionFormula = result.formula
    },
    
    toBaseUnit(value, fromUnit) {
      const conversions = {
        // 长度转换到米
        length: {
          mm: value / 1000,
          cm: value / 100,
          m: value,
          km: value * 1000,
          in: value * 0.0254,
          ft: value * 0.3048,
          yd: value * 0.9144,
          mi: value * 1609.344
        },
        // 重量转换到千克
        weight: {
          mg: value / 1000000,
          g: value / 1000,
          kg: value,
          t: value * 1000,
          oz: value * 0.0283495,
          lb: value * 0.453592
        },
        // 体积转换到升
        volume: {
          ml: value / 1000,
          cl: value / 100,
          l: value,
          m3: value * 1000,
          floz: value * 0.0295735,
          cup: value * 0.236588,
          pt: value * 0.473176,
          gal: value * 3.78541
        },
        // 面积转换到平方米
        area: {
          mm2: value / 1000000,
          cm2: value / 10000,
          m2: value,
          ha: value * 10000,
          km2: value * 1000000,
          in2: value * 0.00064516,
          ft2: value * 0.092903,
          ac: value * 4046.86
        },
        // 温度特殊处理
        temperature: {
          c: value,
          f: (value - 32) * 5/9,
          k: value - 273.15
        }
      }
      
      return conversions[this.activeCategory]?.[fromUnit] ?? value
    },
    
    fromBaseUnit(baseValue, toUnit) {
      if (this.activeCategory === 'temperature') {
        // 温度转换特殊处理
        const conversions = {
          c: { value: baseValue, formula: `${baseValue.toFixed(2)} °C` },
          f: { value: (baseValue * 9/5) + 32, formula: `(${baseValue.toFixed(2)} × 9/5) + 32` },
          k: { value: baseValue + 273.15, formula: `${baseValue.toFixed(2)} + 273.15` }
        }
        return conversions[toUnit] || { value: baseValue, formula: '' }
      }
      
      const conversions = {
        length: {
          mm: baseValue * 1000,
          cm: baseValue * 100,
          m: baseValue,
          km: baseValue / 1000,
          in: baseValue / 0.0254,
          ft: baseValue / 0.3048,
          yd: baseValue / 0.9144,
          mi: baseValue / 1609.344
        },
        weight: {
          mg: baseValue * 1000000,
          g: baseValue * 1000,
          kg: baseValue,
          t: baseValue / 1000,
          oz: baseValue / 0.0283495,
          lb: baseValue / 0.453592
        },
        volume: {
          ml: baseValue * 1000,
          cl: baseValue * 100,
          l: baseValue,
          m3: baseValue / 1000,
          floz: baseValue / 0.0295735,
          cup: baseValue / 0.236588,
          pt: baseValue / 0.473176,
          gal: baseValue / 3.78541
        },
        area: {
          mm2: baseValue * 1000000,
          cm2: baseValue * 10000,
          m2: baseValue,
          ha: baseValue / 10000,
          km2: baseValue / 1000000,
          in2: baseValue / 0.00064516,
          ft2: baseValue / 0.092903,
          ac: baseValue / 4046.86
        }
      }
      
      const value = conversions[this.activeCategory]?.[toUnit] ?? baseValue
      return {
        value: value,
        formula: this.activeCategory === 'temperature' ? '' : `${baseValue.toFixed(6)} → ${value.toFixed(6)}`
      }
    },
    
    swapUnits() {
      ;[this.fromUnit, this.toUnit] = [this.toUnit, this.fromUnit]
      this.convertUnits()
    },
    
    // 产品自定义转换方法
    getProductUnits() {
      const units = new Set()
      this.productConversions.forEach(rule => {
        units.add(rule.from_unit)
        units.add(rule.to_unit)
      })
      return Array.from(units)
    },
    
    convertCustomUnits() {
      if (!this.customFromUnit || !this.customToUnit || !this.customInputValue) {
        this.customConvertedValue = null
        return
      }
      
      if (this.customFromUnit === this.customToUnit) {
        this.customConvertedValue = this.customInputValue
        return
      }
      
      // 查找直接转换规则
      const directRule = this.productConversions.find(
        rule => rule.from_unit === this.customFromUnit && rule.to_unit === this.customToUnit
      )
      
      if (directRule) {
        this.customConvertedValue = this.customInputValue * directRule.conversion_rate
        return
      }
      
      // 查找反向转换规则
      const reverseRule = this.productConversions.find(
        rule => rule.from_unit === this.customToUnit && rule.to_unit === this.customFromUnit
      )
      
      if (reverseRule) {
        this.customConvertedValue = this.customInputValue / reverseRule.conversion_rate
        return
      }
      
      // 尝试通过中间单位转换
      this.customConvertedValue = this.findConversionPath()
    },
    
    findConversionPath() {
      // 简化的路径查找算法
      const graph = this.buildConversionGraph()
      const path = this.findShortestPath(graph, this.customFromUnit, this.customToUnit)
      
      if (path.length < 2) return null
      
      let result = this.customInputValue
      for (let i = 0; i < path.length - 1; i++) {
        const from = path[i]
        const to = path[i + 1]
        const rule = this.productConversions.find(r => r.from_unit === from && r.to_unit === to)
        if (rule) {
          result *= rule.conversion_rate
        } else {
          const reverseRule = this.productConversions.find(r => r.from_unit === to && r.to_unit === from)
          if (reverseRule) {
            result /= reverseRule.conversion_rate
          } else {
            return null
          }
        }
      }
      
      return result
    },
    
    buildConversionGraph() {
      const graph = {}
      this.productConversions.forEach(rule => {
        if (!graph[rule.from_unit]) graph[rule.from_unit] = []
        if (!graph[rule.to_unit]) graph[rule.to_unit] = []
        
        graph[rule.from_unit].push(rule.to_unit)
        graph[rule.to_unit].push(rule.from_unit)
      })
      return graph
    },
    
    findShortestPath(graph, start, end) {
      const queue = [[start]]
      const visited = new Set([start])
      
      while (queue.length > 0) {
        const path = queue.shift()
        const node = path[path.length - 1]
        
        if (node === end) return path
        
        for (const neighbor of graph[node] || []) {
          if (!visited.has(neighbor)) {
            visited.add(neighbor)
            queue.push([...path, neighbor])
          }
        }
      }
      
      return []
    },
    
    // 自定义规则管理
    openCustomModal() {
      this.editingRule = null
      this.newRule = {
        product_id: this.selectedProduct ? this.selectedProduct.id : '',
        from_unit: '',
        to_unit: '',
        conversion_rate: 1,
        description: ''
      }
      this.showCustomModal = true
    },
    
    editCustomRule(rule) {
      this.editingRule = rule
      this.newRule = { ...rule }
      this.showCustomModal = true
    },
    
    saveCustomRule() {
      // 保存到后端
      this.saveCustomRuleToBackend()
      
      this.closeCustomModal()
      this.loadProductConversions() // 重新加载显示
    },
    
    // 保存自定义规则到后端
    async saveCustomRuleToBackend() {
      try {
        const method = this.editingRule ? 'PUT' : 'POST'
        const url = this.editingRule 
          ? `/api/products/${this.newRule.product_id}/conversions/${this.editingRule.id}`
          : `/api/products/${this.newRule.product_id}/conversions`
        
        const response = await fetch(url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.newRule)
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const result = await response.json()
        console.log('保存转换规则成功:', result)
      } catch (error) {
        console.error('保存转换规则失败:', error)
      }
    },
    
    async deleteCustomRule(ruleId) {
      if (confirm('确定要删除这个转换规则吗？')) {
        try {
          const response = await fetch(`/api/products/${this.selectedProduct.id}/conversions/${ruleId}`, {
            method: 'DELETE'
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          console.log('删除转换规则成功')
        } catch (error) {
          console.error('删除转换规则失败:', error)
        }
        
        this.loadProductConversions() // 重新加载显示
      }
    },
    
    closeCustomModal() {
      this.showCustomModal = false
      this.editingRule = null
      this.newRule = {
        product_id: '',
        from_unit: '',
        to_unit: '',
        conversion_rate: 1,
        description: ''
      }
    }
  }
}
</script>

<style scoped>
.unit-converter-page {
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

/* 标签页样式 */
.converter-tabs {
  display: flex;
  gap: 8px;
  background: var(--light-color);
  padding: 4px;
  border-radius: 8px;
}

.tab-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--secondary-color);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: rgba(74, 144, 226, 0.1);
  color: var(--primary-color);
}

.tab-btn.active {
  background: var(--primary-color);
  color: white;
}

/* 转换器容器 */
.converter-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.converter-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--dark-color);
}

.form-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.value-input,
.unit-select {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.value-input:focus,
.unit-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.input-group {
  position: relative;
}

.input-hint {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  color: var(--secondary-color);
}

.swap-button {
  margin-bottom: 8px;
}

.btn-swap {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-swap:hover {
  border-color: var(--primary-color);
  background: var(--light-color);
}

/* 转换结果 */
.conversion-result {
  padding: 20px;
  background: var(--light-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.result-value {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.result-number {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary-color);
}

.result-unit {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--dark-color);
}

.result-formula {
  font-size: 0.9rem;
  color: var(--secondary-color);
  font-family: 'Monaco', 'Consolas', monospace;
}

/* 参考表格 */
.conversion-reference {
  background: var(--light-color);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.conversion-reference h4 {
  margin: 0 0 16px 0;
  color: var(--dark-color);
}

.reference-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reference-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.ref-equation {
  font-weight: 500;
  color: var(--dark-color);
}

.ref-value {
  color: var(--primary-color);
  font-weight: 600;
  font-size: 0.9rem;
}

/* 自定义转换器 */
.custom-converter {
  min-height: 400px;
}

.product-selector {
  margin-bottom: 24px;
}

.product-select {
  width: 100%;
  max-width: 400px;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.95rem;
}

.product-conversions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.conversion-rules {
  background: var(--light-color);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.conversion-rules h4 {
  margin: 0 0 16px 0;
  color: var(--dark-color);
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.rule-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.rule-from {
  color: var(--primary-color);
}

.rule-equals {
  color: var(--secondary-color);
}

.rule-to {
  color: var(--success-color);
}

.rule-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.8rem;
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

.no-rules {
  text-align: center;
  padding: 40px 20px;
  color: var(--secondary-color);
}

.custom-converter-form {
  background: var(--light-color);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.custom-converter-form h4 {
  margin: 0 0 16px 0;
  color: var(--dark-color);
}

.custom-result {
  margin-top: 16px;
  padding: 16px;
  background: white;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  font-size: 1.1rem;
  text-align: center;
}

.no-product-selected {
  text-align: center;
  padding: 60px 20px;
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
  max-width: 600px;
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
  display: block;
  margin-top: 4px;
  font-size: 0.8rem;
  color: var(--secondary-color);
}

.rule-preview {
  margin: 20px 0;
  padding: 16px;
  background: #e8f5e8;
  border-radius: 6px;
  border: 1px solid #c8e6c9;
}

.rule-preview h4 {
  margin: 0 0 8px 0;
  font-size: 1rem;
  color: #2e7d32;
}

.preview-equation {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2e7d32;
  text-align: center;
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
  .converter-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .product-conversions {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .converter-tabs {
    width: 100%;
    overflow-x: auto;
  }
  
  .form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .swap-button {
    align-self: center;
    margin: 0;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
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
  
  .rule-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .rule-actions {
    justify-content: flex-end;
  }
}
</style>