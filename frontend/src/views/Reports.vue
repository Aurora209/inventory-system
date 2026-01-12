<template>
  <div class="reports-page">
    <div class="page-header">
      <h2>📊 报表中心</h2>
      <p>查看和导出各类业务报表</p>
    </div>

    <!-- 报表类型选择 -->
    <div class="report-tabs">
      <button 
        v-for="tab in reportTabs" 
        :key="tab.key"
        :class="['tab-button', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- 报表内容区域 -->
    <div class="report-content">
      <!-- BOM导出报表 -->
      <div v-if="activeTab === 'bom-export'" class="report-section">
        <div class="section-header">
          <h3>BOM数据导出</h3>
          <button class="btn btn-primary" @click="exportBomExcel">
            <i class="icon">📥</i> 导出Excel
          </button>
        </div>
        <div class="report-description">
          <p>导出所有产品的BOM数据为Excel格式，包含产品信息、物料清单、数量、单价和小计等详细信息。</p>
        </div>
      </div>

      <!-- 物料需求计划报表 -->
      <div v-if="activeTab === 'material-requirements'" class="report-section">
        <div class="section-header">
          <h3>物料需求计划</h3>
        </div>
        <div class="report-description">
          <p>显示所有物料的总需求量、当前库存和缺货情况，帮助制定采购计划。</p>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>物料SKU</th>
                <th>物料名称</th>
                <th>单位</th>
                <th>总需求数量</th>
                <th>当前库存</th>
                <th>缺货数量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in materialRequirements" :key="index">
                <td>{{ item['物料SKU'] }}</td>
                <td>{{ item['物料名称'] }}</td>
                <td>{{ item['单位'] }}</td>
                <td>{{ item['总需求数量'].toFixed(2) }}</td>
                <td>{{ item['当前库存'].toFixed(2) }}</td>
                <td :class="{ 'low-stock': item['缺货数量'] > 0 }">
                  {{ item['缺货数量'].toFixed(2) }}
                </td>
              </tr>
              <tr v-if="materialRequirements.length === 0">
                <td colspan="6" class="empty-state">
                  <div class="empty-content">
                    <i class="empty-icon">📋</i>
                    <p>暂无物料需求数据</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 成本分析报表 -->
      <div v-if="activeTab === 'cost-analysis'" class="report-section">
        <div class="section-header">
          <h3>成本分析</h3>
        </div>
        <div class="report-description">
          <p>分析各产品的物料成本，包括总成本和单位成本，帮助进行成本控制。</p>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>产品SKU</th>
                <th>产品名称</th>
                <th>物料数量</th>
                <th>总成本</th>
                <th>单位成本</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in costAnalysis" :key="index">
                <td>{{ item['产品SKU'] }}</td>
                <td>{{ item['产品名称'] }}</td>
                <td>{{ item['物料数量'] }}</td>
                <td>¥{{ item['总成本'].toFixed(2) }}</td>
                <td>¥{{ item['单位成本'].toFixed(2) }}</td>
              </tr>
              <tr v-if="costAnalysis.length === 0">
                <td colspan="5" class="empty-state">
                  <div class="empty-content">
                    <i class="empty-icon">💰</i>
                    <p>暂无成本分析数据</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 采购清单报表 -->
      <div v-if="activeTab === 'purchase-list'" class="report-section">
        <div class="section-header">
          <h3>采购清单</h3>
        </div>
        <div class="report-description">
          <p>列出所有需要采购的物料清单，包括采购数量和金额，帮助制定采购计划。</p>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>物料SKU</th>
                <th>物料名称</th>
                <th>单位</th>
                <th>总需求数量</th>
                <th>当前库存</th>
                <th>采购数量</th>
                <th>采购单价</th>
                <th>采购金额</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in purchaseList" :key="index">
                <td>{{ item['物料SKU'] }}</td>
                <td>{{ item['物料名称'] }}</td>
                <td>{{ item['单位'] }}</td>
                <td>{{ item['总需求数量'].toFixed(2) }}</td>
                <td>{{ item['当前库存'].toFixed(2) }}</td>
                <td>{{ item['缺货数量'].toFixed(2) }}</td>
                <td>¥{{ item['采购单价'].toFixed(2) }}</td>
                <td>¥{{ item['采购金额'].toFixed(2) }}</td>
              </tr>
              <tr v-if="purchaseList.length === 0">
                <td colspan="8" class="empty-state">
                  <div class="empty-content">
                    <i class="empty-icon">🛒</i>
                    <p>暂无需要采购的物料</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reportApi } from '@/services/api';

export default {
  name: 'Reports',
  data() {
    return {
      activeTab: 'bom-export',
      reportTabs: [
        { key: 'bom-export', name: 'BOM导出' },
        { key: 'material-requirements', name: '物料需求计划' },
        { key: 'cost-analysis', name: '成本分析' },
        { key: 'purchase-list', name: '采购清单' }
      ],
      materialRequirements: [],
      costAnalysis: [],
      purchaseList: []
    }
  },
  watch: {
    activeTab: {
      handler(newTab) {
        this.loadReportData(newTab);
      },
      immediate: true
    }
  },
  methods: {
    async loadReportData(tab) {
      try {
        switch (tab) {
          case 'material-requirements':
            const materialRes = await reportApi.getMaterialRequirements();
            this.materialRequirements = materialRes || [];
            break;
          case 'cost-analysis':
            const costRes = await reportApi.getCostAnalysis();
            this.costAnalysis = costRes || [];
            break;
          case 'purchase-list':
            const purchaseRes = await reportApi.getPurchaseList();
            this.purchaseList = purchaseRes || [];
            break;
        }
      } catch (error) {
        console.error('加载报表数据失败:', error);
        alert('加载报表数据失败: ' + (error.message || '未知错误'));
      }
    },
    
    async exportBomExcel() {
      try {
        const response = await reportApi.exportBomExcel();
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'bom_report.xlsx');
        document.body.appendChild(link);
        link.click();
        
        // 清理
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        alert('BOM报表导出成功！');
      } catch (error) {
        console.error('导出BOM报表失败:', error);
        alert('导出BOM报表失败: ' + (error.message || '未知错误'));
      }
    }
  }
}
</script>

<style scoped>
.reports-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header h2 {
  margin-bottom: 8px;
  color: var(--dark-color);
}

.page-header p {
  color: var(--secondary-color);
  margin: 0;
}

.report-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.tab-button {
  padding: 12px 24px;
  background: var(--light-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab-button:hover {
  background: #e9ecef;
}

.tab-button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.report-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  color: var(--dark-color);
}

.report-description {
  margin-bottom: 24px;
  color: var(--secondary-color);
}

.report-description p {
  margin: 0;
  line-height: 1.6;
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
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  background: var(--light-color);
  font-weight: 600;
  color: var(--dark-color);
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.low-stock {
  color: var(--danger-color);
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

@media (max-width: 768px) {
  .reports-page {
    padding: 16px;
  }
  
  .report-tabs {
    gap: 4px;
  }
  
  .tab-button {
    padding: 10px 16px;
    font-size: 0.9rem;
  }
  
  .report-section {
    padding: 16px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>