<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1 class="error-title">页面不存在</h1>
      <p class="error-message">
        抱歉，您访问的页面不存在或已被删除。
      </p>
      <div class="error-actions">
        <router-link to="/" class="action-button home-button">
          返回首页
        </router-link>
        <button class="action-button back-button" @click="goBack">
          返回上一页
        </button>
      </div>
      <div class="error-suggestions">
        <h3 class="suggestions-title">您可以尝试：</h3>
        <ul class="suggestions-list">
          <li>检查网址是否输入正确</li>
          <li>返回首页浏览商品</li>
          <li>使用搜索功能查找内容</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}

onMounted(() => {
  // 可以添加页面统计代码等
})
</script>

<style scoped>
.not-found-container {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  padding: 40px 20px;
}

.not-found-content {
  background: white;
  border-radius: 12px;
  padding: 60px;
  text-align: center;
  box-shadow: 0 8px 32px var(--black-alpha-10);
  max-width: 600px;
  width: 100%;
  animation: fadeIn 0.5s ease-in-out;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: var(--primary-color);
  margin: 0 0 20px;
  line-height: 1;
}

.error-title {
  font-size: 32px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 15px;
}

.error-message {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0 0 40px;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 40px;
}

.action-button {
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s;
  border: 1px solid transparent;
  cursor: pointer;
}

.home-button {
  background: var(--primary-color);
  color: white;
}

.home-button:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--primary-alpha-30);
}

.back-button {
  background: white;
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.back-button:hover {
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
  transform: translateY(-2px);
}

.error-suggestions {
  text-align: left;
  border-top: 1px solid var(--border-secondary);
  padding-top: 30px;
}

.suggestions-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 15px;
}

.suggestions-list {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 0 20px;
  line-height: 1.6;
}

.suggestions-list li {
  margin-bottom: 8px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .not-found-content {
    padding: 40px;
  }
  
  .error-code {
    font-size: 90px;
  }
  
  .error-title {
    font-size: 24px;
  }
  
  .error-message {
    font-size: 14px;
    margin-bottom: 30px;
  }
  
  .error-actions {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 30px;
  }
  
  .action-button {
    width: 100%;
    max-width: 200px;
    margin: 0 auto;
  }
  
  .error-suggestions {
    padding-top: 20px;
  }
}

@media (max-width: 480px) {
  .not-found-container {
    min-height: calc(100vh - 80px);
    padding: 20px 15px;
  }
  
  .not-found-content {
    padding: 30px 20px;
  }
  
  .error-code {
    font-size: 70px;
  }
  
  .error-title {
    font-size: 20px;
  }
  
  .error-message {
    font-size: 13px;
  }
  
  .suggestions-title {
    font-size: 14px;
  }
  
  .suggestions-list {
    font-size: 13px;
    margin-left: 15px;
  }
}
</style>
