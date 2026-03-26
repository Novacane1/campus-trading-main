<template>
  <div class="announcements-page">
    <div class="page-header">
      <h1>平台公告</h1>
      <p>了解最新的平台动态和重要通知</p>
    </div>

    <div class="announcements-list" v-loading="loading">
      <div v-if="announcements.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无公告" />
      </div>

      <div v-for="ann in announcements" :key="ann.id" class="announcement-card" @click="showDetail(ann)">
        <div class="card-header">
          <div class="card-tags">
            <el-tag v-if="ann.priority === 'urgent'" type="danger" size="small">紧急</el-tag>
            <el-tag v-else-if="ann.priority === 'high'" type="warning" size="small">重要</el-tag>
            <el-tag v-else type="info" size="small">公告</el-tag>
          </div>
          <span class="card-time">{{ formatTime(ann.publish_time) }}</span>
        </div>
        <h3 class="card-title">{{ ann.title }}</h3>
        <p class="card-content">{{ ann.content }}</p>
        <div class="card-footer">
          <span class="publisher">发布者: {{ ann.publisher_name || '管理员' }}</span>
        </div>
      </div>

      <div class="pagination-container" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          layout="prev, pager, next"
          :total="total"
          @current-change="fetchAnnouncements"
        />
      </div>
    </div>

    <!-- 公告详情对话框 -->
    <el-dialog v-model="detailVisible" :title="currentAnnouncement.title" width="600px">
      <div class="detail-meta">
        <el-tag v-if="currentAnnouncement.priority === 'urgent'" type="danger" size="small">紧急</el-tag>
        <el-tag v-else-if="currentAnnouncement.priority === 'high'" type="warning" size="small">重要</el-tag>
        <span>发布时间: {{ currentAnnouncement.publish_time }}</span>
        <span>发布者: {{ currentAnnouncement.publisher_name || '管理员' }}</span>
      </div>
      <el-divider />
      <div class="detail-content">{{ currentAnnouncement.content }}</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import announcementAPI from '../services/announcementAPI'

const loading = ref(false)
const announcements = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const detailVisible = ref(false)
const currentAnnouncement = ref({})

const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const res = await announcementAPI.getAnnouncements({
      page: currentPage.value,
      limit: pageSize.value
    })
    announcements.value = res.data.announcements || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('获取公告失败:', e)
  } finally {
    loading.value = false
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const showDetail = (ann) => {
  currentAnnouncement.value = ann
  detailVisible.value = true
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.announcements-page {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.page-header p {
  color: var(--text-secondary);
}

.announcement-card {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  border: 1px solid var(--border-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.announcement-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.card-time {
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
}

.card-title {
  font-size: 18px;
  margin: 0 0 var(--spacing-sm);
  color: var(--text-primary);
}

.card-content {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--border-secondary);
}

.publisher {
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-xl);
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.detail-content {
  white-space: pre-wrap;
  line-height: 1.8;
  color: var(--text-primary);
}

.empty-state {
  padding: var(--spacing-2xl);
}
</style>
