<template>
  <div class="about-container">
    <h2 class="page-title">关于我们</h2>
    
    <div class="about-content">
      <!-- 平台介绍 -->
      <div class="about-section">
        <h3 class="section-title">平台介绍</h3>
        <p class="section-content">
          校园二手交易平台是一个专为在校学生打造的二手物品交易服务平台，致力于为学生提供安全、便捷、高效的二手交易环境。
        </p>
        <p class="section-content">
          我们的平台旨在减少资源浪费，促进校园内物品的循环利用，同时为学生提供一个经济实惠的购物渠道。
        </p>
        <p class="section-content">
          通过我们的平台，您可以轻松发布、浏览和购买二手商品，享受便捷的交易体验。
        </p>
      </div>
      
      <!-- 我们的优势 -->
      <div class="about-section">
        <h3 class="section-title">我们的优势</h3>
        <div class="advantages-grid">
          <div class="advantage-item">
            <div class="advantage-icon">
              <el-icon><i class="el-icon-safety-certificate"></i></el-icon>
            </div>
            <h4 class="advantage-title">安全可靠</h4>
            <p class="advantage-description">
              严格的用户认证机制，确保交易双方身份真实可信
            </p>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">
              <el-icon><i class="el-icon-lightning"></i></el-icon>
            </div>
            <h4 class="advantage-title">便捷高效</h4>
            <p class="advantage-description">
              简洁的操作界面，快速发布和浏览商品
            </p>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">
              <el-icon><i class="el-icon-position"></i></el-icon>
            </div>
            <h4 class="advantage-title">校园本地化</h4>
            <p class="advantage-description">
              基于校园地理位置，方便线下交易
            </p>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">
              <el-icon><i class="el-icon-chat-dot-round"></i></el-icon>
            </div>
            <h4 class="advantage-title">即时通讯</h4>
            <p class="advantage-description">
              内置聊天功能，方便买卖双方沟通
            </p>
          </div>
        </div>
      </div>
      
      <!-- 团队介绍 -->
      <div class="about-section">
        <h3 class="section-title">团队介绍</h3>
        <div class="team-grid">
          <div class="team-member">
            <div class="member-avatar">
              <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=professional%20team%20member%20avatar&image_size=square" alt="团队成员" />
            </div>
            <h4 class="member-name">张三</h4>
            <p class="member-role">前端开发</p>
            <p class="member-description">
              负责平台前端界面开发，专注于用户体验
            </p>
          </div>
          <div class="team-member">
            <div class="member-avatar">
              <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=professional%20team%20member%20avatar%202&image_size=square" alt="团队成员" />
            </div>
            <h4 class="member-name">李四</h4>
            <p class="member-role">后端开发</p>
            <p class="member-description">
              负责平台后端系统开发，确保系统稳定运行
            </p>
          </div>
          <div class="team-member">
            <div class="member-avatar">
              <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=professional%20team%20member%20avatar%203&image_size=square" alt="团队成员" />
            </div>
            <h4 class="member-name">王五</h4>
            <p class="member-role">产品设计</p>
            <p class="member-description">
              负责产品规划和用户界面设计
            </p>
          </div>
        </div>
      </div>
      
      <!-- 联系方式 -->
      <div class="about-section">
        <h3 class="section-title">联系方式</h3>
        <div class="contact-info">
          <div class="contact-item">
            <el-icon class="contact-icon"><i class="el-icon-message"></i></el-icon>
            <span class="contact-label">邮箱：</span>
            <span class="contact-value">contact@campustrade.com</span>
          </div>
          <div class="contact-item">
            <el-icon class="contact-icon"><i class="el-icon-phone"></i></el-icon>
            <span class="contact-label">电话：</span>
            <span class="contact-value">123-4567-8910</span>
          </div>
          <div class="contact-item">
            <el-icon class="contact-icon"><i class="el-icon-chat-line-round"></i></el-icon>
            <span class="contact-label">微信：</span>
            <span class="contact-value">CampusTrade</span>
          </div>
          <div class="contact-item">
            <el-icon class="contact-icon"><i class="el-icon-location"></i></el-icon>
            <span class="contact-label">地址：</span>
            <span class="contact-value">某某大学科技园A座1001室</span>
          </div>
        </div>
      </div>
      
      <!-- 加入我们 -->
      <div class="about-section">
        <h3 class="section-title">加入我们</h3>
        <p class="section-content">
          我们欢迎有才华、有热情的同学加入我们的团队，共同建设更好的校园二手交易平台。
        </p>
        <p class="section-content">
          如果您对前端开发、后端开发、产品设计等岗位感兴趣，欢迎联系我们。
        </p>
        <el-button type="primary" class="join-button">
          立即申请
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // 页面加载时的处理
})
</script>

<style scoped>
.about-container {
  padding: 20px 0;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-primary);
  text-align: center;
}

.about-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px var(--black-alpha-10);
}

.about-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 20px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-secondary);
  padding-bottom: 10px;
}

.section-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 15px;
  text-align: justify;
}

/* 优势网格 */
.advantages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.advantage-item {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 25px;
  text-align: center;
  transition: all 0.3s;
}

.advantage-item:hover {
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
  transform: translateY(-5px);
  box-shadow: 0 4px 16px var(--black-alpha-10);
}

.advantage-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  margin: 0 auto 15px;
}

.advantage-title {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 10px;
  color: var(--text-primary);
}

.advantage-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

/* 团队网格 */
.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 30px;
  margin-top: 20px;
}

.team-member {
  text-align: center;
}

.member-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 15px;
  box-shadow: 0 4px 12px var(--black-alpha-10);
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.member-name {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 5px;
  color: var(--text-primary);
}

.member-role {
  font-size: 14px;
  color: var(--primary-color);
  margin: 0 0 10px;
}

.member-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

/* 联系方式 */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.contact-icon {
  font-size: 20px;
  color: var(--primary-color);
  width: 24px;
  text-align: center;
}

.contact-label {
  font-size: 14px;
  color: var(--text-secondary);
  width: 80px;
}

.contact-value {
  font-size: 14px;
  color: var(--text-primary);
  flex: 1;
}

/* 加入我们 */
.join-button {
  margin-top: 20px;
  padding: 10px 30px;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .about-content {
    padding: 20px;
  }
  
  .about-section {
    margin-bottom: 30px;
  }
  
  .section-title {
    font-size: 16px;
    margin-bottom: 15px;
  }
  
  .advantages-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .advantage-item {
    padding: 20px;
  }
  
  .team-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
  
  .member-avatar {
    width: 100px;
    height: 100px;
  }
  
  .contact-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .contact-label {
    width: auto;
  }
}

@media (max-width: 480px) {
  .about-content {
    padding: 15px;
  }
  
  .team-grid {
    grid-template-columns: 1fr;
  }
  
  .member-avatar {
    width: 80px;
    height: 80px;
  }
  
  .join-button {
    width: 100%;
  }
}
</style>
