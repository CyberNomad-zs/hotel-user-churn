<template>
  <div>
    <el-card shadow="hover" style="width: 100%;">
      <div slot="header" class="clearfix">
        <span>访问和入住人数（ECharts）</span>
        <div style="float: right;">
          <el-button size="mini" type="primary" @click="fetchData" :loading="loading">刷新</el-button>
        </div>
      </div>

      <div ref="chartContainer" :style="{ width: '100%', height: chartHeight + 'px' }"></div>

      <div v-if="loading" style="text-align:center; margin-top:10px;">加载中...</div>
      <div v-if="error" style="color: red; text-align:center; margin-top:10px;">获取数据失败：{{ error }}</div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'VisitChart',
  props: {
    apiUrl: { type: String, default: '/api/visit_arrival_data' },
    chartHeight: { type: Number, default: 420 },
    tryParseTime: { type: Boolean, default: true }
  },
  data() {
    return {
      chart: null,
      loading: false,
      error: null
    }
  },
  mounted() {
    this.initChart()
    this.fetchData()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    this.disposeChart()
  },
  methods: {
    initChart() {
      const el = this.$refs.chartContainer
      if (!el) return
      this.chart = echarts.init(el)
      this.chart.setOption({
        title: { text: '访问和入住人数图', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['入住人数', '预定人数'], top: 30 },
        grid: { left: '6%', right: '6%', bottom: '14%', containLabel: true },
        xAxis: { type: 'category', data: [], axisLabel: { rotate: 45 } },
        yAxis: { type: 'value', name: '人数' },
        dataZoom: [{ type: 'slider', start: 0, end: 100, bottom: 0 }, { type: 'inside', start: 0, end: 100 }],
        series: [{ name: '入住人数', type: 'line', data: [] }, { name: '预定人数', type: 'bar', data: [] }]
      })
    },

    async fetchData() {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get('http://localhost:5000/api/visit_arrival_data')
        const payload = res.data
        const x = payload.x
        const arrival = payload.arrival.map(v => Number(v || 0))
        const d = payload.d.map(v => Number(v || 0))

        let xAxisType = 'category'
        if (x.length && typeof x[0] === 'string' && (x[0].includes('-') || x[0].includes('T'))) {
          xAxisType = 'time'
        }

        this.updateChart({ x, arrival, d, xAxisType })
      } catch (err) {
        this.error = err.message || String(err)
      } finally {
        this.loading = false
      }
    },
    updateChart({ x, arrival, d, xAxisType }) {
      if (!this.chart) return

      if (xAxisType === 'time') {
        const lineData = []
        const barData = []
        for (let i = 0; i < x.length; i++) {
          lineData.push([x[i], arrival[i]])
          barData.push([x[i], d[i]])
        }

        this.chart.setOption({
          xAxis: { type: 'time', data: undefined },
          series: [
            { name: '入住人数', type: 'line', data: lineData },
            { name: '预定人数', type: 'bar', data: barData }
          ]
        }, { notMerge: false })
      } else {
        // category
        this.chart.setOption({
          xAxis: { type: 'category', data: x },
          series: [
            { name: '入住人数', type: 'line', data: arrival },
            { name: '预定人数', type: 'bar', data: d }
          ]
        }, { notMerge: false })
      }
    },

    handleResize() {
      if (this.chart) {
        this.chart.resize()
      }
    },

    disposeChart() {
      if (this.chart) {
        try {
          this.chart.dispose()
        } catch (e) {
          // ignore
        }
        this.chart = null
      }
    }
  } // end methods
} // end export default
</script>