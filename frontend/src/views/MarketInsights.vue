<template>
  <div class="market-insights">
    <div class="page-header">
      <h1>市场行情</h1>
      <p>基于数据分析的价格走势与市场供需情况</p>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <PriceTrendChart />
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <SupplyDemandChart />
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <PriceDistributionChart />
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <CategoryAvgPriceChart />
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="insights-card">
          <template #header>
            <span>市场洞察</span>
          </template>
          <div class="insights-content">
            <el-alert
              title="定价建议"
              type="info"
              :closable="false"
              show-icon
            >
              <p>根据市场数据分析，建议您：</p>
              <ul>
                <li>参考同类商品的平均价格进行定价</li>
                <li>关注价格走势，选择合适的发布时机</li>
                <li>价格区间分布显示了买家的购买力范围</li>
                <li>供需比例反映了市场的活跃程度</li>
              </ul>
            </el-alert>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PriceTrendChart from '@/components/PriceTrendChart.vue'
import SupplyDemandChart from '@/components/SupplyDemandChart.vue'
import PriceDistributionChart from '@/components/PriceDistributionChart.vue'
import CategoryAvgPriceChart from '@/components/CategoryAvgPriceChart.vue'
</script>

<style scoped>
.market-insights {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.page-header p {
  color: var(--text-tertiary);
  font-size: 14px;
}

.el-row {
  margin-bottom: 20px;
}

.insights-card {
  margin-top: 20px;
}

.insights-content ul {
  margin-top: 10px;
  padding-left: 20px;
}

.insights-content li {
  margin-bottom: 8px;
  line-height: 1.6;
}
</style>
