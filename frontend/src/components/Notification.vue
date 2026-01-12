<template>
  <div class="notification" :class="[type, { show: show }]" v-if="message">
    {{ message }}
  </div>
</template>

<script>
export default {
  name: 'Notification',
  data() {
    return {
      show: false,
      message: '',
      type: 'info'
    }
  },
  methods: {
    showNotification(message, type = 'info') {
      this.message = message
      this.type = type
      this.show = true
      
      setTimeout(() => {
        this.show = false
      }, 3000)
    }
  }
}
</script>

<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  transform: translateX(120%);
  transition: transform 0.3s ease;
  transform: translateZ(0);
  will-change: transform;
  max-width: 300px;
  word-wrap: break-word;
}

.notification.success {
  background-color: var(--success-color);
}

.notification.error {
  background-color: var(--danger-color);
}

.notification.warning {
  background-color: var(--warning-color);
}

.notification.info {
  background-color: var(--info-color);
}

.notification.show {
  transform: translateX(0);
}
</style>