<template>
  <section class="ip-screen">
    <header class="screen-header">
      <div class="title-block">
        <span class="eyebrow">NETWORK CONTROL</span>
        <h1>IP设置</h1>
      </div>
      <div class="header-actions">
        <button class="head-btn secondary" @click="goMain">返回主界面</button>
        <button class="head-btn" :disabled="loading" @click="fetchCurrentIp">
          {{ loading ? '读取中...' : '刷新当前IP' }}
        </button>
      </div>
    </header>

    <div class="screen-grid">
      <article class="panel current-panel">
        <h2>当前上位机通信配置</h2>
        <div class="current-ip-box">
          <label>当前允许 IP</label>
          <div class="ip-value">{{ currentIp }}</div>
          <p class="hint">后端仅接收该来源 IP 的上报数据</p>
        </div>
      </article>

      <article class="panel form-panel">
        <h2>更新 IP 白名单</h2>
        <form class="ip-form" @submit.prevent="saveIp">
          <label for="ip-input">新 IP 地址</label>
          <div class="input-row">
            <input
              id="ip-input"
              v-model.trim="newIp"
              type="text"
              placeholder="例如：192.168.1.105"
              autocomplete="off"
            />
            <button type="submit" class="primary-btn" :disabled="saving">
              {{ saving ? '提交中...' : '确认修改' }}
            </button>
          </div>
          <p class="form-tip">修改后将立即生效，请确认数据发送端地址与此一致。</p>
        </form>

        <div class="status-strip" :class="messageType" v-if="statusMessage">
          {{ statusMessage }}
        </div>
      </article>

      <article class="panel info-panel">
        <h2>安全提示</h2>
        <ul class="tips">
          <li>修改后，后端会校验请求来源 IP。</li>
          <li>非白名单来源的 JSON 数据上报将被拒绝。</li>
          <li>联调时请统一前后端配置中的主机地址。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { API_PREFIX } from '../config/backend'

const router = useRouter()
const currentIp = ref('加载中...')
const newIp = ref('')
const saving = ref(false)
const loading = ref(false)
const statusMessage = ref('')
const messageType = ref('')

const isIpv4 = (value) => {
  const s = String(value || '').trim()
  const parts = s.split('.')
  if (parts.length !== 4) return false
  return parts.every((part) => /^(0|[1-9]\d{0,2})$/.test(part) && Number(part) >= 0 && Number(part) <= 255)
}

const setStatus = (type, message) => {
  messageType.value = type
  statusMessage.value = message
}

const fetchCurrentIp = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${API_PREFIX}/config/ip`)
    currentIp.value = res.data?.current_ip || '未返回'
    setStatus('success', '已读取当前 IP 配置')
  } catch (error) {
    setStatus('error', '读取当前 IP 失败')
    ElMessage.error('读取当前IP失败')
    console.error('fetchCurrentIp failed', error)
  } finally {
    loading.value = false
  }
}

const saveIp = async () => {
  if (!newIp.value) {
    setStatus('warning', '请输入新的 IP 地址')
    ElMessage.error('请输入有效IP')
    return
  }
  if (!isIpv4(newIp.value)) {
    setStatus('warning', 'IP 格式不正确，请输入 IPv4 地址')
    ElMessage.error('IP格式不正确')
    return
  }

  saving.value = true
  try {
    await axios.post(`${API_PREFIX}/config/ip`, { new_ip: newIp.value })
    currentIp.value = newIp.value
    setStatus('success', 'IP 修改成功，已更新白名单')
    ElMessage.success('上位机IP修改成功')
    newIp.value = ''
  } catch (error) {
    setStatus('error', 'IP 修改失败，请检查后端服务状态')
    ElMessage.error('修改失败')
    console.error('saveIp failed', error)
  } finally {
    saving.value = false
  }
}

const goMain = () => {
  router.push('/health')
}

onMounted(fetchCurrentIp)
</script>

<style scoped>
.ip-screen {
  position: relative;
  min-height: calc(100vh - 32px);
  padding: 16px;
  color: #d9f6ff;
  border: 1px solid rgba(77, 201, 255, 0.4);
  border-radius: 12px;
  background:
    radial-gradient(900px 420px at 10% -5%, rgba(69, 155, 255, 0.16), transparent 65%),
    radial-gradient(700px 320px at 100% 0%, rgba(46, 218, 255, 0.12), transparent 65%),
    linear-gradient(180deg, #06163d, #08265f 52%, #071c4f);
  box-shadow:
    inset 0 0 26px rgba(34, 157, 255, 0.18),
    0 0 16px rgba(25, 133, 236, 0.18);
  overflow: hidden;
}

.ip-screen::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(101, 193, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(101, 193, 255, 0.06) 1px, transparent 1px);
  background-size: 28px 28px;
}

.screen-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid rgba(101, 209, 255, 0.28);
  border-radius: 10px;
  background: linear-gradient(180deg, rgba(16, 50, 106, 0.85), rgba(8, 31, 77, 0.88));
  box-shadow: inset 0 0 16px rgba(58, 171, 255, 0.12);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-block {
  display: grid;
  gap: 2px;
}

.eyebrow {
  color: #8ddfff;
  font-size: 11px;
  letter-spacing: 1.8px;
}

.title-block h1 {
  margin: 0;
  font-size: 28px;
  letter-spacing: 2px;
  color: #eefbff;
  text-shadow: 0 0 10px rgba(109, 217, 255, 0.24);
}

.head-btn {
  height: 40px;
  padding: 0 14px;
  border-radius: 8px;
  border: 1px solid rgba(108, 216, 255, 0.36);
  background: linear-gradient(180deg, #1f5cad, #153f84);
  color: #e6fbff;
  cursor: pointer;
  transition: 0.2s ease;
}

.head-btn.secondary {
  background: linear-gradient(180deg, #19467f, #12345f);
}

.head-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 12px rgba(89, 205, 255, 0.28);
}

.head-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.screen-grid {
  position: relative;
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1.1fr 1.5fr;
  gap: 12px;
}

.panel {
  position: relative;
  border-radius: 10px;
  border: 1px solid rgba(95, 205, 255, 0.28);
  background: linear-gradient(180deg, rgba(8, 32, 79, 0.9), rgba(7, 22, 58, 0.9));
  box-shadow:
    inset 0 0 18px rgba(44, 164, 255, 0.14),
    0 0 8px rgba(31, 127, 231, 0.12);
  padding: 14px;
}

.panel::after {
  content: "";
  position: absolute;
  inset: 6px;
  border: 1px solid rgba(101, 205, 255, 0.12);
  border-radius: 8px;
  pointer-events: none;
}

.panel h2 {
  margin: 0 0 12px;
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 12px;
  border-radius: 6px;
  color: #a7eeff;
  font-size: 14px;
  border: 1px solid rgba(100, 207, 255, 0.25);
  background: linear-gradient(180deg, rgba(24, 74, 150, 0.95), rgba(15, 46, 104, 0.95));
}

.current-panel {
  min-height: 220px;
}

.current-ip-box {
  display: grid;
  gap: 10px;
  align-content: start;
  min-height: 150px;
  padding: 14px;
  border-radius: 8px;
  border: 1px solid rgba(100, 207, 255, 0.14);
  background: rgba(7, 25, 66, 0.45);
}

.current-ip-box label {
  color: #9bdff7;
  font-size: 13px;
}

.ip-value {
  min-height: 54px;
  display: flex;
  align-items: center;
  padding: 0 14px;
  border-radius: 8px;
  border: 1px solid rgba(110, 216, 255, 0.24);
  background: linear-gradient(180deg, rgba(20, 67, 133, 0.4), rgba(11, 36, 83, 0.35));
  color: #e6fbff;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
  text-shadow: 0 0 10px rgba(117, 220, 255, 0.2);
}

.hint {
  margin: 0;
  color: #86c7df;
  font-size: 12px;
}

.form-panel {
  min-height: 220px;
}

.ip-form {
  display: grid;
  gap: 10px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(110, 216, 255, 0.14);
  background: rgba(7, 23, 58, 0.45);
}

.ip-form label {
  font-size: 13px;
  color: #9edcf3;
}

.input-row {
  display: grid;
  grid-template-columns: 1fr 140px;
  gap: 10px;
}

.input-row input {
  height: 42px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid rgba(111, 212, 255, 0.22);
  background: rgba(8, 26, 64, 0.82);
  color: #dcf7ff;
  outline: none;
  transition: 0.2s ease;
}

.input-row input::placeholder {
  color: #6fa6bf;
}

.input-row input:focus {
  border-color: rgba(137, 228, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(74, 167, 255, 0.12);
}

.primary-btn {
  height: 42px;
  border-radius: 8px;
  border: 1px solid rgba(110, 216, 255, 0.35);
  background: linear-gradient(180deg, #2d7ed3, #1b4e97);
  color: #effcff;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s ease;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 14px rgba(92, 201, 255, 0.26);
}

.primary-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.form-tip {
  margin: 0;
  color: #7fc2dc;
  font-size: 12px;
}

.status-strip {
  margin-top: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid rgba(111, 212, 255, 0.12);
  font-size: 13px;
}

.status-strip.success {
  color: #77ffd2;
  background: rgba(20, 106, 78, 0.2);
  border-color: rgba(108, 255, 209, 0.16);
}

.status-strip.warning {
  color: #ffe28e;
  background: rgba(138, 102, 12, 0.16);
  border-color: rgba(255, 226, 142, 0.14);
}

.status-strip.error {
  color: #ff9aa8;
  background: rgba(115, 22, 38, 0.18);
  border-color: rgba(255, 154, 168, 0.14);
}

.info-panel {
  grid-column: 1 / -1;
}

.tips {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
  color: #b8ebfb;
  font-size: 13px;
}

@media (max-width: 960px) {
  .screen-grid {
    grid-template-columns: 1fr;
  }

  .info-panel {
    grid-column: auto;
  }

  .input-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .screen-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .head-btn {
    width: 100%;
  }

  .title-block h1 {
    font-size: 22px;
  }

  .ip-value {
    font-size: 18px;
    word-break: break-all;
  }
}
</style>
