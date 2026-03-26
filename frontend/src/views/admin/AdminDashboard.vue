<template>
  <div class="admin-dashboard">
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :span="6" v-for="item in summaryStats" :key="item.label">
          <el-card shadow="hover" class="stat-card">
            <template #header>
              <div class="card-header">
                <span>{{ item.label }}</span>
                <el-tag :type="item.trend > 0 ? 'success' : 'danger'" size="small">
                  {{ item.trend > 0 ? '+' : '' }}{{ item.trend }}%
                </el-tag>
              </div>
            </template>
            <div class="stat-value">{{ item.value }}</div>
            <div class="stat-footer">{{ item.diff }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="dashboard-charts">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="never">
            <template #header><span>商品均价趋势 (近30日)</span></template>
            <v-chart class="chart" :option="lineOption" autoresize />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never">
            <template #header><span>商品品类分布</span></template>
            <v-chart class="chart" :option="pieOption" autoresize />
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="dashboard-bottom">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card header="最新操作日志" shadow="never">
            <el-table :data="recentLogs" stripe style="width: 100%">
              <el-table-column prop="time" label="操作时间" width="180" />
              <el-table-column prop="user" label="操作人" width="120" />
              <el-table-column prop="action" label="动作" width="120">
                <template #default="scope">
                  <el-tag :type="getActionTag(scope.row.action)">{{ scope.row.action }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="target" label="操作对象" />
              <el-table-column prop="ip" label="IP地址" width="150" />
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card header="告警通知" shadow="never">
            <el-timeline>
              <el-timeline-item
                v-for="(activity, index) in alerts"
                :key="index"
                :type="activity.type"
                :timestamp="activity.timestamp"
              >
                {{ activity.content }}
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import adminAPI from '../../services/adminAPI'
import statsAPI from '../../services/statsAPI'

use([PieChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

// 获取 CSS 变量值的辅助函数
const getCSSVar = (varName) => {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
}

const loading = ref(false)

const summaryStats = ref([
  { label: '总用户数', value: '0', trend: 0, diff: '-' },
  { label: '在售商品', value: '0', trend: 0, diff: '-' },
  { label: '总订单数', value: '0', trend: 0, diff: '-' },
  { label: '待审核商品', value: '0', trend: 0, diff: '-' }
])

const alerts = ref([])
const recentLogs = ref([])
const priceTrends = ref([])
const categoryDistribution = ref([])

const lineOption = computed(() => ({
  tooltip: { trigger: 'axis', formatter: params => `${params[0].axisValue}<br/>均价: ¥${params[0].value}` },
  grid: { left: 50, right: 20, top: 10, bottom: 30 },
  xAxis: { type: 'category', data: priceTrends.value.map(i => i.date.slice(5)), boundaryGap: false, axisLine: { lineStyle: { color: getCSSVar('--border-secondary') } }, axisLabel: { color: getCSSVar('--text-secondary') } },
  yAxis: { type: 'value', axisLabel: { color: getCSSVar('--text-secondary'), formatter: '¥{value}' }, splitLine: { lineStyle: { color: getCSSVar('--border-tertiary') } } },
  series: [{
    type: 'line',
    data: priceTrends.value.map(i => Number(i.price.toFixed(2))),
    smooth: true,
    symbol: 'circle',
    symbolSize: 5,
    lineStyle: { width: 2.5, color: getCSSVar('--primary-color') },
    itemStyle: { color: getCSSVar('--primary-color') },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: getCSSVar('--primary-alpha-20') },
          { offset: 1, color: getCSSVar('--primary-alpha-01') }
        ]
      }
    }
  }]
}))

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 件 ({d}%)' },
  legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: getCSSVar('--text-secondary'), fontSize: 12 } },
  series: [{
    type: 'pie',
    radius: ['40%', '65%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: true,
    itemStyle: { borderRadius: 5, borderColor: getCSSVar('--bg-secondary'), borderWidth: 2 },
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
    data: categoryDistribution.value
  }]
}))

const fetchDashboard = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getDashboard()
    const d = res.data
    summaryStats.value = [
      { label: '总用户数', value: String(d.total_users || 0), trend: 0, diff: `今日+${d.today_users || 0}` },
      { label: '在售商品', value: String(d.total_items || 0), trend: 0, diff: `今日+${d.today_items || 0}` },
      { label: '总订单数', value: String(d.total_orders || 0), trend: 0, diff: `今日+${d.today_orders || 0}` },
      { label: '待审核商品', value: String(d.pending_items || 0), trend: 0, diff: '需处理' }
    ]
    if (d.pending_items > 0) {
      alerts.value.push({ content: `有 ${d.pending_items} 件商品等待审核`, timestamp: '现在', type: 'warning' })
    }
  } catch (e) {
    console.error('获取仪表盘数据失败', e)
  } finally {
    loading.value = false
  }
}

const fetchLogs = async () => {
  try {
    const res = await adminAPI.getLogs({ page: 1, per_page: 10 })
    recentLogs.value = (res.data.logs || []).map(log => ({
      time: log.created_at,
      user: log.username || 'system',
      action: log.action || log.module,
      target: log.detail,
      ip: log.ip_address || '-'
    }))
  } catch (e) {
    console.error('获取日志失败', e)
  }
}

const fetchCharts = async () => {
  try {
    const [priceRes, categoryRes] = await Promise.all([
      statsAPI.getPriceTrends(),
      statsAPI.getCategoryDistribution()
    ])
    priceTrends.value = priceRes.data || []
    categoryDistribution.value = (categoryRes.data || []).map(item => ({
      name: item.name,
      value: item.value
    }))
  } catch (e) {
    console.error('获取图表数据失败', e)
  }
}

const getActionTag = (action) => {
  const map = { '删除': 'danger', '封禁': 'danger', '更新': 'warning', '审核': 'success' }
  return map[action] || 'info'
}

onMounted(() => {
  fetchDashboard()
  fetchLogs()
  fetchCharts()
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 12px 0;
}

.stat-footer {
  font-size: 12px;
  color: var(--text-tertiary);
}

.dashboard-charts {
  margin: 0;
}

.chart {
  width: 100%;
  height: 280px;
}

.dashboard-bottom {
  margin: 0;
}
</style>
