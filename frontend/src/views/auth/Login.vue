<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-right">
        <div class="login-form-wrapper">
          <div class="form-header">
            <h2 class="login-title">用户登录</h2>
            <p class="login-subtitle">欢迎回来，请登录您的账号</p>
          </div>
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-position="top"
            class="login-form"
            @submit.prevent
          >
            <el-form-item label="账号" prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名/手机号/邮箱/学号"
                prefix-icon="el-icon-user"
                @keyup.enter="handleLogin"
                class="auth-input"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="el-icon-lock"
                show-password
                @keyup.enter="handleLogin"
                class="auth-input"
              />
            </el-form-item>
            <div class="form-options">
              <el-checkbox v-model="loginForm.remember" class="remember-checkbox">记住我</el-checkbox>
              <router-link to="/forgot-password" class="forgot-password">忘记密码？</router-link>
            </div>
            <el-form-item>
              <el-button
                type="primary"
                class="login-button"
                @click="handleLogin"
                :loading="loading"
                native-type="button"
              >
                登录
              </el-button>
            </el-form-item>
            <div class="register-link">
              还没有账号？
              <router-link to="/register" class="register-button">立即注册</router-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  // 表单验证
  if (!loginFormRef.value) return

  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login({
          username: loginForm.username,
          password: loginForm.password,
          remember: loginForm.remember
        })
        // 登录成功，跳转到首页
        // 使用 replace 而不是 push，避免用户回退到登录页
        // 强制刷新状态，确保 Pinia 状态更新被组件感知
        // 使用 window.location.href 强制刷新页面，彻底解决路由状态不一致的问题
        const redirect = route.query.redirect
        const target = typeof redirect === 'string' && redirect.length > 0 ? redirect : '/'
        router.replace(target)
      } catch (error) {
        const msg = error?.response?.data?.message || error?.response?.data?.msg || '账号或密码错误，请重试'
        ElMessage.error(msg)
        console.error('登录失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: var(--spacing-md);
}

.login-content {
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-primary);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 500px;
  width: 100%;
  padding: var(--spacing-2xl);
}

/* 登录表单 */
.login-right {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.login-title {
  font-size: var(--font-size-2xl);
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm);
}

.login-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
}

.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.auth-input {
  border-radius: var(--border-radius-lg);
  height: 48px;
  font-size: var(--font-size-md);
}

.login-button {
  width: 100%;
  padding: var(--spacing-md);
  font-size: var(--font-size-md);
  border-radius: var(--border-radius-lg);
  transition: all var(--transition-normal);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.remember-checkbox {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.forgot-password {
  font-size: var(--font-size-sm);
  color: var(--primary-color);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.forgot-password:hover {
  color: var(--primary-hover);
}

.register-link {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.register-button {
  color: var(--primary-color);
  font-weight: 500;
  text-decoration: none;
  transition: color var(--transition-fast);
}

.register-button:hover {
  color: var(--primary-hover);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-content {
    padding: var(--spacing-lg);
  }

  .login-title {
    font-size: var(--font-size-xl);
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: var(--spacing-sm);
  }

  .login-content {
    padding: var(--spacing-md);
  }

  .login-title {
    font-size: var(--font-size-lg);
  }

  .auth-input {
    height: 44px;
    font-size: var(--font-size-sm);
  }

  .login-button {
    padding: var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
}
</style>
