<template>
  <div class="contact-container">
    <h2 class="page-title">联系我们</h2>
    
    <div class="contact-content">
      <!-- 联系表单 -->
      <div class="contact-form-section">
        <h3 class="section-title">发送消息</h3>
        <div class="form-card">
          <el-form
            ref="contactFormRef"
            :model="contactForm"
            :rules="contactRules"
            label-width="80px"
          >
            <el-form-item label="姓名" prop="name">
              <el-input v-model="contactForm.name" placeholder="请输入您的姓名" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="contactForm.email" type="email" placeholder="请输入您的邮箱" />
            </el-form-item>
            <el-form-item label="电话" prop="phone">
              <el-input v-model="contactForm.phone" placeholder="请输入您的电话" />
            </el-form-item>
            <el-form-item label="主题" prop="subject">
              <el-select v-model="contactForm.subject" placeholder="请选择消息主题">
                <el-option label="功能建议" value="suggestion" />
                <el-option label="问题反馈" value="feedback" />
                <el-option label="合作咨询" value="cooperation" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="内容" prop="message">
              <el-input
                v-model="contactForm.message"
                type="textarea"
                :rows="5"
                placeholder="请输入您的消息内容"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="loading">
                提交消息
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <!-- 联系方式 -->
      <div class="contact-info-section">
        <h3 class="section-title">联系方式</h3>
        <div class="info-card">
          <div class="info-item">
            <el-icon class="info-icon"><i class="el-icon-message"></i></el-icon>
            <div class="info-content">
              <h4 class="info-title">邮箱</h4>
              <p class="info-value">contact@campustrade.com</p>
            </div>
          </div>
          <div class="info-item">
            <el-icon class="info-icon"><i class="el-icon-phone"></i></el-icon>
            <div class="info-content">
              <h4 class="info-title">电话</h4>
              <p class="info-value">123-4567-8910</p>
            </div>
          </div>
          <div class="info-item">
            <el-icon class="info-icon"><i class="el-icon-chat-line-round"></i></el-icon>
            <div class="info-content">
              <h4 class="info-title">微信</h4>
              <p class="info-value">CampusTrade</p>
            </div>
          </div>
          <div class="info-item">
            <el-icon class="info-icon"><i class="el-icon-location"></i></el-icon>
            <div class="info-content">
              <h4 class="info-title">地址</h4>
              <p class="info-value">某某大学科技园A座1001室</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 常见问题 -->
      <div class="faq-section">
        <h3 class="section-title">常见问题</h3>
        <div class="faq-card">
          <el-collapse v-model="activeFaq">
            <el-collapse-item title="如何发布二手商品？" name="1">
              <div class="faq-content">
                登录账号后，点击首页的"发布商品"按钮，填写商品信息、上传图片、选择分类和交易地点，提交后即可发布。
              </div>
            </el-collapse-item>
            <el-collapse-item title="如何修改已发布的商品信息？" name="2">
              <div class="faq-content">
                登录账号后，进入"个人中心" - "我的商品"，找到要修改的商品，点击"编辑"按钮进行修改。
              </div>
            </el-collapse-item>
            <el-collapse-item title="交易时需要注意什么？" name="3">
              <div class="faq-content">
                建议选择校园内安全的公共区域进行交易，最好在监控覆盖范围内。交易前仔细检查商品质量，确认无误后再完成交易。
              </div>
            </el-collapse-item>
            <el-collapse-item title="如何处理交易纠纷？" name="4">
              <div class="faq-content">
                如遇到交易纠纷，可通过平台消息系统与对方协商解决。若协商未果，可联系平台客服寻求帮助。
              </div>
            </el-collapse-item>
            <el-collapse-item title="账号被盗怎么办？" name="5">
              <div class="faq-content">
                立即联系平台客服冻结账号，并尽快修改密码。同时检查账号是否有异常操作，如有损失可报警处理。
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const contactFormRef = ref(null)
const loading = ref(false)
const activeFaq = ref(['1'])

const contactForm = reactive({
  name: '',
  email: '',
  phone: '',
  subject: '',
  message: ''
})

const contactRules = {
  name: [
    { required: true, message: '请输入您的姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入您的邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入您的电话', trigger: 'blur' }
  ],
  subject: [
    { required: true, message: '请选择消息主题', trigger: 'change' }
  ],
  message: [
    { required: true, message: '请输入您的消息内容', trigger: 'blur' },
    { min: 10, message: '消息内容至少10个字符', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!contactFormRef.value) return
  
  contactFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 模拟提交
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('表单提交成功:', contactForm)
        // 显示成功提示
        alert('消息发送成功，我们会尽快与您联系！')
        // 重置表单
        contactForm.name = ''
        contactForm.email = ''
        contactForm.phone = ''
        contactForm.subject = ''
        contactForm.message = ''
      } catch (error) {
        console.error('表单提交失败:', error)
        // 显示错误提示
        alert('消息发送失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.contact-container {
  padding: 20px 0;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-primary);
  text-align: center;
}

.contact-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.contact-form-section,
.contact-info-section,
.faq-section {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px var(--black-alpha-10);
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 20px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-secondary);
  padding-bottom: 10px;
}

.form-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
}

/* 联系方式 */
.info-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 8px;
  transition: all 0.3s;
}

.info-item:hover {
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
  transform: translateX(5px);
}

.info-icon {
  font-size: 24px;
  color: var(--primary-color);
  margin-top: 2px;
}

.info-content {
  flex: 1;
}

.info-title {
  font-size: 14px;
  font-weight: bold;
  margin: 0 0 5px;
  color: var(--text-primary);
}

.info-value {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* 常见问题 */
.faq-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
}

.faq-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  padding: 10px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .contact-content {
    gap: 30px;
  }
  
  .contact-form-section,
  .contact-info-section,
  .faq-section {
    padding: 20px;
  }
  
  .section-title {
    font-size: 16px;
    margin-bottom: 15px;
  }
  
  .form-card {
    padding: 15px;
  }
  
  .info-item {
    padding: 12px;
  }
  
  .info-icon {
    font-size: 20px;
  }
  
  .faq-card {
    padding: 15px;
  }
}

@media (max-width: 480px) {
  .contact-form-section,
  .contact-info-section,
  .faq-section {
    padding: 15px;
  }
  
  .el-form-item {
    margin-bottom: 15px;
  }
  
  .el-form-item__label {
    font-size: 13px;
  }
  
  .el-input {
    font-size: 13px;
  }
}
</style>
