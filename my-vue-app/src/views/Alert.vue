<template>
  <div v-show="false"></div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { ElNotification } from 'element-plus'

// 连接到 SocketIO 服务端
const socket = io('http://192.168.2.5:5000') // 确保使用你的无线网 IP

onMounted(() => {
  // 监听后端发出的 'fault_alarm' 事件
  socket.on('fault_alarm', (data) => {
    console.log('收到故障推送:', data)
    
    // 弹出右侧提醒框
    ElNotification({
      title: `报警：系统出现${data.故障程度}`,
      message: formatMessage(data),
      type: data.故障程度 === '严重故障' ? 'error' : 'warning',
      duration: 0, // 设为 0 则不自动关闭，除非用户手动点掉
      position: 'top-right'
    })
  })
})

// 格式化展示报警详细内容
const formatMessage = (data) => {
  let msg = ''
  if (data.turntable_system) msg += `转台：${data.turntable_system}；`
  if (data.geodetic_system) msg += `大地系：${data.geodetic_system}；`
  if (data.motor1) msg += `电机1：${data.motor1}；`
  if (data.motor2) msg += `电机2：${data.motor2}；`
  return msg || '具体参数请查看详情'
}

onUnmounted(() => {
  socket.disconnect() // 销毁组件时断开连接
})
</script>