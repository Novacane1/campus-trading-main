<template>
  <div class="price-trend-chart">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>价格走势分析</span>
          <el-select v-model="selectedDays" @change="loadData" size="small" style="width: 120px">
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
            <el-option label="最近90天" :value="90" />
          </el-select>
        </div>
      </template>

      <v-chart
        :option="chartOption"
        :loading="loading"
        style="height: 400px"
        autoresize
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import statsAPI from '@/services/statsAPI'
import { ElMessage } from 'element-plus'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 获取 CSS 变量值的辅助函数
const getCSSVar = (varName) => {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
}

const props = defineProps({
  categoryId: {
    type: String,
    default: null
  }
})

const loading = ref(false)
const chartData = ref([])
const selectedDays = ref(30)

const chartOption = computed(() => {
  const dates = chartData.value.map(item => item.date)
  const avgPrices = chartData.value.map(item => item.avg_price || item.price)
  const minPrices = chartData.value.map(item => item.min_price)
  const maxPrices = chartData.value.map(item => item.max_price)

  const series = [
    {
      name: '平均价格',
      type: 'line',
      data: avgPrices,
      smooth: true,
      itemStyle: {
        color: getCSSVar('--primary-color')
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: getCSSVar('--primary-alpha-30') },
            { offset: 1, color: getCSSVar('--primary-alpha-05') }
          ]
        }
      }
    }
  ]

  // 如果有最小最大价格数据，添加到图表
  if (minPrices.some(p => p !== undefined)) {
    series.push({
      name: '最低价格',
      type: 'line',
      data: minPrices,
      smooth: true,
      itemStyle: {
        color: getCSSVar('--success-color')
      },
      lineStyle: {
        type: 'dashed'
      }
    })
  }

  if (maxPrices.some(p => p !== undefined)) {
    series.push({
      name: '最高价格',
      type: 'line',
      data: maxPrices,
      smooth: true,
      itemStyle: {
        color: getCSSVar('--danger-color')
      },
      lineStyle: {
        type: 'dashed'
      }
    })
  }

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: series.map(s => s.name),
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '价格（元）',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series
  }
})

const loadData = async () => {
  loading.value = true
  try {
    let response
    if (props.categoryId) {
      response = await statsAPI.getCategoryPriceTrends(props.categoryId, selectedDays.value)
    } else {
      response = await statsAPI.getPriceTrends()
    }
    chartData.value = response.data || []
  } catch (error) {
    console.error('加载价格走势数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.price-trend-chart {
  margin: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
