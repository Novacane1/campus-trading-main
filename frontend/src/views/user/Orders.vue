<template>
  <div class="orders-page">
    <h2>订单管理</h2>
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="我买到的" name="buy" />
      <el-tab-pane label="我卖出的" name="sell" />
    </el-tabs>

    <el-card v-loading="loading">
      <el-empty v-if="!loading && !orders.length" description="暂无订单">
        <el-button type="primary" @click="$router.push('/products')">去逛逛</el-button>
      </el-empty>

      <div v-else class="order-list">
        <div v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-header">
            <span class="order-id">订单号: {{ order.id }}</span>
            <span class="order-time">{{ formatOrderTime(order.created_at) }}</span>
            <el-tag :type="statusType(order.status)" size="small">{{ statusText(order.status) }}</el-tag>
          </div>
          <div class="order-body" @click="$router.push(`/product/${order.item_id}`)">
            <el-image class="order-img" :src="order.item_image" fit="cover" />
            <div class="order-info">
              <div class="order-title">{{ order.item_title }}</div>
              <div class="order-meta">
                <span v-if="activeTab === 'buy'">卖家: {{ order.seller_name }}</span>
                <span v-else>买家: {{ order.buyer_name }}</span>
              </div>
            </div>
            <div class="order-price">¥{{ order.total_price }}</div>
          </div>
          <div class="order-footer">
            <template v-if="activeTab === 'buy'">
              <span v-if="order.status === 'pending' && countdowns[order.id]" class="countdown">
                剩余支付时间：{{ countdowns[order.id] }}
              </span>
              <el-button
                v-if="order.status === 'pending' && !expiredOrderIds[order.id]"
                size="small"
                type="primary"
                :loading="payingOrderId === order.id"
                @click="payOrder(order)"
              >
                去付款
              </el-button>
              <el-button v-if="order.status === 'shipped'" size="small" type="success" @click="confirmReceive(order)">确认收货</el-button>
              <el-button
                v-if="order.status === 'pending'"
                size="small"
                :disabled="payingOrderId === order.id"
                @click="cancelOrder(order)"
              >
                取消订单
              </el-button>
              <el-button v-if="order.status === 'completed' && !reviewStatuses[order.id]" size="small" type="warning" @click="openReview(order)">去评价</el-button>
              <el-tag v-if="order.status === 'completed' && reviewStatuses[order.id]" type="success" size="small">已评价</el-tag>
            </template>
            <template v-if="activeTab === 'sell'">
              <el-button v-if="order.status === 'paid'" size="small" type="primary" @click="shipOrder(order)">确认发货</el-button>
              <el-button v-if="order.status === 'completed' && !reviewStatuses[order.id]" size="small" type="warning" @click="openReview(order)">去评价</el-button>
              <el-tag v-if="order.status === 'completed' && reviewStatuses[order.id]" type="success" size="small">已评价</el-tag>
            </template>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 评价弹窗 -->
    <ReviewForm
      v-model="showReviewDialog"
      :order-id="currentReviewOrderId"
      @success="onReviewSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import orderAPI from '../../services/orderAPI'
import ReviewForm from '../../components/ReviewForm.vue'
import { getReviewStatus } from '../../services/reviewAPI'

const route = useRoute()
const router = useRouter()
const activeTab = ref('buy')
const loading = ref(false)
const orders = ref([])
const countdowns = ref({})
const expiredOrderIds = ref({})
const reviewStatuses = ref({})
const showReviewDialog = ref(false)
const currentReviewOrderId = ref('')
const payingOrderId = ref('')
let countdownTimer = null

const parseServerDate = (value) => {
  if (!value || typeof value !== 'string') return null
  const normalized = /([zZ]|[+-]\d{2}:?\d{2})$/.test(value) ? value : `${value}Z`
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

const formatOrderTime = (value) => {
  const date = parseServerDate(value)
  if (!date) return value || '-'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

const updateCountdowns = () => {
  const now = Date.now()
  orders.value.forEach(order => {
    if (order.status === 'pending' && order.expire_time) {
      const expireAt = parseServerDate(order.expire_time)
      if (!expireAt) {
        countdowns.value[order.id] = ''
        return
      }
      const remaining = expireAt.getTime() - now
      if (remaining <= 0) {
        countdowns.value[order.id] = '已超时'
        expiredOrderIds.value[order.id] = true
      } else {
        const m = Math.floor(remaining / 60000)
        const s = Math.floor((remaining % 60000) / 1000)
        countdowns.value[order.id] = `${m}:${String(s).padStart(2, '0')}`
        delete expiredOrderIds.value[order.id]
      }
    }
  })
}

const startCountdown = () => {
  updateCountdowns()
  countdownTimer = setInterval(updateCountdowns, 1000)
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const res = activeTab.value === 'buy'
      ? await orderAPI.getMyOrders()
      : await orderAPI.getMySales()
    orders.value = res.data.orders || res.data || []
    expiredOrderIds.value = {}
    if (countdownTimer) clearInterval(countdownTimer)
    startCountdown()
    // 检查已完成订单的评价状态
    await fetchReviewStatuses()
  } catch (e) {
    ElMessage.error('获取订单失败')
  } finally {
    loading.value = false
  }
}

const fetchReviewStatuses = async () => {
  const completedOrders = orders.value.filter(o => o.status === 'completed')
  for (const order of completedOrders) {
    try {
      const res = await getReviewStatus(order.id)
      reviewStatuses.value[order.id] = !res.data.can_review
    } catch {
      reviewStatuses.value[order.id] = false
    }
  }
}

const openReview = (order) => {
  currentReviewOrderId.value = String(order.id)
  showReviewDialog.value = true
}

const onReviewSuccess = () => {
  reviewStatuses.value[currentReviewOrderId.value] = true
  ElMessage.success('评价成功！')
}

const handleTabChange = () => { fetchOrders() }

const statusType = (s) => {
  const m = { pending: 'warning', paid: 'primary', shipped: '', completed: 'success', cancelled: 'info' }
  return m[s] || 'info'
}
const statusText = (s) => {
  const m = { pending: '待付款', paid: '已付款', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
  return m[s] || s
}

const submitPaymentForm = (paymentForm) => {
  const container = document.createElement('div')
  container.innerHTML = paymentForm
  const form = container.querySelector('form')
  if (!form) {
    throw new Error('支付表单生成失败')
  }

  form.style.display = 'none'
  form.setAttribute('target', '_self')
  document.body.appendChild(form)
  form.submit()
}

const submitLaunchForm = (orderId) => {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('登录状态已失效，请重新登录')
  }

  const form = document.createElement('form')
  form.method = 'POST'
  form.action = '/api/payments/alipay/launch'
  form.target = '_self'
  form.style.display = 'none'

  const orderInput = document.createElement('input')
  orderInput.type = 'hidden'
  orderInput.name = 'order_id'
  orderInput.value = orderId
  form.appendChild(orderInput)

  const tokenInput = document.createElement('input')
  tokenInput.type = 'hidden'
  tokenInput.name = 'token'
  tokenInput.value = token
  form.appendChild(tokenInput)

  document.body.appendChild(form)
  form.submit()
}

const payOrder = async (order) => {
  payingOrderId.value = order.id
  try {
    submitLaunchForm(order.id)
  } catch (e) {
    ElMessage.error(e?.response?.data?.msg || '发起支付失败')
  } finally {
    payingOrderId.value = ''
  }
}

const confirmReceive = async (order) => {
  try {
    await orderAPI.confirmOrder(order.id)
    order.status = 'completed'
    ElMessage.success('已确认收货')
  } catch (e) { ElMessage.error('操作失败') }
}

const cancelOrder = (order) => {
  ElMessageBox.confirm('确定取消该订单吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await orderAPI.updateOrderStatus(order.id, 'cancelled')
        order.status = 'cancelled'
        ElMessage.success('订单已取消')
      } catch (e) { ElMessage.error('取消失败') }
    }).catch(() => {})
}

const shipOrder = async (order) => {
  try {
    await orderAPI.updateOrderStatus(order.id, 'shipped')
    order.status = 'shipped'
    ElMessage.success('已确认发货')
  } catch (e) { ElMessage.error('操作失败') }
}

const handleAlipayReturn = async () => {
  const orderId = route.query.order_id
  if (route.query.alipay_return !== '1' || !orderId) {
    return
  }

  try {
    let latestStatus = ''
    for (let attempt = 0; attempt < 3; attempt += 1) {
      const res = await orderAPI.syncAlipayOrderStatus(orderId)
      latestStatus = res.data?.order?.status || ''
      if (latestStatus && latestStatus !== 'pending') {
        break
      }
      if (attempt < 2) {
        await new Promise(resolve => setTimeout(resolve, 1500))
      }
    }

    await fetchOrders()

    if (latestStatus === 'paid' || latestStatus === 'shipped' || latestStatus === 'completed') {
      ElMessage.success('支付结果已同步')
    } else if (latestStatus === 'cancelled') {
      ElMessage.warning('订单已关闭')
    } else {
      ElMessage.info('支付结果同步中，请稍后刷新订单列表')
    }
  } catch (e) {
    ElMessage.warning(e?.response?.data?.msg || '未能立即同步支付结果，请稍后刷新')
  } finally {
    router.replace({ path: route.path, query: {} }).catch(() => {})
  }
}

onMounted(async () => {
  await fetchOrders()
  await handleAlipayReturn()
})
onUnmounted(() => { if (countdownTimer) clearInterval(countdownTimer) })
</script>

<style scoped>
.orders-page { max-width: 900px; margin: 0 auto; padding: var(--spacing-lg); }
.orders-page h2 { color: var(--text-primary); margin-bottom: var(--spacing-md); }
.order-list { display: flex; flex-direction: column; gap: var(--spacing-md); }
.order-card { border: 1px solid var(--border-secondary); border-radius: var(--border-radius-lg); overflow: hidden; background: var(--bg-primary); transition: box-shadow var(--transition-normal); }
.order-card:hover { box-shadow: var(--shadow-sm); }
.order-header { display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: var(--bg-secondary); font-size: 13px; color: var(--text-tertiary); border-bottom: 1px solid var(--border-secondary); }
.order-id { font-weight: bold; color: var(--text-primary); }
.order-time { flex: 1; }
.order-body { display: flex; align-items: center; gap: 16px; padding: 16px; cursor: pointer; transition: background var(--transition-fast); }
.order-body:hover { background: var(--bg-secondary); }
.order-img { width: 64px; height: 64px; border-radius: var(--border-radius-md); flex-shrink: 0; }
.order-info { flex: 1; min-width: 0; }
.order-title { font-weight: bold; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.order-meta { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; }
.order-price { font-size: 18px; font-weight: bold; color: var(--danger-color); white-space: nowrap; }
.order-footer { display: flex; justify-content: flex-end; align-items: center; gap: 8px; padding: 10px 16px; border-top: 1px solid var(--border-secondary); background: var(--bg-secondary); }
.countdown { font-size: 13px; color: var(--warning-color); margin-right: auto; font-weight: 500; }
</style>
