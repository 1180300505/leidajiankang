<template>
  <div style="padding: 20px; font-family: Arial, sans-serif;">
    <h2>测控系统数据传输测试</h2>
    
    <button @click="sendTelemetry" style="padding: 10px 20px; cursor: pointer;">
      发送模拟模拟遥测数据 (JSON)
    </button>

    <div v-if="statusMsg" style="margin-top: 20px; color: blue;">
      {{ statusMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const statusMsg = ref('')

// 推荐的 JS 时间格式化方法
const now = new Date();
const timestamp = now.getFullYear() + '-' + 
                 String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                 String(now.getDate()).padStart(2, '0') + ' ' + 
                 String(now.getHours()).padStart(2, '0') + ':' + 
                 String(now.getMinutes()).padStart(2, '0') + ':' + 
                 String(now.getSeconds()).padStart(2, '0');
// 结果示例: 2026-02-24 05:47:56

const sendTelemetry = async () => {
  // 按照你定义的类结构构造 JSON 对象
  const telemetryData = {
    timestamp: timestamp,
    system_status: {
      mode: "自动追踪",
      signal_source: "卫星A",
      source_status: "正常",
      lock_status: "已锁定",
      lock_indicator: "绿灯"
    },
    signal_params: {
      agc_threshold: 1.2,
      agc_voltage: 3.5,
      azimuth_error_voltage: 0.02,
      pitch_error_voltage: 0.01
    },
    tracking_data: { // 注意：对应后端逻辑，包裹在 tracking_data 里
      turntable_system: {
        guide_azimuth: 120.5 + (Math.random() - 0.5) * 10,
        guide_pitch: 45.0,
        guide_tilt: 0.0,
        current_azimuth: 120.48,
        current_pitch: 45.01,
        current_tilt: 0.0,
        deviation_azimuth: -0.02,
        deviation_pitch: 0.01,
        deviation_tilt: 0.0
      },
      geodetic_system: {
        guide_azimuth: 110.2 + (Math.random() - 0.5) * 10,
        guide_pitch: 40.0,
        current_azimuth: 110.19,
        current_pitch_alt: 40.01,
        deviation_azimuth: -0.01,
        deviation_pitch: 0.01
      }
    },
    motor_diagnostics: {
      motor_1: {
        power_on: true,
        status: "运行中",
        current: 5.2,
        voltage: 220.0 + (Math.random() - 0.5) * 10,
        inertia: 0.85,
        temp: 42.5
      },
      motor_2: {
        power_on: true,
        status: "待机",
        current: 0.1,
        voltage: 220.0 + (Math.random() - 0.5) * 10,
        inertia: 0.85,
        temp: 38.0
      }
    }
  }

  try {
    statusMsg.value = "正在发送..."
    const response = await axios.post('http://192.168.2.5:5000/api/send-item', telemetryData)
    statusMsg.value = `服务器响应: ${JSON.stringify(response.data)}`
    console.log("发送成功内容:", telemetryData)
  } catch (error) {
    statusMsg.value = "发送失败，请检查后端是否开启及跨域设置"
    console.error(error)
  }
}
</script>