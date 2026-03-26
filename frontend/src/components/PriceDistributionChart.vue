<template>
  <div class="price-distribution-chart">
    <el-card>
      <template #header>
        <span>价格区间分布</span>
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

const props = defineProps({
  categoryId: {
    type: String,
    default: null
  }
})

const loading = ref(false)
const chartData = ref([])

const chartOption = computed(() => {
  const ranges = chartData.value.map(item => item.range)
  const counts = chartData.value.map(item => item.count)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>商品数量: ${param.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ranges,
      name: '价格区间（元）',
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '商品数量'
    },
    series: [
      {
        name: '商品数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#b4fb51' },
              { offset: 1, color: '#8fe083' }
            ]
          },
          borderRadius: [5, 5, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#c3ff6f' },
                { offset: 1, color: '#8fe083' }
              ]
            }
          }
        }
      }
    ]
  }
})

const loadData = async () => {
  loading.value = true
  try {
    const response = await statsAPI.getPriceDistribution(props.categoryId)
    chartData.value = response.data || []
  } catch (error) {
    console.error('加载价格分布数据失败:', error)
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
.price-distribution-chart {
  margin: 20px 0;
}
</style>
