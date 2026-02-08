<template>
  <div style="color: #666;font-size: 16px;">
    <div style="padding-bottom: 20px">
      <h1 style="text-align: center"><b>亲爱的{{ user.nickname }}，欢迎登录AI多模型协同酒店用户流失预警系统</b></h1>
    </div>
    <el-row :gutter="10" style="margin-bottom: 5px;font-size: 16px">
      <el-col :span="6">
        <el-card style="color: #409EFF">
          <div><i class="el-icon-user-solid" />当前用户总数</div>
          <div style="padding: 10px 0; text-align: center; font-weight: bold" v-text="total"></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card style="color: #409EFF;margin-bottom:50px">
          <div><i class="el-icon-user-solid" />酒店用户总数</div>
          <div style="padding: 10px 0; text-align: center; font-weight: bold" v-text="total2"></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card style="color: #409EFF;margin-bottom:50px">
          <div><i class="el-icon-user-solid" />今日预测流失总数</div>
          <div style="padding: 10px 0; text-align: center; font-weight: bold" v-text="total1"></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card style="color: #409EFF;margin-bottom:50px">
          <div><i class="el-icon-user-solid" />用户流失总量</div>
          <div style="padding: 10px 0; text-align: center; font-weight: bold">{{ total3 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover" style="width: 100%;">
          <div slot="header" class="clearfix">
            <span>酒店用户分类图</span>
          </div>
          <div id="tu" style="width: 100%; height: 500px"></div>
        </el-card>
      </el-col>

<!--      <el-col :span="12">-->
<!--        <el-card shadow="hover" style="width: 100%;">-->
<!--          <div slot="header" class="clearfix">-->
<!--            <span>车辆数量VS交通情况分类</span>-->
<!--          </div>-->
<!--          <VehicleChart />-->
<!--        </el-card>-->
<!--      </el-col>-->
      <el-col :span="12">
        <el-card shadow="hover" style="width: 100%;">
          <div slot="header" class="clearfix">
            <span>预定时间VS入住时间</span>
          </div>
          <VisitChart />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>

import VehicleChart from "@/components/VehicleChart";
import VisitChart from "@/components/VisitChart";
import * as echarts from 'echarts';

export default {
  name: "Home",
  components: {
    VehicleChart,
    VisitChart
  },
  data() {
    return {
      user: localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user")) : {},
      total: 0,
      total1: 0,
      total2: 0,
      total3: 0,
    }
  },
  created() {
    this.load();
    this.load1();
    this.load2();
    this.load3();
  },
  methods: {
    load() {
      this.request.get("/user/totle").then(res => {
        this.total = res.data;
      });
    },
    load2() {
      this.request.get("/echarts/totle").then(res => {
        this.total2 = res.data;
      });
    },
    load1() {
      this.request.get("/echarts/totle1").then(res => {
        this.total1 = 0;
      });
    },
    load3() {
      this.request.get("/echarts/totle3").then(res => {
        this.total3 =6193;
      });
    }
  },
  mounted() {
    const chartDom = document.getElementById('tu');
    const myChart = echarts.init(chartDom);

    const option = {
      polar: {
        radius: [10, '85%']
      },
      angleAxis: {
        max: function(value) {
          return value.max + 500;
        },
        startAngle: 75
      },
      radiusAxis: {
        type: 'category',
        data: ['正常', '流失']
      },
      tooltip: {},
      series: {
        type: 'bar',
        data: [],
        coordinateSystem: 'polar',
        label: {
          show: true,
          position: 'middle',
          formatter: '{b}: {c}'
        },
        itemStyle: {
          color: params => {
            const colorList = ['#5470C6', '#91CC75', '#FAC858', '#EE6666'];
            return colorList[params.dataIndex];
          }
        }
      }
    };

    this.request.get("/echarts/members").then(res => {
      option.series.data = res.data;
      myChart.setOption(option);
    });
  }
}
</script>

<style scoped>
.el-card {
  margin-bottom: 20px;
}

.el-row {
  margin-bottom: 20px;
}

.el-col {
  margin-bottom: 20px;
}
</style>