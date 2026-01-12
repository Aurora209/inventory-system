<template>
  <div class="orders-page">
    <h1>简化版采购订单</h1>
    <p>这是一个简化版本，用来测试是否能正常加载</p>
  </div>
</template>

<script>
export default {
  name: 'MinimalPurchaseOrders',
  data() {
    return {
      orders: [],
      newOrder: {
        items: []
      }
    }
  },
  methods: {
    generateOrderNumber() {
      const now = new Date()
      const year = now.getFullYear().toString().slice(2)
      const month = (now.getMonth() + 1).toString().padStart(2, '0')
      const day = now.getDate().toString().padStart(2, '0')
      const hours = now.getHours().toString().padStart(2, '0')
      const minutes = now.getMinutes().toString().padStart(2, '0')
      const seconds = now.getSeconds().toString().padStart(2, '0')
      return `PO-${year}${month}${day}-${hours}${minutes}${seconds}`
    }
  }
}
</script>