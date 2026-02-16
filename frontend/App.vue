<template>
  <div class="debug-container">
    <header>
      <h2>测控系统实时监控 (调试版)</h2>
      <button @click="sendTelemetry" class="btn">手动上报模拟数据</button>
      <span :class="isConnected ? 'text-success' : 'text-danger'">
        {{ isConnected ? '● 连接成功' : '○ 未连接' }}
      </span>
    </header>

    <div v-if="dashboardData && dashboardData.data" class="table-grid">
      
      <div class="card">
        <h3>📡 信号强度</h3>
        <table>
          <thead>
            <tr><th>信号名</th><th>数值</th></tr>
          </thead>
          <tbody>
            <tr v-for="(val, key) in dashboardData.data.overview?.signals" :key="key">
              <td>{{ key }}</td>
              <td class="val highlight">{{ val }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <h3>⚙️ 子系统运行状态</h3>
        <div v-for="sys in dashboardData.data.overview?.subsystems" :key="sys.id" class="sub-item">
          <span :class="['light', sys.status === 1 ? 'ok' : sys.status === 3 ? 'error' : 'off']"></span>
          {{ sys.name }} (ID: {{ sys.id }})
        </div>
      </div>

      <div class="card">
        <h3>❤️ 健康状态评分</h3>
        <div class="score-display">
          当前评分: <span class="score-num">{{ dashboardData.data.health?.current_score }}</span>
        </div>
        <p>维度分：{{ dashboardData.data.health?.radar_data?.scores?.join(' | ') }}</p>
      </div>

      <div class="card full-width">
        <h3>⚠️ 当前故障报警</h3>
        <table v-if="dashboardData.data.alerts?.length">
          <tr v-for="(alert, index) in dashboardData.data.alerts" :key="index" class="alert-row">
            <td class="severity-tag">{{ alert.severity }}</td>
            <td><strong>{{ alert.type }}</strong></td>
            <td>位置: {{ alert.position_tag }}</td>
            <td class="desc">{{ alert.desc }}</td>
          </tr>
        </table>
        <p v-else style="color: green;">系统一切正常</p>
      </div>
    </div>

    <div v-else class="loading">
      <p>等待后端数据推送...</p>
      <small>请确保 Python 后端已运行且执行了 socketio.emit</small>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { io } from 'socket.io-client'

const isConnected = ref(false)
const dashboardData = ref(null)

onMounted(() => {
  // 注意：此处地址需与 Flask 保持一致
  const socket = io('http://127.0.0.1:5000')

  socket.on('connect', () => {
    isConnected.value = true
    console.log("WebSocket 连接成功")
  })

  socket.on('update_dashboard', (response) => {
    console.log("收到推送内容:", response)
    // 直接存储整个返回的 JSON 对象
    dashboardData.value = response
  })
})

const sendTelemetry = async () => {
  try {
    // 这里发送的内容会触发后端的解析逻辑
    await axios.post('http://127.0.0.1:5000/api/send-item', {
      test: "trigger" 
    })
  } catch (e) {
    console.error("发送失败:", e)
  }
}
</script>

<style scoped>
.debug-container { padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; min-height: 100vh; }
.header { margin-bottom: 20px; }
.btn { padding: 8px 16px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.table-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-top: 20px; }
.full-width { grid-column: 1 / -1; }
.card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
h3 { margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px; font-size: 16px; }
table { width: 100%; border-collapse: collapse; }
td, th { text-align: left; padding: 10px 5px; border-bottom: 1px solid #fafafa; }
.val { text-align: right; font-family: monospace; }
.highlight { color: #1890ff; font-weight: bold; }
.score-num { font-size: 24px; color: #52c41a; font-weight: bold; }
.sub-item { display: flex; align-items: center; margin: 8px 0; }
.light { width: 10px; height: 10px; border-radius: 50%; margin-right: 10px; display: inline-block; }
.ok { background: #52c41a; }
.off { background: #bfbfbf; }
.error { background: #ff4d4f; }
.alert-row { background: #fff1f0; }
.severity-tag { color: #f5222d; font-weight: bold; }
.text-success { color: #52c41a; margin-left: 10px; }
.text-danger { color: #ff4d4f; margin-left: 10px; }
.loading { text-align: center; margin-top: 100px; color: #999; }
</style>