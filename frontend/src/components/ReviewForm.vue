<template>
  <el-dialog v-model="visible" title="评价交易" width="500px" @close="handleClose">
    <el-form :model="form" label-width="80px">
      <el-form-item label="评分">
        <el-rate v-model="form.rating" show-text :texts="['很差', '较差', '一般', '满意', '非常满意']" />
      </el-form-item>
      <el-form-item label="评价内容">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="4"
          placeholder="请输入您的评价（选填）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="匿名评价">
        <el-switch v-model="form.is_anonymous" />
        <span class="anonymous-tip">开启后对方将看不到您的用户名</span>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        提交评价
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { createReview } from '@/services/reviewAPI'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean,
  orderId: String
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(false)
const submitting = ref(false)

const form = reactive({
  rating: 5,
  content: '',
  is_anonymous: false
})

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleClose = () => {
  visible.value = false
  form.rating = 5
  form.content = ''
  form.is_anonymous = false
}

const handleSubmit = async () => {
  if (form.rating < 1) {
    ElMessage.warning('请选择评分')
    return
  }

  submitting.value = true
  try {
    await createReview({
      order_id: props.orderId,
      rating: form.rating,
      content: form.content,
      is_anonymous: form.is_anonymous
    })
    ElMessage.success('评价成功')
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '评价失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.anonymous-tip {
  margin-left: 10px;
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
