<template>
  <div class="register-container">
    <div class="register-form-wrapper">
      <h2 class="register-title">用户注册</h2>
      <el-steps :active="step" align-center class="register-steps">
        <el-step title="学生身份验证" />
        <el-step title="填写注册信息" />
        <el-step title="选择兴趣分类" />
      </el-steps>

      <!-- 第一步：学生身份验证 -->
      <el-form
        v-if="step === 0"
        ref="verifyFormRef"
        :model="verifyForm"
        :rules="verifyRules"
        label-width="80px"
        class="register-form"
      >
        <el-form-item label="学校" prop="school">
          <el-select v-model="verifyForm.school" placeholder="请选择学校" filterable style="width: 100%">
            <el-option v-for="s in schoolList" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="学号" prop="studentId">
          <el-input v-model="verifyForm.studentId" placeholder="请输入真实学号" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="verifyForm.realName" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="register-button" @click="handleVerify" :loading="verifyLoading">
            验证学生身份
          </el-button>
        </el-form-item>
        <el-form-item class="login-link">
          已有账号？<router-link to="/login">立即登录</router-link>
        </el-form-item>
      </el-form>

      <!-- 第二步：填写注册信息 -->
      <el-form
        v-else-if="step === 1"
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="100px"
        class="register-form"
      >
        <el-alert type="success" :closable="false" style="margin-bottom: 16px;">
          学生身份验证通过：{{ verifyForm.school }} - {{ verifyForm.studentId }} - {{ verifyForm.realName }}
        </el-alert>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码（至少6位）" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" show-password />
        </el-form-item>
        <el-form-item class="checkbox-item">
          <el-checkbox v-model="registerForm.agree">
            我已阅读并同意
            <a href="/terms" target="_blank">《使用条款》</a>和<a href="/privacy" target="_blank">《隐私政策》</a>
          </el-checkbox>
        </el-form-item>
        <el-form-item class="button-item">
          <el-button type="primary" class="register-button" @click="goToInterests">下一步：选择兴趣</el-button>
        </el-form-item>
        <el-form-item class="button-item">
          <el-button class="register-button" @click="step = 0">返回上一步</el-button>
        </el-form-item>
      </el-form>

      <!-- 第三步：选择兴趣分类 -->
      <div v-else-if="step === 2" class="register-form">
        <p class="interest-hint">选择你感兴趣的商品分类，我们将为你推荐相关商品（可多选）</p>
        <div class="interest-grid">
          <div
            v-for="cat in categoryList"
            :key="cat.id"
            class="interest-item"
            :class="{ selected: selectedInterests.includes(cat.id) }"
            @click="toggleInterest(cat.id)"
          >
            <span class="interest-name">{{ cat.name }}</span>
          </div>
        </div>
        <div class="interest-actions">
          <el-button type="primary" class="register-button" @click="handleRegister" :loading="loading">
            完成注册
          </el-button>
          <el-button class="register-button" @click="handleRegister" :loading="loading">
            跳过，直接注册
          </el-button>
          <el-button class="register-button" @click="step = 1">返回上一步</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { ElMessage } from 'element-plus'
import authAPI from '../../services/authAPI'
import categoryAPI from '../../services/categoryAPI'

const router = useRouter()
const userStore = useUserStore()
const registerFormRef = ref(null)
const verifyFormRef = ref(null)
const loading = ref(false)
const verifyLoading = ref(false)
const step = ref(0)
const schoolList = ref([])
const categoryList = ref([])
const selectedInterests = ref([])

const verifyForm = reactive({
  school: '',
  studentId: '',
  realName: ''
})

const verifyRules = {
  school: [{ required: true, message: '请选择学校', trigger: 'change' }],
  studentId: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }]
}

const registerForm = reactive({
  phone: '',
  email: '',
  password: '',
  confirmPassword: '',
  username: '',
  agree: false
})

const registerRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度2-20位', trigger: 'blur' }
  ]
}

onMounted(async () => {
  try {
    const res = await authAPI.getSchools()
    schoolList.value = res.data
  } catch (e) {
    console.error('获取学校列表失败:', e)
  }
  try {
    const res = await categoryAPI.getCategories()
    categoryList.value = res.data || []
  } catch (e) {
    console.error('获取分类列表失败:', e)
  }
})

const handleVerify = async () => {
  if (!verifyFormRef.value) return
  verifyFormRef.value.validate(async (valid) => {
    if (valid) {
      verifyLoading.value = true
      try {
        const res = await authAPI.verifyStudent({
          school: verifyForm.school,
          studentId: verifyForm.studentId,
          realName: verifyForm.realName
        })
        if (res.data.verified) {
          ElMessage.success('学生身份验证通过')
          step.value = 1
        } else {
          ElMessage.error(res.data.msg || '验证失败')
        }
      } catch (e) {
        ElMessage.error('验证请求失败，请稍后重试')
      } finally {
        verifyLoading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  loading.value = true
  try {
    await userStore.register({
      phone: registerForm.phone,
      email: registerForm.email,
      password: registerForm.password,
      username: registerForm.username,
      school: verifyForm.school,
      studentId: verifyForm.studentId,
      interests: selectedInterests.value
    })
    ElMessage.success('注册成功，欢迎加入！')
    setTimeout(() => { router.replace('/') }, 300)
  } catch (err) {
    const msg = err?.response?.data?.msg || err?.response?.data?.message || '注册失败，请稍后重试'
    ElMessage.error(msg)
    console.error('注册失败:', err)
  } finally {
    loading.value = false
  }
}

const toggleInterest = (catId) => {
  const idx = selectedInterests.value.indexOf(catId)
  if (idx === -1) {
    selectedInterests.value.push(catId)
  } else {
    selectedInterests.value.splice(idx, 1)
  }
}

const goToInterests = () => {
  if (!registerFormRef.value) return
  registerFormRef.value.validate((valid) => {
    if (valid) {
      if (!registerForm.agree) {
        ElMessage.warning('请阅读并同意使用条款和隐私政策')
        return
      }
      step.value = 2
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.register-form-wrapper {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 16px var(--black-alpha-10);
  width: 100%;
  max-width: 500px;
}

.register-title {
  text-align: center;
  color: var(--primary-color);
  margin-bottom: 16px;
  font-size: 24px;
  font-weight: bold;
}

.register-steps {
  margin-bottom: 24px;
}

.register-steps :deep(.el-step__title) {
  font-weight: 500;
}

.register-steps :deep(.el-step:nth-child(1) .el-step__title) {
  color: #52c41a !important;
}

.register-steps :deep(.el-step:nth-child(2) .el-step__title) {
  color: #73d13d !important;
}

.register-steps :deep(.el-step:nth-child(3) .el-step__title) {
  color: #95de64 !important;
}

.register-steps :deep(.el-step__title.is-process) {
  font-weight: 600;
}

.register-steps :deep(.el-step__title.is-wait) {
  opacity: 0.6;
}

.register-form {
  width: 100%;
}

.register-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.button-item {
  margin-bottom: 12px;
}

.button-item :deep(.el-form-item__content) {
  margin-left: 0 !important;
}

.checkbox-item :deep(.el-form-item__content) {
  margin-left: 0 !important;
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

/* 兴趣选择 */
.interest-hint {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}

.interest-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.interest-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border: 2px solid var(--border-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: var(--bg-secondary);
}

.interest-item:hover {
  border-color: var(--primary-color);
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
}

.interest-item.selected {
  border-color: var(--primary-color);
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
  color: var(--primary-color);
  font-weight: 600;
}

.interest-name {
  font-size: 14px;
}

.interest-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.interest-actions .el-button {
  width: 100% !important;
  margin: 0 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-form-wrapper {
    padding: 30px;
  }
  
  .register-title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .register-button {
    padding: 10px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .register-form-wrapper {
    padding: 20px;
  }
  
  .register-title {
    font-size: 18px;
  }
  
  .el-form-item {
    margin-bottom: 12px;
  }
  
  .el-form-item__label {
    font-size: 12px;
    width: 70px;
  }
  
  .el-form-item__content {
    margin-left: 80px !important;
  }
}
</style>
