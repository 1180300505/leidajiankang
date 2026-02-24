<template>
  <div id="app">
    <el-menu mode="horizontal" router :default-active="activePath" @select="handleMenuSelect">
      <el-menu-item index="/">数据监控中心</el-menu-item>
      <el-menu-item index="/send">发送模拟数据</el-menu-item>
      <el-menu-item index="/ip">上位机IP设置</el-menu-item>
      <el-menu-item index="/health">健康度监控</el-menu-item>
    </el-menu>

    <div style="margin-top: 20px;">
      <router-view v-slot="{ Component }">
        <component 
          :is="Component" 
          ref="currentPageRef" 
        />
      </router-view>
    </div>

    <FaultAlarm />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import FaultAlarm from './views/Alert.vue'

const route = useRoute()
const activePath = ref('/')
const currentPageRef = ref(null)

// 监听路由变化，更新菜单高亮状态
watch(() => route.path, (newPath) => {
  activePath.value = newPath
})

// 当菜单选中时触发逻辑
const handleMenuSelect = (index) => {
  // 如果点击的是健康度监控页面，且该页面组件已加载
  if (index === '/health') {
    // 延迟一小会儿等待路由跳转完成，然后触发刷新
    setTimeout(() => {
      if (currentPageRef.value && typeof currentPageRef.value.refreshData === 'function') {
        currentPageRef.value.refreshData()
      }
    }, 100)
  }
}
</script>

<style>
body { margin: 0; font-family: sans-serif; background-color: #f5f7fa; }
#app { padding: 0 20px; }
</style>