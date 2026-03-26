<template>
  <div class="market-trends-container">
    <div class="header-section">
      <h2 class="page-title">校园二手市场行情面板</h2>
      <p class="page-subtitle">实时统计全校商品分布及价格走势，助您掌握市场动态</p>
    </div>

    <!-- 核心指标 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in marketStats" :key="stat.label">
        <div class="stat-main">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
        <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
          <el-icon><CaretTop v-if="stat.trend > 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(stat.trend) }}%
        </div>
      </div>
    </div>

    <div class="main-charts">
      <!-- 品类占比 - ECharts 饼图 -->
      <div class="chart-box category-distribution">
        <div class="box-header">
          <h3 class="box-title">各品类商品占比</h3>
          <el-tooltip content="统计系统内所有在售商品的分类比例" placement="top">
            <el-icon class="info-icon"><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <v-chart class="chart" :option="pieOption" autoresize />
      </div>

      <!-- 价格走势 - ECharts 折线图 -->
      <div class="chart-box price-trends">
        <div class="box-header">
          <h3 class="box-title">商品均价走势 (近30日)</h3>
        </div>
        <v-chart class="chart" :option="lineOption" autoresize />
      </div>
    </div>

    <!-- 供需对比 - ECharts 柱状图 -->
    <div class="chart-box supply-demand-section">
      <div class="box-header">
        <h3 class="box-title">供需对比 (近7日)</h3>
        <el-tooltip content="对比每日新增商品数量与新增订单数量" placement="top">
          <el-icon class="info-icon"><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
      <v-chart class="chart" :option="barOption" autoresize />
    </div>

    <!-- 新增：价格分布直方图 -->
    <div class="chart-box price-distribution-section">
      <div class="box-header">
        <h3 class="box-title">价格区间分布</h3>
        <el-tooltip content="展示不同价格区间的商品数量分布" placement="top">
          <el-icon class="info-icon"><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
      <v-chart class="chart" :option="histogramOption" autoresize />
    </div>

    <!-- 新增：品类平均价格对比 -->
    <div class="chart-box category-price-section">
      <div class="box-header">
        <h3 class="box-title">各品类平均价格对比</h3>
        <el-tooltip content="横向对比各品类商品的平均价格" placement="top">
          <el-icon class="info-icon"><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
      <v-chart class="chart" :option="categoryPriceOption" autoresize />
    </div>

    <!-- 市场洞察建议 -->
    <div class="insights-section">
      <div class="box-header">
        <h3 class="box-title">市场洞察与定价建议</h3>
      </div>
      <div class="insights-content">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>定价建议</template>
          <ul class="insights-list">
            <li>参考同类商品的平均价格进行定价</li>
            <li>关注价格走势，选择合适的发布时机</li>
            <li>价格区间分布显示了买家的购买力范围</li>
            <li>供需比例反映了市场的活跃程度</li>
          </ul>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { CaretTop, CaretBottom, InfoFilled } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, LineChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import statsAPI from '../services/statsAPI'

use([PieChart, LineChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

// 获取 CSS 变量值的辅助函数
const getCSSVar = (varName) => {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
}

const marketStats = ref([
  { label: '在售商品', value: '-', trend: 0 },
  { label: '今日新增', value: '-', trend: 0 },
  { label: '累计成交', value: '-', trend: 0 },
  { label: '市场均价', value: '-', trend: 0 }
])

const categoryDistribution = ref([])
const priceTrends = ref([])
const supplyDemand = ref([])
const priceDistribution = ref([])
const categoryPrices = ref([])

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 件 ({d}%)' },
  legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: getCSSVar('--text-secondary') } },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: true,
    itemStyle: { borderRadius: 6, borderColor: getCSSVar('--bg-secondary'), borderWidth: 2 },
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
    data: categoryDistribution.value
  }]
}))

const lineOption = computed(() => ({
  tooltip: { trigger: 'axis', formatter: params => `${params[0].axisValue}<br/>均价: ¥${params[0].value}` },
  grid: { left: 50, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'category', data: priceTrends.value.map(i => i.date.slice(5)), boundaryGap: false, axisLine: { lineStyle: { color: getCSSVar('--border-secondary') } }, axisLabel: { color: getCSSVar('--text-secondary') } },
  yAxis: { type: 'value', axisLabel: { color: getCSSVar('--text-secondary'), formatter: '¥{value}' }, splitLine: { lineStyle: { color: getCSSVar('--border-tertiary') } } },
  series: [{
    type: 'line',
    data: priceTrends.value.map(i => Number(i.price.toFixed(2))),
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: { width: 3, color: getCSSVar('--primary-color') },
    itemStyle: { color: getCSSVar('--primary-color') },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: getCSSVar('--primary-alpha-25') },
          { offset: 1, color: getCSSVar('--primary-alpha-02') }
        ]
      }
    }
  }]
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['新增商品', '新增订单'], top: 0 },
  grid: { left: 50, right: 20, top: 40, bottom: 30 },
  xAxis: { type: 'category', data: supplyDemand.value.map(i => i.date.slice(5)), axisLine: { lineStyle: { color: getCSSVar('--border-secondary') } }, axisLabel: { color: getCSSVar('--text-secondary') } },
  yAxis: { type: 'value', axisLabel: { color: getCSSVar('--text-secondary') }, splitLine: { lineStyle: { color: getCSSVar('--border-tertiary') } } },
  series: [
    { name: '新增商品', type: 'bar', data: supplyDemand.value.map(i => i.supply), barWidth: '35%', itemStyle: { color: getCSSVar('--primary-color'), borderRadius: [4, 4, 0, 0] } },
    { name: '新增订单', type: 'bar', data: supplyDemand.value.map(i => i.demand), barWidth: '35%', itemStyle: { color: getCSSVar('--success-color'), borderRadius: [4, 4, 0, 0] } }
  ]
}))

// 价格分布直方图
const histogramOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}<br/>商品数量: ${params[0].value}` },
  grid: { left: 50, right: 20, top: 20, bottom: 50 },
  xAxis: { type: 'category', data: priceDistribution.value.map(i => i.range), name: '价格区间（元）', axisLabel: { rotate: 45, color: getCSSVar('--text-secondary') } },
  yAxis: { type: 'value', name: '商品数量', axisLabel: { color: getCSSVar('--text-secondary') } },
  series: [{
    type: 'bar',
    data: priceDistribution.value.map(i => i.count),
    itemStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: getCSSVar('--primary-color') },
          { offset: 1, color: getCSSVar('--success-color') }
        ]
      },
      borderRadius: [5, 5, 0, 0]
    }
  }]
}))

// 品类平均价格对比
const categoryPriceOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}<br/>平均价格: ¥${params[0].value}` },
  grid: { left: 80, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'value', name: '平均价格（元）', axisLabel: { formatter: '¥{value}', color: getCSSVar('--text-secondary') } },
  yAxis: { type: 'category', data: categoryPrices.value.map(i => i.name), axisLabel: { color: getCSSVar('--text-secondary') } },
  series: [{
    type: 'bar',
    data: categoryPrices.value.map(i => i.avg_price),
    itemStyle: { color: getCSSVar('--primary-color'), borderRadius: [0, 5, 5, 0] }
  }]
}))

const fetchData = async () => {
  try {
    const [overviewRes, categoryRes, priceRes, sdRes, distRes, catPriceRes] = await Promise.all([
      statsAPI.getOverview(),
      statsAPI.getCategoryDistribution(),
      statsAPI.getPriceTrends(),
      statsAPI.getSupplyDemand(),
      statsAPI.getPriceDistribution().catch(() => ({ data: [] })),
      statsAPI.getCategoryAvgPrices().catch(() => ({ data: [] }))
    ])

    const ov = overviewRes.data
    marketStats.value = [
      { label: '在售商品', value: String(ov.total_items || 0), trend: 12.5 },
      { label: '今日新增', value: String(ov.today_items || 0), trend: 5.2 },
      { label: '累计成交', value: String(ov.total_orders || 0), trend: -2.1 },
      { label: '市场均价', value: `¥${ov.avg_price || 0}`, trend: 1.8 }
    ]

    categoryDistribution.value = (categoryRes.data || []).map(item => ({
      name: item.name,
      value: item.value
    }))

    priceTrends.value = priceRes.data || []
    supplyDemand.value = sdRes.data || []
    priceDistribution.value = distRes.data || []
    categoryPrices.value = catPriceRes.data || []
  } catch (e) {
    console.error('获取统计数据失败', e)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.market-trends-container {
  padding: 24px 0;
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-tertiary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-primary);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-secondary);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-tertiary);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-trend.up {
  color: var(--danger-color);
  background: color-mix(in srgb, var(--danger-color) 16%, transparent 84%);
}

.stat-trend.down {
  color: var(--success-color);
  background: color-mix(in srgb, var(--success-color) 16%, transparent 84%);
}

.main-charts {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 24px;
  margin-bottom: 32px;
}

.chart-box {
  background: var(--bg-primary);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-secondary);
}

.box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.box-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-icon {
  color: var(--text-quaternary);
  cursor: help;
}

.chart {
  width: 100%;
  height: 320px;
}

.supply-demand-section,
.price-distribution-section,
.category-price-section {
  margin-bottom: 32px;
}

.supply-demand-section .chart,
.price-distribution-section .chart,
.category-price-section .chart {
  height: 300px;
}

.insights-section {
  background: var(--bg-primary);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-secondary);
}

.insights-list {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.insights-list li {
  margin-bottom: 8px;
  line-height: 1.6;
}

@media (max-width: 992px) {
  .main-charts {
    grid-template-columns: 1fr;
  }
}
</style>
