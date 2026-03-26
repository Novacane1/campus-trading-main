<template>
  <div class="supply-demand-chart">
    <el-card>
      <template #header>
        <span>供需比例分析</span>
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
import { PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import statsAPI from '@/services/statsAPI'
import { ElMessage } from 'element-plus'

use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent
])

const loading = ref(false)
const chartData = ref([])

const chartOption = computed(() => {
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: chartData.value.map(item => item.name)
    },
    series: [
      {
        name: '供需情况',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#272c21',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: chartData.value,
        color: ['#b4fb51', '#8fe083', '#ff9933']
      }
    ]
  }
})

const loadData = async () => {
  loading.value = true
  try {
    const response = await statsAPI.getSupplyDemandRatio()
    chartData.value = response.data || []
  } catch (error) {
    console.error('加载供需数据失败:', error)
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
.supply-demand-chart {
  margin: 20px 0;
}
</style>
