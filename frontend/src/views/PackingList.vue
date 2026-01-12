<template>
  <div class="packing-list-page">
    <div class="container">
      <div class="section">
        <div class="section-header">
          <h3>装箱单 - {{ selectedOrder?.order_number || '' }}</h3>
          <button class="btn btn-secondary" @click="printPackingList">打印装箱单</button>
          <button class="btn btn-primary" @click="savePackingList">保存装箱单</button>
          <button class="btn btn-secondary" @click="$emit('close')">返回订单列表</button>
        </div>

        <div class="packing-edit-section" v-if="selectedOrder">
          <div v-for="(item, idx) in selectedOrder.items" :key="idx" class="packing-item">
            <div class="packing-item-header">
              <strong>{{ idx + 1 }}. {{ item.description }}</strong>
              <span>数量: {{ item.quantity }}</span>
            </div>
            
            <!-- 小箱配置 -->
            <div class="box-config">
              <h4>小箱配置</h4>
              <div class="form-group">
                <label>每小箱装入件数</label>
                <input type="number" v-model.number="item.units_per_box" min="1" placeholder="每小箱件数">
              </div>
              <div class="form-group">
                <label>小箱尺寸 (cm)</label>
                <div class="dimensions-input">
                  <input type="number" v-model.number="item.smallBox.length" placeholder="长">
                  <span>x</span>
                  <input type="number" v-model.number="item.smallBox.width" placeholder="宽">
                  <span>x</span>
                  <input type="number" v-model.number="item.smallBox.height" placeholder="高">
                </div>
              </div>
              <div class="form-group">
                <label>小箱重量 (kg)</label>
                <input type="number" v-model.number="item.smallBox.weight" step="0.01" placeholder="重量">
              </div>
            </div>
            
            <!-- 大箱配置 -->
            <div class="box-config">
              <h4>大箱配置</h4>
              <div class="form-group">
                <label>每大箱包含小箱数</label>
                <input type="number" v-model.number="item.largeBox.units_per_box" min="1" placeholder="小箱数">
              </div>
              <div class="form-group">
                <label>大箱尺寸 (cm)</label>
                <div class="dimensions-input">
                  <input type="number" v-model.number="item.largeBox.length" placeholder="长">
                  <span>x</span>
                  <input type="number" v-model.number="item.largeBox.width" placeholder="宽">
                  <span>x</span>
                  <input type="number" v-model.number="item.largeBox.height" placeholder="高">
                </div>
              </div>
              <div class="form-group">
                <label>大箱重量 (kg)</label>
                <input type="number" v-model.number="item.largeBox.weight" step="0.01" placeholder="重量">
              </div>
            </div>
            
            <!-- 装箱详情 -->
            <div class="packing-boxes">
              <h4>装箱详情</h4>
              <div v-if="!item.packing || item.packing.length === 0" class="packing-auto">
                系统将自动按每小箱 {{ item.units_per_box }} 件，每大箱 {{ item.largeBox.units_per_box }} 小箱分箱
              </div>
              <div v-else>
                <div v-for="(box, boxIdx) in item.packing" :key="boxIdx" class="packing-box-row">
                  <span>大箱 {{ boxIdx + 1 }}:</span>
                  <span>{{ box.smallBoxes }} 小箱</span>
                  <button @click="removeBox(item, boxIdx)" class="btn btn-sm btn-danger">删除</button>
                </div>
              </div>
              <button @click="addBox(item)" class="btn btn-sm btn-secondary">添加大箱</button>
              <button v-if="item.packing && item.packing.length > 0" @click="resetPacking(item)" class="btn btn-sm btn-warning">重置为自动分箱</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { orderApi } from '@/services/api.js'

export default {
  name: 'PackingList',
  props: {
    order: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      selectedOrder: null
    }
  },
  created() {
    // 深拷贝订单数据，避免修改原始数据
    this.selectedOrder = JSON.parse(JSON.stringify(this.order));
    
    // 确保每个订单项都有装箱相关属性
    if (this.selectedOrder && this.selectedOrder.items) {
      this.selectedOrder.items.forEach(item => {
        // 确保每小箱装入件数存在，默认为1
        if (item.units_per_box === undefined || item.units_per_box === null) {
          item.units_per_box = 1;
        }
        
        // 初始化小箱配置
        if (!item.smallBox) {
          item.smallBox = {
            length: null,
            width: null,
            height: null,
            weight: null
          };
        }
        
        // 初始化大箱配置
        if (!item.largeBox) {
          item.largeBox = {
            units_per_box: 4, // 默认每大箱包含4个小箱
            length: null,
            width: null,
            height: null,
            weight: null
          };
        }
        
        // 如果订单项中已有箱子信息，则使用这些信息
        if (item.small_box_length !== undefined) {
          item.smallBox.length = item.small_box_length;
        }
        if (item.small_box_width !== undefined) {
          item.smallBox.width = item.small_box_width;
        }
        if (item.small_box_height !== undefined) {
          item.smallBox.height = item.small_box_height;
        }
        if (item.small_box_weight !== undefined) {
          item.smallBox.weight = item.small_box_weight;
        }
        
        if (item.large_box_units_per_box !== undefined) {
          item.largeBox.units_per_box = item.large_box_units_per_box;
        }
        if (item.large_box_length !== undefined) {
          item.largeBox.length = item.large_box_length;
        }
        if (item.large_box_width !== undefined) {
          item.largeBox.width = item.large_box_width;
        }
        if (item.large_box_height !== undefined) {
          item.largeBox.height = item.large_box_height;
        }
        if (item.large_box_weight !== undefined) {
          item.largeBox.weight = item.large_box_weight;
        }
        
        // 初始化装箱信息
        if (item.packing === undefined) {
          item.packing = [];
        }
      });
    }
  },
  methods: {
    addBox(item) {
      // 添加大箱
      if (!item.packing) {
        item.packing = [];
      }
      
      // 计算需要的小箱数量
      const smallBoxes = item.largeBox.units_per_box || 4;
      
      item.packing.push({
        smallBoxes: smallBoxes
      });
    },

    removeBox(item, index) {
      // 删除大箱
      if (item.packing && item.packing.length > index) {
        item.packing.splice(index, 1);
        // 如果没有大箱了，清空packing数组
        if (item.packing.length === 0) {
          item.packing = [];
        }
      }
    },

    resetPacking(item) {
      // 重置为自动分箱
      item.packing = [];
    },

    async savePackingList() {
      try {
        // 处理箱子信息，确保后端能正确接收
        const orderToSave = JSON.parse(JSON.stringify(this.selectedOrder));
        
        // 为每个订单项添加箱子信息字段，确保与后端字段对应
        if (orderToSave.items) {
          orderToSave.items.forEach(item => {
            // 小箱信息
            item.small_box_length = item.smallBox?.length || null;
            item.small_box_width = item.smallBox?.width || null;
            item.small_box_height = item.smallBox?.height || null;
            item.small_box_weight = item.smallBox?.weight || null;
            
            // 大箱信息
            item.large_box_units_per_box = item.largeBox?.units_per_box || 4;
            item.large_box_length = item.largeBox?.length || null;
            item.large_box_width = item.largeBox?.width || null;
            item.large_box_height = item.largeBox?.height || null;
            item.large_box_weight = item.largeBox?.weight || null;
          });
        }
        
        // 保存装箱单信息到订单中
        const updatedOrder = await orderApi.updateOrder(orderToSave.id, orderToSave);
        this.$emit('saved', updatedOrder.data || updatedOrder);
        alert('装箱单保存成功');
      } catch (error) {
        console.error('保存装箱单失败:', error);
        alert('保存装箱单失败: ' + (error.response?.data?.message || error.message));
      }
    },

    printPackingList() {
      // 打印装箱单
      if (!this.selectedOrder) {
        window.print();
        return;
      }

      // 构建打印内容
      let packingRows = '';
      let rowIndex = 1;
      
      this.selectedOrder.items.forEach((item, itemIdx) => {
        // 如果有手动装箱信息
        if (item.packing && item.packing.length > 0) {
          item.packing.forEach((box, boxIdx) => {
            // 计算净重和毛重
            const smallBoxCount = box.smallBoxes;
            const itemsPerSmallBox = item.units_per_box || 1;
            const totalItemsInLargeBox = smallBoxCount * itemsPerSmallBox;
            
            // 净重计算（仅产品重量）
            const netWeightKg = (item.smallBox.weight || 0) * smallBoxCount;
            const netWeightLb = netWeightKg * 2.20462;
            
            // 毛重计算（产品重量 + 大箱重量）
            const grossWeightKg = netWeightKg + (item.largeBox.weight || 0);
            const grossWeightLb = grossWeightKg * 2.20462;
            
            // 尺寸信息
            const smallBoxDimsCm = [item.smallBox.length, item.smallBox.width, item.smallBox.height]
              .filter(dim => dim !== null)
              .join('x') || '未设置';
              
            const largeBoxDimsCm = [item.largeBox.length, item.largeBox.width, item.largeBox.height]
              .filter(dim => dim !== null)
              .join('x') || '未设置';
              
            // 转换为英寸 (1英寸 = 2.54厘米)
            let smallBoxDimsInch = '未设置';
            if (item.smallBox.length && item.smallBox.width && item.smallBox.height) {
              const inchLength = (item.smallBox.length / 2.54).toFixed(1);
              const inchWidth = (item.smallBox.width / 2.54).toFixed(1);
              const inchHeight = (item.smallBox.height / 2.54).toFixed(1);
              smallBoxDimsInch = `${inchLength}x${inchWidth}x${inchHeight}`;
            }
            
            let largeBoxDimsInch = '未设置';
            if (item.largeBox.length && item.largeBox.width && item.largeBox.height) {
              const inchLength = (item.largeBox.length / 2.54).toFixed(1);
              const inchWidth = (item.largeBox.width / 2.54).toFixed(1);
              const inchHeight = (item.largeBox.height / 2.54).toFixed(1);
              largeBoxDimsInch = `${inchLength}x${inchWidth}x${inchHeight}`;
            }
            
            // 生成小箱信息的分栏显示
            let smallBoxDetails = '';
            for (let i = 0; i < smallBoxCount; i++) {
              // 每个小箱的重量
              const smallNetWeightKg = item.smallBox.weight || 0;
              const smallNetWeightLb = smallNetWeightKg * 2.20462;
              const smallGrossWeightKg = smallNetWeightKg + (item.largeBox.weight || 0) / smallBoxCount;
              const smallGrossWeightLb = smallGrossWeightKg * 2.20462;
              
              smallBoxDetails += `
                <div class="small-box-row">
                  <span>小箱 ${i + 1}</span>
                  <span>${smallBoxDimsCm} cm</span>
                  <span>${smallBoxDimsInch} inch</span>
                  <span>${smallGrossWeightKg.toFixed(2)} kg</span>
                  <span>${smallGrossWeightLb.toFixed(2)} lb</span>
                  <span>${smallNetWeightKg.toFixed(2)} kg</span>
                  <span>${smallNetWeightLb.toFixed(2)} lb</span>
                </div>
              `;
            }
            
            packingRows += `
              <tr>
                <td>${rowIndex++}</td>
                <td>${item.description}</td>
                <td>大箱 ${boxIdx + 1}</td>
                <td class="small-box-container">
                  <div class="small-box-header">
                    <span>箱号</span>
                    <span>尺寸cm</span>
                    <span>尺寸inch</span>
                    <span>毛重kg</span>
                    <span>毛重lb</span>
                    <span>净重kg</span>
                    <span>净重lb</span>
                  </div>
                  ${smallBoxDetails}
                </td>
                <td>
                  <div>${largeBoxDimsCm} cm</div>
                  <div>${largeBoxDimsInch} inch</div>
                </td>
                <td>
                  <div>${(item.largeBox.weight || 0).toFixed(2)} kg</div>
                  <div>${((item.largeBox.weight || 0) * 2.20462).toFixed(2)} lb</div>
                </td>
              </tr>
            `;
          });
        } else {
          // 自动分箱计算
          const totalItems = item.quantity || 0;
          const itemsPerSmallBox = item.units_per_box || 1;
          const smallBoxesPerLargeBox = item.largeBox.units_per_box || 4;
          
          // 计算需要的总小箱数和大箱数
          const totalSmallBoxes = Math.ceil(totalItems / itemsPerSmallBox);
          const totalLargeBoxes = Math.ceil(totalSmallBoxes / smallBoxesPerLargeBox);
          
          // 为每个大箱生成一行
          for (let boxIdx = 0; boxIdx < totalLargeBoxes; boxIdx++) {
            // 计算这个大箱中的小箱数
            const remainingSmallBoxes = totalSmallBoxes - (boxIdx * smallBoxesPerLargeBox);
            const smallBoxCount = Math.min(remainingSmallBoxes, smallBoxesPerLargeBox);
            const itemsInThisLargeBox = smallBoxCount * itemsPerSmallBox;
            
            // 净重计算（仅产品重量）
            const netWeightKg = (item.smallBox.weight || 0) * smallBoxCount;
            const netWeightLb = netWeightKg * 2.20462;
            
            // 毛重计算（产品重量 + 大箱重量）
            const grossWeightKg = netWeightKg + (item.largeBox.weight || 0);
            const grossWeightLb = grossWeightKg * 2.20462;
            
            // 尺寸信息
            const smallBoxDimsCm = [item.smallBox.length, item.smallBox.width, item.smallBox.height]
              .filter(dim => dim !== null)
              .join('x') || '未设置';
              
            const largeBoxDimsCm = [item.largeBox.length, item.largeBox.width, item.largeBox.height]
              .filter(dim => dim !== null)
              .join('x') || '未设置';
              
            // 转换为英寸 (1英寸 = 2.54厘米)
            let smallBoxDimsInch = '未设置';
            if (item.smallBox.length && item.smallBox.width && item.smallBox.height) {
              const inchLength = (item.smallBox.length / 2.54).toFixed(1);
              const inchWidth = (item.smallBox.width / 2.54).toFixed(1);
              const inchHeight = (item.smallBox.height / 2.54).toFixed(1);
              smallBoxDimsInch = `${inchLength}x${inchWidth}x${inchHeight}`;
            }
            
            let largeBoxDimsInch = '未设置';
            if (item.largeBox.length && item.largeBox.width && item.largeBox.height) {
              const inchLength = (item.largeBox.length / 2.54).toFixed(1);
              const inchWidth = (item.largeBox.width / 2.54).toFixed(1);
              const inchHeight = (item.largeBox.height / 2.54).toFixed(1);
              largeBoxDimsInch = `${inchLength}x${inchWidth}x${inchHeight}`;
            }
            
            // 生成小箱信息的分栏显示
            let smallBoxDetails = '';
            for (let i = 0; i < smallBoxCount; i++) {
              // 每个小箱的重量
              const smallNetWeightKg = item.smallBox.weight || 0;
              const smallNetWeightLb = smallNetWeightKg * 2.20462;
              const smallGrossWeightKg = smallNetWeightKg + (item.largeBox.weight || 0) / smallBoxCount;
              const smallGrossWeightLb = smallGrossWeightKg * 2.20462;
              
              smallBoxDetails += `
                <div class="small-box-row">
                  <span>小箱 ${i + 1}</span>
                  <span>${smallBoxDimsCm} cm</span>
                  <span>${smallBoxDimsInch} inch</span>
                  <span>${smallGrossWeightKg.toFixed(2)} kg</span>
                  <span>${smallGrossWeightLb.toFixed(2)} lb</span>
                  <span>${smallNetWeightKg.toFixed(2)} kg</span>
                  <span>${smallNetWeightLb.toFixed(2)} lb</span>
                </div>
              `;
            }
            
            packingRows += `
              <tr>
                <td>${rowIndex++}</td>
                <td>${item.description}</td>
                <td>大箱 ${boxIdx + 1}</td>
                <td class="small-box-container">
                  <div class="small-box-header">
                    <span>箱号</span>
                    <span>尺寸cm</span>
                    <span>尺寸inch</span>
                    <span>毛重kg</span>
                    <span>毛重lb</span>
                    <span>净重kg</span>
                    <span>净重lb</span>
                  </div>
                  ${smallBoxDetails}
                </td>
                <td>
                  <div>${largeBoxDimsCm} cm</div>
                  <div>${largeBoxDimsInch} inch</div>
                </td>
                <td>
                  <div>${(item.largeBox.weight || 0).toFixed(2)} kg</div>
                  <div>${((item.largeBox.weight || 0) * 2.20462).toFixed(2)} lb</div>
                </td>
              </tr>
            `;
          }
        }
      });

      // 打印样式
      const styles = `
        <style>
          body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            font-size: 14px;
          }
          .pl-title { 
            text-align: center; 
            font-size: 24px; 
            margin-bottom: 20px;
            font-weight: bold;
          }
          .pl-header { 
            margin-bottom: 20px;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
          }
          .pl-header div {
            margin-bottom: 5px;
          }
          .pl-table { 
            width: 100%; 
            border-collapse: collapse;
            margin-bottom: 20px;
            table-layout: fixed;
          }
          .pl-table th, .pl-table td { 
            border: 1px solid #000; 
            padding: 10px; 
            text-align: left; 
            vertical-align: top;
          }
          .pl-table th { 
            background-color: #f2f2f2;
            font-weight: bold;
            text-align: center;
          }
          .small-box-container {
            font-size: 12px;
          }
          .small-box-header {
            font-weight: bold;
            border-bottom: 1px solid #999;
            padding-bottom: 5px;
            margin-bottom: 5px;
          }
          .small-box-header span, .small-box-row span {
            display: inline-block;
            width: 14%;
          }
          .small-box-row {
            margin-bottom: 3px;
          }
          @media print {
            button { display: none; }
            body { font-size: 11px; }
            .pl-table th, .pl-table td { padding: 6px; }
            .small-box-header span, .small-box-row span {
              width: 13%;
              font-size: 11px;
            }
          }
        </style>
      `;

      // 打印内容
      const content = `
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>装箱单 - ${this.selectedOrder.order_number || ""}</title>
          ${styles}
        </head>
        <body>
          <div class="pl-title">装箱单 / Packing List</div>
          
          <div class="pl-header">
            <div><strong>订单号:</strong> ${this.selectedOrder.order_number || ""}</div>
            <div><strong>客户/供应商:</strong> ${this.selectedOrder.customer_supplier || ""}</div>
            <div><strong>日期:</strong> ${this.formatDate(this.selectedOrder.order_date) || ""}</div>
          </div>

          <table class="pl-table">
            <thead>
              <tr>
                <th width="5%">序号</th>
                <th width="15%">产品名称</th>
                <th width="10%">箱号（大箱）</th>
                <th width="35%">小箱信息</th>
                <th width="20%">大箱尺寸</th>
                <th width="15%">大箱重量</th>
              </tr>
            </thead>
            <tbody>
              ${packingRows}
            </tbody>
          </table>
          
          <div style="margin-top:30px;font-size:12px;color:#666">
            <p><strong>备注:</strong> 请按装箱单核对货物件数与包装。</p>
            <p>1英寸 = 2.54厘米, 1磅(lb) = 0.453592千克(kg)</p>
          </div>
        </body>
        </html>
      `;

      const printWindow = window.open("", "_blank");
      if (!printWindow) {
        window.print();
        return;
      }

      printWindow.document.open();
      printWindow.document.write(content);
      printWindow.document.close();
      printWindow.focus();

      setTimeout(() => {
        try {
          printWindow.print();
        } catch (e) {
          console.error("打印错误", e);
        }
        try {
          printWindow.close();
        } catch (e) {
          // 忽略关闭错误
        }
      }, 300);
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN');
    }
  }
}
</script>

<style scoped>
.packing-list-page {
  padding: 20px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.section-header h3 {
  margin: 0;
}

.packing-edit-section .packing-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.packing-item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.box-config {
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
}

.box-config h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.dimensions-input {
  display: flex;
  align-items: center;
  gap: 5px;
}

.dimensions-input input {
  width: 60px;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 3px;
}

.dimensions-input span {
  margin: 0 5px;
}

.form-group input {
  width: 100%;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 3px;
  box-sizing: border-box;
}

.packing-auto {
  color: #666;
  font-style: italic;
  padding: 10px 0;
}

.packing-boxes h4 {
  margin-top: 0;
}

.packing-boxes {
  margin-top: 10px;
}

.packing-box-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
  padding: 5px;
  background-color: #f9f9f9;
  border-radius: 3px;
}

.box-quantity-input {
  width: 80px;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 3px;
}
</style>