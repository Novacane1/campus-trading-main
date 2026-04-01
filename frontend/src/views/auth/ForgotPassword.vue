<template>
  <div class="forgot-password-container">
    <div class="forgot-password-form-wrapper">
      <h2 class="forgot-password-title">找回密码</h2>
      <el-form
        ref="forgotPasswordFormRef"
        :model="forgotPasswordForm"
        :rules="forgotPasswordRules"
        label-width="80px"
        class="forgot-password-form"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="forgotPasswordForm.email"
            placeholder="请输入注册时的邮箱"
            prefix-icon="el-icon-message"
            @keyup.enter="handleSubmit"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            class="submit-button"
            @click="handleSubmit"
            :loading="loading"
          >
            发送重置链接
          </el-button>
        </el-form-item>
        <el-form-item class="login-link">
          想起密码了？
          <router-link to="/login">立即登录</router-link>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import authAPI from '../../services/authAPI'

const router = useRouter()
const forgotPasswordFormRef = ref(null)
const loading = ref(false)

const forgotPasswordForm = reactive({
  email: ''
})

const forgotPasswordRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!forgotPasswordFormRef.value) return
  
  forgotPasswordFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authAPI.forgotPassword(forgotPasswordForm.email)
        ElMessage.success('重置链接已生成，请联系管理员或查看接口返回信息')
        router.push('/login')
      } catch (error) {
        console.error('发送重置链接失败:', error)
        ElMessage.error(error?.response?.data?.msg || '发送重置链接失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.forgot-password-form-wrapper {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 16px var(--black-alpha-10);
  width: 100%;
  max-width: 400px;
}

.forgot-password-title {
  text-align: center;
  color: var(--primary-color);
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: bold;
}

.forgot-password-form {
  width: 100%;
}

.submit-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: var(--text-secondary);
}

.login-link a {
  color: var(--primary-color);
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .forgot-password-form-wrapper {
    padding: 30px;
  }
  
  .forgot-password-title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .submit-button {
    padding: 10px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .forgot-password-form-wrapper {
    padding: 20px;
  }
  
  .forgot-password-title {
    font-size: 18px;
  }
}
</style>
