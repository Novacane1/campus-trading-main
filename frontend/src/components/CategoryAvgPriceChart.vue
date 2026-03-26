<template>
  <div class="category-avg-price-chart">
    <el-card>
      <template #header>
        <span>各品类平均价格对比</span>
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
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import statsAPI from '@/services/statsAPI'
import { ElMessage } from 'element-plus'

use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent
])

const loading = ref(false)
const chartData = ref([])

const chartOption = computed(() => {
  const categories = chartData.value.map(item => item.category)
  const avgPrices = chartData.value.map(item => item.avg_price)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>平均价格: ¥${param.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '平均价格（元）',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0
      }
    },
    series: [
      {
        name: '平均价格',
        type: 'bar',
        data: avgPrices,
        itemStyle: {
          color: '#b4fb51',
          borderRadius: [0, 5, 5, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: '¥{c}'
        },
        emphasis: {
          itemStyle: {
            color: '#c3ff6f'
          }
        }
      }
    ]
  }
})

const loadData = async () => {
  loading.value = true
  try {
    const response = await statsAPI.getCategoryAvgPrice()
    chartData.value = response.data || []
  } catch (error) {
    console.error('加载品类价格数据失败:', error)
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
.category-avg-price-chart {
  margin: 20px 0;
}
</style>
