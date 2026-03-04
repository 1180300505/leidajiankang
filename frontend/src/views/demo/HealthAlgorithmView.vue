<template>
  <div class="health-algorithm-page" v-loading="loading">
    <el-row :gutter="24">
      <!-- 左侧：算法选择 -->
      <el-col :xs="24" :sm="24" :md="10" :lg="8">
        <el-card class="card" header="算法选择" shadow="hover">
          <div class="algorithm-section">
            <div class="section-label">健康评估算法</div>
            <el-radio-group v-model="currentAlgorithm" @change="handleAlgorithmChange" class="algorithm-radio">
              <el-radio label="kmeans" size="large">
                <span class="radio-label">KMeans</span>
                <span class="radio-desc">基于聚类的距离评估</span>
              </el-radio>
              <el-radio label="som" size="large">
                <span class="radio-label">SOM</span>
                <span class="radio-desc">自组织映射神经网络</span>
              </el-radio>
            </el-radio-group>
          </div>
          <div class="action-buttons">
            <el-button type="primary" :loading="retrainLoading" @click="handleRetrain">
              重新训练模型
            </el-button>
          </div>
          <el-alert
            v-if="!isConnected"
            type="info"
            :closable="false"
            show-icon
            class="socket-tip"
          >
            未连接实时数据，请确保后端已启动并有数据上报以获取健康分数
          </el-alert>
        </el-card>
      </el-col>

      <!-- 右侧：健康分数结果 -->
      <el-col :xs="24" :sm="24" :md="14" :lg="16">
        <el-card class="card" header="健康分数结果" shadow="hover">
          <div v-if="!healthData" class="empty-state">
            <el-empty description="暂无健康评估数据">
              <template #image>
                <el-icon :size="64" color="#909399"><Monitor /></el-icon>
              </template>
              <p class="hint">当有数据通过「发送模拟数据」或上位机上报后，此处将展示实时健康分数</p>
            </el-empty>
          </div>

          <div v-else class="health-result">
            <!-- 整体健康 -->
            <div class="result-block overall">
              <div class="block-title">整体健康度</div>
              <div class="score-row">
                <el-progress
                  type="dashboard"
                  :percentage="overallScore"
                  :color="progressColors"
                  :width="140"
                />
                <div class="status-info">
                  <el-tag :type="statusTagType(healthData.overall_status)" size="large">
                    {{ healthData.overall_status }}
                  </el-tag>
                  <p class="update-time">更新于 {{ lastUpdated }}</p>
                </div>
              </div>
            </div>

            <!-- 子系统 -->
            <div class="result-block subsystems">
              <div class="block-title">子系统健康</div>
              <el-row :gutter="16">
                <el-col :span="12">
                  <div class="sub-item">
                    <div class="sub-name">转台系</div>
                    <el-progress
                      :percentage="turntableScore"
                      :stroke-width="12"
                      :color="progressColors"
                    />
                    <el-tag :type="statusTagType(healthData.subsystems?.turntable?.status)" size="small">
                      {{ healthData.subsystems?.turntable?.status || '--' }}
                    </el-tag>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="sub-item">
                    <div class="sub-name">电馈系</div>
                    <el-progress
                      :percentage="electrofeedScore"
                      :stroke-width="12"
                      :color="progressColors"
                    />
                    <el-tag :type="statusTagType(healthData.subsystems?.electrofeed?.status)" size="small">
                      {{ healthData.subsystems?.electrofeed?.status || '--' }}
                    </el-tag>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Monitor } from '@element-plus/icons-vue'
import { API_PREFIX } from '../../config/backend'
import { createDashboardSocket } from '../../socket/dashboardSocket'

const loading = ref(false)
const retrainLoading = ref(false)
const currentAlgorithm = ref('kmeans')
const isConnected = ref(false)
const dashboardPayload = ref(null)
const lastUpdateTime = ref(null)

let socket = null

const healthData = computed(() => {
  const data = dashboardPayload.value?.data?.health
  return data || null
})

const overallScore = computed(() => healthData.value?.current_score ?? 0)
const turntableScore = computed(() => healthData.value?.subsystems?.turntable?.score ?? 0)
const electrofeedScore = computed(() => healthData.value?.subsystems?.electrofeed?.score ?? 0)
const lastUpdated = computed(() => {
  if (!lastUpdateTime.value) return '--'
  return new Date(lastUpdateTime.value).toLocaleTimeString('zh-CN')
})

const progressColors = [
  { color: '#f56c6c', percentage: 60 },
  { color: '#e6a23c', percentage: 80 },
  { color: '#67c23a', percentage: 100 },
]

const statusTagType = (status) => {
  if (!status) return 'info'
  if (status === '正常') return 'success'
  if (status === '轻度异常') return 'warning'
  if (status === '重度异常') return 'danger'
  return 'info'
}

const fetchAlgorithm = async () => {
  try {
    const res = await axios.get(`${API_PREFIX}/health/algorithm`)
    currentAlgorithm.value = res.data.algorithm || 'kmeans'
  } catch (e) {
    console.error('获取算法失败', e)
  }
}

const handleAlgorithmChange = async (val) => {
  loading.value = true
  try {
    await axios.post(`${API_PREFIX}/health/algorithm`, { algorithm: val })
    ElMessage.success(`已切换为 ${val.toUpperCase()} 算法`)
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '切换失败')
    await fetchAlgorithm()
  } finally {
    loading.value = false
  }
}

const handleRetrain = async () => {
  retrainLoading.value = true
  try {
    await axios.post(`${API_PREFIX}/health/retrain`)
    ElMessage.success('模型已重新训练')
  } catch (e) {
    ElMessage.error('重新训练失败')
  } finally {
    retrainLoading.value = false
  }
}

const connectSocket = () => {
  socket = createDashboardSocket({
    onConnect: () => { isConnected.value = true },
    onDisconnect: () => { isConnected.value = false },
    onDashboardUpdate: (payload) => {
      dashboardPayload.value = payload
      lastUpdateTime.value = Date.now()
    },
  })
}

const refreshData = () => {
  fetchAlgorithm()
}

defineExpose({ refreshData })

onMounted(() => {
  fetchAlgorithm()
  connectSocket()
})

onUnmounted(() => {
  if (socket) socket.disconnect()
})
</script>

<style scoped>
.health-algorithm-page {
  padding: 20px;
}
.card {
  margin-bottom: 20px;
  border-radius: 8px;
}
.algorithm-section {
  margin-bottom: 20px;
}
.section-label {
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}
.algorithm-radio {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.algorithm-radio :deep(.el-radio) {
  margin-right: 0;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  width: 100%;
  height: auto;
}
.algorithm-radio :deep(.el-radio.is-checked) {
  border-color: var(--el-color-primary);
  background: rgba(64, 158, 255, 0.05);
}
.radio-label {
  font-weight: 600;
  display: block;
}
.radio-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
.action-buttons {
  margin-top: 16px;
}
.socket-tip {
  margin-top: 16px;
}
.empty-state {
  padding: 40px 0;
}
.hint {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}
.health-result {
  padding: 10px 0;
}
.result-block {
  margin-bottom: 28px;
}
.result-block:last-child {
  margin-bottom: 0;
}
.block-title {
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
  font-size: 15px;
}
.score-row {
  display: flex;
  align-items: center;
  gap: 32px;
  flex-wrap: wrap;
}
.status-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.update-time {
  font-size: 12px;
  color: #909399;
  margin: 0;
}
.sub-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 12px;
}
.sub-name {
  font-weight: 500;
  margin-bottom: 8px;
  color: #606266;
}
.sub-item .el-progress {
  margin-bottom: 8px;
}
</style>
