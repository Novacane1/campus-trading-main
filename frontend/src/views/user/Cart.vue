<template>
  <div class="cart-page">
    <div class="page-header">
      <h2>我的购物车</h2>
      <el-button v-if="cartItems.length" type="danger" plain size="small" @click="handleClearCart">清空购物车</el-button>
    </div>

    <el-card v-loading="loading">
      <el-empty v-if="!loading && !cartItems.length" description="购物车是空的，去逛逛吧~">
        <el-button type="primary" @click="$router.push('/products')">去逛逛</el-button>
      </el-empty>

      <div v-else class="cart-list">
        <!-- 全选栏 -->
        <div class="select-all-bar">
          <el-checkbox
            v-model="isAllSelected"
            :indeterminate="isIndeterminate"
            @change="handleSelectAll"
          >全选</el-checkbox>
          <span class="available-hint">可选 {{ availableItems.length }} 件商品</span>
        </div>

        <div v-for="item in cartItems" :key="item.cart_id" class="cart-item">
          <el-checkbox
            v-model="item.selected"
            :disabled="item.status !== 'on_sale'"
            @change="handleItemSelectChange"
            class="item-checkbox"
          />
          <el-image
            class="item-image"
            :src="item.image"
            fit="cover"
            @click="$router.push(`/product/${item.item_id}`)"
          />
          <div class="item-info">
            <div class="item-title" @click="$router.push(`/product/${item.item_id}`)">{{ item.title }}</div>
            <div class="item-desc">{{ item.description }}</div>
            <div class="item-seller">卖家：{{ item.seller }}</div>
          </div>
          <div class="item-price">¥{{ item.price }}</div>
          <div class="item-actions">
            <el-button type="primary" size="small" @click="handleBuy(item)" :disabled="item.status !== 'on_sale'">
              {{ item.status === 'sold' ? '已售出' : '立即购买' }}
            </el-button>
            <el-button type="danger" size="small" plain @click="handleRemove(item)">移除</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 底部批量操作栏 -->
    <div v-if="cartItems.length" class="batch-bar">
      <div class="batch-left">
        <el-checkbox
          v-model="isAllSelected"
          :indeterminate="isIndeterminate"
          @change="handleSelectAll"
        >全选</el-checkbox>
        <span class="selected-count">已选 <b>{{ selectedItems.length }}</b> 件</span>
      </div>
      <div class="batch-right">
        <span class="total-price">合计：<b>¥{{ selectedTotalPrice }}</b></span>
        <el-button
          type="primary"
          :disabled="selectedItems.length === 0"
          @click="handleBatchBuy"
        >
          批量下单{{ selectedItems.length ? `(${selectedItems.length})` : '' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import cartAPI from '../../services/cartAPI'
import orderAPI from '../../services/orderAPI'

const router = useRouter()
const loading = ref(false)
const cartItems = ref([])

// === 多选相关计算属性 ===
const availableItems = computed(() => cartItems.value.filter(i => i.status === 'on_sale'))
const selectedItems = computed(() => cartItems.value.filter(i => i.selected))
const selectedTotalPrice = computed(() => {
  return selectedItems.value.reduce((sum, i) => sum + Number(i.price), 0).toFixed(2)
})
const isAllSelected = computed({
  get: () => availableItems.value.length > 0 && availableItems.value.every(i => i.selected),
  set: () => {}
})
const isIndeterminate = computed(() => {
  const count = availableItems.value.filter(i => i.selected).length
  return count > 0 && count < availableItems.value.length
})

const handleSelectAll = (val) => {
  cartItems.value.forEach(item => {
    if (item.status === 'on_sale') {
      item.selected = val
    }
  })
}

const handleItemSelectChange = () => {
  // 计算属性自动更新，无需额外操作
}

const fetchCart = async () => {
  loading.value = true
  try {
    const res = await cartAPI.getCart()
    const raw = res.data.items || res.data || []
    cartItems.value = raw.map(entry => ({
      cart_id: entry.id,
      item_id: entry.item_id,
      title: entry.item?.name || '未知商品',
      image: (entry.item?.images || [])[0] || '',
      price: entry.item?.price ?? 0,
      description: entry.item?.description || '',
      seller: entry.item?.seller?.username || '',
      status: entry.item?.status || 'on_sale',
      selected: false
    }))
  } catch (e) {
    ElMessage.error('获取购物车失败')
  } finally {
    loading.value = false
  }
}

const handleRemove = async (item) => {
  try {
    await cartAPI.removeFromCart(item.cart_id)
    cartItems.value = cartItems.value.filter(i => i.cart_id !== item.cart_id)
    ElMessage.success('已移除')
  } catch (e) {
    ElMessage.error('移除失败')
  }
}

const handleClearCart = () => {
  ElMessageBox.confirm('确定要清空购物车吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await cartAPI.clearCart()
        cartItems.value = []
        ElMessage.success('购物车已清空')
      } catch (e) {
        ElMessage.error('清空失败')
      }
    }).catch(() => {})
}

const handleBuy = (item) => {
  ElMessageBox.confirm(`确定要购买 "${item.title}" (¥${item.price}) 吗？`, '确认购买', { type: 'info' })
    .then(async () => {
      try {
        await orderAPI.createOrder({ item_id: item.item_id })
        await cartAPI.removeFromCart(item.cart_id)
        cartItems.value = cartItems.value.filter(i => i.cart_id !== item.cart_id)
        ElMessage.success('下单成功！')
        router.push('/orders')
      } catch (e) {
        ElMessage.error(e?.response?.data?.msg || '下单失败')
      }
    }).catch(() => {})
}

const handleBatchBuy = () => {
  const items = selectedItems.value
  if (items.length === 0) {
    ElMessage.warning('请先选择要购买的商品')
    return
  }
  const msg = `确定要批量购买 ${items.length} 件商品，合计 ¥${selectedTotalPrice.value} 吗？`
  ElMessageBox.confirm(msg, '确认批量下单', { type: 'info' })
    .then(async () => {
      try {
        const itemIds = items.map(i => i.item_id)
        const cartIds = items.map(i => i.cart_id)
        const res = await orderAPI.batchCreateOrder(itemIds)
        await cartAPI.batchRemove(cartIds)
        cartItems.value = cartItems.value.filter(i => !cartIds.includes(i.cart_id))
        const orderCount = res.data.orders?.length || items.length
        ElMessage.success(`成功下单 ${orderCount} 件商品！`)
        if (res.data.errors?.length) {
          ElMessage.warning(`${res.data.errors.length} 件商品下单失败`)
        }
        router.push('/orders')
      } catch (e) {
        ElMessage.error(e?.response?.data?.msg || '批量下单失败')
      }
    }).catch(() => {})
}

onMounted(() => {
  fetchCart()
})
</script>

<style scoped>
.cart-page { max-width: 900px; margin: 0 auto; padding: 24px; padding-bottom: 80px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; color: var(--text-primary); }
.cart-list { display: flex; flex-direction: column; gap: 16px; }
.select-all-bar { display: flex; align-items: center; gap: 12px; padding: 8px 12px; border-bottom: 1px solid var(--border-color, #eee); }
.available-hint { font-size: 12px; color: var(--text-tertiary); }
.cart-item { display: flex; align-items: center; gap: 16px; padding: 12px; border-radius: 8px; background: var(--bg-secondary, var(--bg-secondary)); }
.item-checkbox { flex-shrink: 0; }
.item-image { width: 80px; height: 80px; border-radius: 8px; cursor: pointer; flex-shrink: 0; }
.item-info { flex: 1; min-width: 0; }
.item-title { font-weight: bold; color: var(--text-primary); cursor: pointer; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-title:hover { color: var(--el-color-primary); }
.item-desc { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-seller { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.item-price { font-size: 18px; font-weight: bold; color: var(--danger-color); white-space: nowrap; }
.item-actions { display: flex; gap: 8px; flex-shrink: 0; }
.batch-bar {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 24px; background: var(--bg-primary, #fff);
  border-top: 1px solid var(--border-color, #eee);
  box-shadow: 0 -2px 8px rgba(0,0,0,0.06);
}
.batch-left { display: flex; align-items: center; gap: 16px; }
.selected-count { font-size: 14px; color: var(--text-secondary); }
.selected-count b { color: var(--el-color-primary); }
.batch-right { display: flex; align-items: center; gap: 16px; }
.total-price { font-size: 16px; color: var(--text-primary); }
.total-price b { color: var(--danger-color); font-size: 20px; }
</style>
