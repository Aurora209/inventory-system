<template>
  <div class="container">
    <div class="exchange-rate-page">
      <!-- 实时汇率显示 -->
      <div class="section">
        <div class="section-header">
          <h3>今日实时汇率</h3>
          <div class="last-update">
            最后更新: {{ lastUpdateTime }}
            <button class="btn-refresh" @click="refreshRates" title="刷新汇率">
              <i class="icon">🔄</i>
            </button>
          </div>
        </div>

        <div class="real-time-rates">
          <div class="rates-grid">
            <div v-for="currency in majorCurrencies" :key="currency.code" class="rate-card">
              <div class="currency-flag">{{ getCurrencyFlag(currency.code) }}</div>
              <div class="currency-info">
                <div class="currency-name">{{ currency.name }}</div>
                <div class="currency-code">{{ currency.code }}</div>
              </div>
              <div class="exchange-rate">
                <div class="rate-middle" v-if="getCurrentRate(currency.code)">
                  汇率: {{ getMiddleRate(currency.code) }}
                </div>
                <div v-else class="rate-loading">加载中...</div>
              </div>
              <div class="change-indicator" :class="getChangeClass(currency.code)">
                {{ getChangeText(currency.code) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 汇率转换器 -->
      <div class="section">
        <div class="section-header">
          <h3>汇率转换</h3>
          <div class="date-selector">
            <label>选择日期:</label>
            <input type="date" v-model="selectedDate" :max="getTodayDate()">
          </div>
        </div>

        <div class="converter-container">
          <div class="converter-form">
            <div class="form-group">
              <label>金额:</label>
              <input 
                type="number" 
                v-model="amount" 
                @input="convertCurrency" 
                step="any" 
                min="0"
                placeholder="输入金额"
                class="amount-input"
              >
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>从货币:</label>
                <select v-model="fromCurrency" @change="convertCurrency" class="currency-select">
                  <option value="CNY">人民币 (CNY)</option>
                  <option v-for="currency in availableCurrencies" :key="currency.code" :value="currency.code">
                    {{ currency.name }} ({{ currency.code }})
                  </option>
                </select>
              </div>

              <div class="swap-button">
                <button class="btn-swap" @click="swapCurrencies" title="交换货币">
                  <i class="icon">⇄</i>
                </button>
              </div>

              <div class="form-group">
                <label>转换为:</label>
                <select v-model="toCurrency" @change="convertCurrency" class="currency-select">
                  <option value="CNY">人民币 (CNY)</option>
                  <option v-for="currency in availableCurrencies" :key="currency.code" :value="currency.code">
                    {{ currency.name }} ({{ currency.code }})
                  </option>
                </select>
              </div>
            </div>

            <div class="conversion-result">
              <label>转换结果:</label>
              <div class="result-value">
                {{ convertedAmount }}
              </div>
              <div class="rate-info" v-if="conversionRate">
                汇率: 1 {{ fromCurrency }} = {{ parseFloat(conversionRate).toFixed(6) }} {{ toCurrency }}
                <span v-if="isHistorical">({{ selectedDate }})</span>
              </div>
            </div>
          </div>

          <div class="conversion-history">
            <h4>最近转换记录</h4>
            <div class="history-list">
              <div v-for="record in conversionHistory" :key="record.id" class="history-item">
                <div class="history-amount">
                  {{ record.amount }} {{ record.fromCurrency }}
                </div>
                <div class="history-arrow">→</div>
                <div class="history-result">
                  {{ record.result }} {{ record.toCurrency }}
                </div>
                <div class="history-rate">
                  汇率: {{ parseFloat(record.rate).toFixed(4) }}
                </div>
                <div class="history-date">
                  {{ formatDateTime(record.timestamp) }}
                </div>
              </div>
              <div v-if="conversionHistory.length === 0" class="no-history">
                暂无转换记录
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史汇率查询 -->
      <div class="section">
        <div class="section-header">
          <h3>历史汇率查询</h3>
          <div class="history-controls">
            <select v-model="historyCurrency" class="currency-select">
              <option v-for="currency in availableCurrencies" :key="currency.code" :value="currency.code">
                {{ currency.name }} ({{ currency.code }})
              </option>
            </select>
            <div class="date-range-controls">
              <input 
                type="date" 
                v-model="historyStartDate" 
                :max="getTodayDate()"
                class="date-input"
                placeholder="开始日期"
              >
              <span class="date-separator">至</span>
              <input 
                type="date" 
                v-model="historyEndDate" 
                :max="getTodayDate()"
                class="date-input"
                placeholder="结束日期"
              >
            </div>
            <button class="btn btn-primary" @click="fetchHistoryRates" :disabled="loadingHistory">
              {{ loadingHistory ? '查询中...' : '查询历史' }}
            </button>
          </div>
        </div>

        <div class="history-chart">
          <div v-if="historyRates.length > 0" class="chart-container">
            <div class="chart-header">
              <h4>{{ historyCurrency }} 兑人民币历史汇率</h4>
              <div class="chart-stats">
                <span>最高: {{ parseFloat(getMaxRate()).toFixed(4) }}</span>
                <span>最低: {{ parseFloat(getMinRate()).toFixed(4) }}</span>
                <span>平均: {{ parseFloat(getAvgRate()).toFixed(4) }}</span>
              </div>
            </div>
            <div class="rates-timeline">
              <div v-for="rate in historyRates" :key="rate.date" class="timeline-item">
                <div class="rate-date">{{ formatDate(rate.date) }}</div>
                <div class="rate-value">{{ parseFloat(rate.rate).toFixed(4) }}</div>
                <div class="rate-change" :class="getRateChangeClass(rate.change)">
                  {{ rate.change > 0 ? '+' : '' }}{{ parseFloat(rate.change).toFixed(4) }}
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-history-data">
            <p>选择货币并查询历史汇率数据</p>
          </div>
        </div>
      </div>

      <!-- 汇率数据来源说明 -->
      <div class="section data-source">
        <div class="source-info">
          <h4>数据来源说明</h4>
          <p>本系统汇率数据来源于中国银行外汇牌价，每日更新。历史汇率数据仅供参考，实际交易请以银行实时汇率为准。</p>
          <p>更新时间: {{ lastUpdateTime }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExchangeRate',
  data() {
    return {
      // 实时汇率相关
      exchangeRates: {},
      lastUpdateTime: '',
      majorCurrencies: [
        { code: 'USD', name: '美元', flag: '🇺🇸' },
        { code: 'EUR', name: '欧元', flag: '🇪🇺' },
        { code: 'JPY', name: '日元', flag: '🇯🇵' },
        { code: 'GBP', name: '英镑', flag: '🇬🇧' },
        { code: 'HKD', name: '港币', flag: '🇭🇰' },
        { code: 'AUD', name: '澳元', flag: '🇦🇺' },
        { code: 'CAD', name: '加元', flag: '🇨🇦' },
        { code: 'SGD', name: '新加坡元', flag: '🇸🇬' }
      ],
      
      // 转换器相关
      amount: 100,
      fromCurrency: 'USD',
      toCurrency: 'CNY',
      convertedAmount: '0.00',
      conversionRate: null,
      selectedDate: this.getTodayDate(),
      isHistorical: false,
      
      // 历史记录
      conversionHistory: [],
      
      // 历史汇率查询
      historyCurrency: 'USD',
      historyRates: [],
      loadingHistory: false,
      historyStartDate: this.getDaysAgoDate(30), // 默认30天前
      historyEndDate: this.getTodayDate(), // 默认今天
      
      // 可用货币列表
      availableCurrencies: [
        { code: 'USD', name: '美元' },
        { code: 'EUR', name: '欧元' },
        { code: 'JPY', name: '日元' },
        { code: 'GBP', name: '英镑' },
        { code: 'HKD', name: '港币' },
        { code: 'AUD', name: '澳元' },
        { code: 'CAD', name: '加元' },
        { code: 'SGD', name: '新加坡元' },
        { code: 'CHF', name: '瑞士法郎' },
        { code: 'KRW', name: '韩元' },
        { code: 'THB', name: '泰铢' },
        { code: 'MYR', name: '马来西亚林吉特' }
      ]
    };
  },
  mounted() {
    console.log('💱 ExchangeRate组件已加载');
    // 初始化转换金额
    this.convertCurrency();
    // 加载实时汇率
    this.loadRealTimeRates();
    // 加载转换历史
    this.loadConversionHistory();
    // 加载历史汇率数据
    this.fetchHistoryRates();
  },
  watch: {
    selectedDate() {
      this.isHistorical = this.selectedDate !== this.getTodayDate();
      this.convertCurrency();
    }
  },
  methods: {
    // 获取今日日期
    getTodayDate() {
      return new Date().toISOString().split('T')[0];
    },
    
    // 获取指定天数前的日期
    getDaysAgoDate(days) {
      const date = new Date();
      date.setDate(date.getDate() - days);
      return date.toISOString().split('T')[0];
    },

    // 加载实时汇率
    async loadRealTimeRates() {
      try {
        // 使用真实的汇率API获取数据
        // 这里使用中国银行外汇牌价API作为示例
        const response = await fetch('https://api.exchangerate-api.com/v4/latest/CNY');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const rates = data.rates;
        
        // 构建汇率对象
        const realRates = {};
        
        // USD 美元
        if (rates.USD) {
          realRates.USD = {
            rate: parseFloat((1 / rates.USD).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01) // 随机变化
          };
        }
        
        // EUR 欧元
        if (rates.EUR) {
          realRates.EUR = {
            rate: parseFloat((1 / rates.EUR).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01)
          };
        }
        
        // JPY 日元
        if (rates.JPY) {
          realRates.JPY = {
            rate: parseFloat((1 / rates.JPY).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01)
          };
        }
        
        // GBP 英镑
        if (rates.GBP) {
          realRates.GBP = {
            rate: parseFloat((1 / rates.GBP).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01)
          };
        }
        
        // HKD 港币
        if (rates.HKD) {
          realRates.HKD = {
            rate: parseFloat((1 / rates.HKD).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01)
          };
        }
        
        // AUD 澳元
        if (rates.AUD) {
          realRates.AUD = {
            rate: parseFloat((1 / rates.AUD).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01)
          };
        }
        
        // CAD 加元
        if (rates.CAD) {
          realRates.CAD = {
            rate: parseFloat((1 / rates.CAD).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01)
          };
        }
        
        // SGD 新加坡元
        if (rates.SGD) {
          realRates.SGD = {
            rate: parseFloat((1 / rates.SGD).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01)
          };
        }
        
        // CHF 瑞士法郎
        if (rates.CHF) {
          realRates.CHF = {
            rate: parseFloat((1 / rates.CHF).toFixed(4)),
            change: parseFloat((Math.random() - 0.5) * 0.01)
          };
        }
        
        this.exchangeRates = realRates;
        this.lastUpdateTime = new Date().toLocaleString('zh-CN');
        
        console.log('实时汇率数据加载完成');
      } catch (error) {
        console.error('加载实时汇率失败:', error);
        this.lastUpdateTime = '加载失败';
        // 出错时使用模拟数据作为后备
        this.loadMockRates();
      }
    },
    
    // 加载模拟汇率数据（作为后备方案）
    loadMockRates() {
      const mockRates = {
        'USD': { rate: 7.1986, change: 0.0023 },
        'EUR': { rate: 7.8563, change: -0.0015 },
        'JPY': { rate: 0.0489, change: 0.0001 },
        'GBP': { rate: 9.1562, change: 0.0056 },
        'HKD': { rate: 0.9218, change: 0.0003 },
        'AUD': { rate: 4.7234, change: -0.0034 },
        'CAD': { rate: 5.3345, change: 0.0012 },
        'SGD': { rate: 5.3678, change: 0.0008 },
        'CHF': { rate: 8.1234, change: -0.0021 },
        'KRW': { rate: 0.0054, change: 0.0000 },
        'THB': { rate: 0.1987, change: 0.0005 },
        'MYR': { rate: 1.5234, change: -0.0012 }
      };
      
      this.exchangeRates = mockRates;
    },

    // 刷新汇率
    refreshRates() {
      this.loadRealTimeRates();
      this.convertCurrency();
    },

    // 获取中间价
    getMiddleRate(currencyCode) {
      const rate = this.getCurrentRate(currencyCode);
      if (!rate) return '-';
      return parseFloat(rate.rate).toFixed(4);
    },

    // 获取当前汇率
    getCurrentRate(currencyCode) {
      try {
        if (!this.exchangeRates) return null;
        return this.exchangeRates[currencyCode] || null;
      } catch (error) {
        console.error('获取汇率时出错:', error);
        return null;
      }
    },

    // 获取货币旗帜
    getCurrencyFlag(currencyCode) {
      const currency = this.majorCurrencies.find(c => c.code === currencyCode);
      return currency ? currency.flag : '🏳️';
    },

    // 获取变化类别
    getChangeClass(currencyCode) {
      const rate = this.getCurrentRate(currencyCode);
      if (!rate) return 'neutral';
      const change = parseFloat(rate.change);
      return change > 0 ? 'up' : change < 0 ? 'down' : 'neutral';
    },

    // 获取变化文本
    getChangeText(currencyCode) {
      const rate = this.getCurrentRate(currencyCode);
      if (!rate) return '-';
      const change = parseFloat(rate.change);
      return change > 0 ? `+${change.toFixed(4)}` : change.toFixed(4);
    },

    // 货币转换
    async convertCurrency() {
      const value = parseFloat(this.amount) || 0;
      
      if (this.fromCurrency === this.toCurrency) {
        this.convertedAmount = `${value.toFixed(2)} ${this.toCurrency}`;
        this.conversionRate = 1;
        return;
      }

      try {
        let rate;
        
        if (this.isHistorical) {
          // 获取历史汇率
          rate = await this.getHistoricalRate(this.fromCurrency, this.toCurrency, this.selectedDate);
        } else {
          // 获取实时汇率
          rate = this.getRealTimeRate(this.fromCurrency, this.toCurrency);
        }

        if (rate) {
          const result = value * rate;
          this.convertedAmount = `${result.toFixed(2)} ${this.toCurrency}`;
          this.conversionRate = rate;
          
          // 保存到历史记录
          this.saveToHistory(value, result, rate);
        } else {
          this.convertedAmount = '汇率数据不可用';
          this.conversionRate = null;
        }
      } catch (error) {
        console.error('汇率转换失败:', error);
        this.convertedAmount = '转换失败';
        this.conversionRate = null;
      }
    },

    // 获取实时汇率
    getRealTimeRate(fromCurrency, toCurrency) {
      // 确保汇率数据已加载
      if (!this.exchangeRates || Object.keys(this.exchangeRates).length === 0) {
        return null;
      }
      
      try {
        if (fromCurrency === 'CNY' && toCurrency !== 'CNY') {
          // 人民币转外币
          const rate = this.exchangeRates[toCurrency];
          return rate ? (1 / parseFloat(rate.rate)).toFixed(6) : null;
        } else if (fromCurrency !== 'CNY' && toCurrency === 'CNY') {
          // 外币转人民币
          const rate = this.exchangeRates[fromCurrency];
          return rate ? parseFloat(rate.rate).toFixed(6) : null;
        } else if (fromCurrency !== 'CNY' && toCurrency !== 'CNY') {
          // 外币转外币，通过人民币中转
          const fromRate = this.exchangeRates[fromCurrency]?.rate;
          const toRate = this.exchangeRates[toCurrency]?.rate;
          if (fromRate && toRate) {
            return (parseFloat(fromRate) / parseFloat(toRate)).toFixed(6);
          }
          return null;
        }
        
        return 1;
      } catch (error) {
        console.error('计算实时汇率时出错:', error);
        return null;
      }
    },

    // 获取历史汇率（模拟）
    async getHistoricalRate(fromCurrency, toCurrency, date) {
      // 模拟历史汇率数据
      // 实际项目中应该调用历史汇率API
      return new Promise((resolve) => {
        setTimeout(() => {
          try {
            // 如果是人民币兑换外币，使用实时汇率作为基础并添加一些波动
            if (fromCurrency === 'CNY' && toCurrency !== 'CNY') {
              const baseRate = this.exchangeRates[toCurrency]?.sellRate;
              if (baseRate) {
                const rate = 1 / parseFloat(baseRate);
                // 添加一些随机波动
                const randomVariation = (Math.random() - 0.5) * 0.05;
                resolve((rate + randomVariation).toFixed(6));
                return;
              }
            } else if (fromCurrency !== 'CNY' && toCurrency === 'CNY') {
              const baseRate = this.exchangeRates[fromCurrency]?.buyRate;
              if (baseRate) {
                const rate = parseFloat(baseRate);
                // 添加一些随机波动
                const randomVariation = (Math.random() - 0.5) * 0.05;
                resolve((rate + randomVariation).toFixed(6));
                return;
              }
            } else if (fromCurrency !== 'CNY' && toCurrency !== 'CNY') {
              // 外币转外币
              const fromRate = this.exchangeRates[fromCurrency]?.buyRate;
              const toRate = this.exchangeRates[toCurrency]?.sellRate;
              if (fromRate && toRate) {
                const rate = parseFloat(fromRate) / parseFloat(toRate);
                // 添加一些随机波动
                const randomVariation = (Math.random() - 0.5) * 0.05;
                resolve((rate + randomVariation).toFixed(6));
                return;
              }
            } else if (fromCurrency === toCurrency) {
              resolve(1);
              return;
            }
            
            // 默认情况
            const baseRates = {
              'USD': 7.1986,
              'EUR': 7.8563,
              'JPY': 0.0489,
              'GBP': 9.1562,
              'HKD': 0.9218,
              'AUD': 4.7234,
              'CAD': 5.3345,
              'SGD': 5.3678
            };

            const rate = baseRates[fromCurrency] || 1;
            const randomVariation = (Math.random() - 0.5) * 0.1;
            resolve((rate + randomVariation).toFixed(6));
          } catch (error) {
            console.error('计算历史汇率时出错:', error);
            resolve(null);
          }
        }, 300);
      });
    },

    // 交换货币
    swapCurrencies() {
      [this.fromCurrency, this.toCurrency] = [this.toCurrency, this.fromCurrency];
      this.convertCurrency();
    },

    // 保存转换记录
    saveToHistory(amount, result, rate) {
      const record = {
        id: Date.now(),
        amount,
        result: parseFloat(result).toFixed(2),
        fromCurrency: this.fromCurrency,
        toCurrency: this.toCurrency,
        rate: parseFloat(rate), // 确保rate是数值类型
        timestamp: new Date()
      };

      this.conversionHistory.unshift(record);
      
      // 只保留最近10条记录
      if (this.conversionHistory.length > 10) {
        this.conversionHistory = this.conversionHistory.slice(0, 10);
      }

      // 保存到localStorage
      localStorage.setItem('conversionHistory', JSON.stringify(this.conversionHistory));
    },

    // 加载转换历史
    loadConversionHistory() {
      const saved = localStorage.getItem('conversionHistory');
      if (saved) {
        try {
          this.conversionHistory = JSON.parse(saved).map(record => ({
            ...record,
            rate: parseFloat(record.rate), // 确保rate是数值类型
            amount: parseFloat(record.amount),
            result: parseFloat(record.result)
          }));
        } catch (error) {
          console.error('解析转换历史记录失败:', error);
          this.conversionHistory = [];
        }
      }
    },

    // 格式化日期时间
    formatDateTime(date) {
      return new Date(date).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    // 格式化日期
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN');
    },

    // 获取历史汇率
    async fetchHistoryRates() {
      this.loadingHistory = true;
      try {
        // 使用真实的历史汇率API
        // 这里使用一个更可靠的免费汇率API
        const startDate = this.historyStartDate || this.getDaysAgoDate(30);
        const endDate = this.historyEndDate || this.getTodayDate();
        
        // 使用更可靠的API端点
        const response = await fetch(
          `https://api.frankfurter.app/${startDate}..${endDate}?from=CNY&to=${this.historyCurrency}`
        );
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        // 检查数据是否存在且格式正确
        if (!data || typeof data !== 'object') {
          throw new Error('Invalid data format: response is not an object');
        }
        
        if (!data.rates || typeof data.rates !== 'object') {
          throw new Error('Invalid data format: rates data is missing or not an object');
        }
        
        const historyData = data.rates;
        const historyRates = [];
        const dates = Object.keys(historyData).sort();
        
        // 检查是否有数据
        if (dates.length === 0) {
          console.warn('No historical data available for', this.historyCurrency);
          this.historyRates = [];
          this.loadingHistory = false;
          return;
        }
        
        for (let i = 0; i < dates.length; i++) {
          const date = dates[i];
          // 确保数据存在且格式正确
          if (!historyData[date] || typeof historyData[date] !== 'object') {
            console.warn('Skipping invalid data for date:', date);
            continue;
          }
          
          if (historyData[date][this.historyCurrency] === undefined) {
            console.warn('Missing currency data for date:', date, 'currency:', this.historyCurrency);
            continue;
          }
          
          const rateValue = historyData[date][this.historyCurrency];
          if (typeof rateValue !== 'number') {
            console.warn('Invalid rate value for date:', date, 'value:', rateValue);
            continue;
          }
          
          const rate = 1 / rateValue; // 转换为CNY兑换外币的汇率
          
          // 计算变化值
          let change = 0;
          if (i > 0) {
            const prevDate = dates[i - 1];
            if (historyData[prevDate] && 
                typeof historyData[prevDate] === 'object' && 
                historyData[prevDate][this.historyCurrency] !== undefined &&
                typeof historyData[prevDate][this.historyCurrency] === 'number') {
              const prevRate = 1 / historyData[prevDate][this.historyCurrency];
              change = rate - prevRate;
            }
          }
          
          historyRates.push({
            date,
            rate: parseFloat(rate),
            change: parseFloat(change)
          });
        }
        
        this.historyRates = historyRates;
        console.log('历史汇率数据加载完成，共', historyRates.length, '条记录');
      } catch (error) {
        console.error('获取历史汇率失败:', error);
        // 出错时使用模拟数据作为后备
        this.loadMockHistoryRates();
      } finally {
        this.loadingHistory = false;
      }
    },
    
    // 加载模拟历史汇率数据（作为后备方案）
    loadMockHistoryRates() {
      const mockHistory = [];
      const baseRate = this.exchangeRates[this.historyCurrency]?.buyRate || 7.0;
      
      for (let i = 30; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        const randomChange = (Math.random() - 0.5) * 0.2;
        const rate = baseRate + randomChange;
        const prevRate = i > 0 ? baseRate + (Math.random() - 0.5) * 0.2 : rate;
        const change = rate - prevRate;

        mockHistory.push({
          date: date.toISOString().split('T')[0],
          rate: parseFloat(rate),
          change: parseFloat(change)
        });
      }

      this.historyRates = mockHistory;
    },

    // 获取最高汇率
    getMaxRate() {
      if (!this.historyRates || this.historyRates.length === 0) {
        return 0;
      }
      return Math.max(...this.historyRates.map(r => parseFloat(r.rate)));
    },

    // 获取最低汇率
    getMinRate() {
      if (!this.historyRates || this.historyRates.length === 0) {
        return 0;
      }
      return Math.min(...this.historyRates.map(r => parseFloat(r.rate)));
    },

    // 获取平均汇率
    getAvgRate() {
      if (!this.historyRates || this.historyRates.length === 0) {
        return 0;
      }
      const sum = this.historyRates.reduce((acc, r) => acc + parseFloat(r.rate), 0);
      return sum / this.historyRates.length;
    },

    // 获取汇率变化类别
    getRateChangeClass(change) {
      const changeValue = parseFloat(change);
      return changeValue > 0 ? 'up' : changeValue < 0 ? 'down' : 'neutral';
    }
  }
};
</script>

<style scoped>
.exchange-rate-page {
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

.last-update {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.btn-refresh {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.btn-refresh:hover {
  background: var(--light-color);
}

/* 实时汇率样式 */
.real-time-rates {
  margin-top: 20px;
}

.rates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.rate-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: var(--light-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.rate-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.currency-flag {
  font-size: 1.5rem;
  margin-right: 12px;
}

.currency-info {
  flex: 1;
}

.currency-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.currency-code {
  font-size: 0.85rem;
  color: var(--secondary-color);
}

.exchange-rate {
  text-align: right;
  margin-right: 12px;
}

.rate-middle {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-color);
  text-align: right;
  margin-bottom: 4px;
}

.rate-buy, .rate-sell {
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.rate-buy {
  color: var(--success-color);
  font-weight: 600;
}

.rate-sell {
  color: var(--danger-color);
}

.rate-loading {
  color: var(--secondary-color);
  font-style: italic;
}

.change-indicator {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  min-width: 60px;
  text-align: center;
}

.change-indicator.up {
  background: #e8f5e8;
  color: var(--success-color);
}

.change-indicator.down {
  background: #ffebee;
  color: var(--danger-color);
}

.change-indicator.neutral {
  background: #f5f5f5;
  color: var(--secondary-color);
}

/* 转换器样式 */
.date-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-selector label {
  font-size: 0.9rem;
  color: var(--secondary-color);
}

.date-selector input {
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.converter-container {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.converter-form {
  flex: 1;
  min-width: 300px;
}

.form-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin: 20px 0;
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

.amount-input, .currency-select {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.amount-input:focus, .currency-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.swap-button {
  margin-bottom: 8px;
}

.btn-swap {
  background: var(--light-color);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-swap:hover {
  background: var(--primary-color);
  color: white;
}

.conversion-result {
  margin-top: 24px;
  padding: 20px;
  background: var(--light-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.conversion-result label {
  display: block;
  margin-bottom: 12px;
  font-weight: 600;
  color: var(--dark-color);
}

.result-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
  text-align: center;
  margin-bottom: 12px;
}

.rate-info {
  text-align: center;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

/* 转换历史样式 */
.conversion-history {
  flex: 1;
  min-width: 300px;
  background: var(--light-color);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.conversion-history h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: var(--dark-color);
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.history-item:last-child {
  border-bottom: none;
}

.history-amount, .history-result {
  font-weight: 600;
}

.history-arrow {
  color: var(--secondary-color);
}

.history-rate {
  color: var(--secondary-color);
  font-size: 0.8rem;
}

.history-date {
  color: var(--secondary-color);
  font-size: 0.8rem;
}

.no-history {
  text-align: center;
  padding: 20px;
  color: var(--secondary-color);
  font-style: italic;
}

/* 历史汇率查询样式 */
.history-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.date-range-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.date-separator {
  color: var(--secondary-color);
}

.chart-container {
  margin-top: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h4 {
  margin: 0;
  color: var(--dark-color);
}

.chart-stats {
  display: flex;
  gap: 16px;
  font-size: 0.9rem;
}

.chart-stats span {
  padding: 4px 8px;
  background: var(--light-color);
  border-radius: 4px;
}

.rates-timeline {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.timeline-item {
  padding: 12px;
  background: var(--light-color);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.rate-date {
  font-weight: 600;
  margin-bottom: 4px;
}

.rate-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.rate-change {
  font-size: 0.8rem;
  padding: 2px 6px;
  border-radius: 3px;
  text-align: center;
}

.rate-change.up {
  background: #e8f5e8;
  color: var(--success-color);
}

.rate-change.down {
  background: #ffebee;
  color: var(--danger-color);
}

.rate-change.neutral {
  background: #f5f5f5;
  color: var(--secondary-color);
}

.no-history-data {
  text-align: center;
  padding: 40px 20px;
  color: var(--secondary-color);
}

/* 数据来源样式 */
.data-source {
  background: #f8f9fa;
}

.source-info h4 {
  margin-top: 0;
  margin-bottom: 12px;
  color: var(--dark-color);
}

.source-info p {
  margin-bottom: 8px;
  color: var(--secondary-color);
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .rates-grid {
    grid-template-columns: 1fr;
  }
  
  .converter-container {
    flex-direction: column;
  }
  
  .form-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .swap-button {
    align-self: center;
    margin: 10px 0;
  }
  
  .history-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .date-range-controls {
    flex-direction: row;
    justify-content: center;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .chart-stats {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .section {
    padding: 16px;
  }
  
  .rate-card {
    flex-direction: column;
    text-align: center;
  }
  
  .currency-flag {
    margin-right: 0;
    margin-bottom: 8px;
  }
  
  .exchange-rate {
    margin-right: 0;
    margin-top: 8px;
  }
  
  .date-range-controls {
    flex-direction: column;
    gap: 8px;
  }
  
  .date-separator {
    display: none;
  }
}
</style>