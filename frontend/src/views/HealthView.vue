<template>
  <section class="health-screen">
    <button
      v-if="hasActiveAlarm"
      class="corner-alarm"
      :class="[`severity-${alarmSeverity}`]"
      type="button"
      @click="goAlertsPage"
      :title="alarmBannerText"
    >
      <span class="corner-alarm-icon">{{ alarmBannerIcon }}</span>
      <span class="corner-alarm-text">{{ alarmBannerText }}</span>
    </button>

    <header class="screen-header panel-box">
      <div class="header-nav">
        <button
          v-for="item in topLeftTabs"
          :key="item.label"
          class="tab-chip"
          type="button"
          @click="handleTopTabClick(item)"
        >
          {{ item.label }}
        </button>
      </div>
      <h1 class="screen-title">天线系统健康监测</h1>
      <div class="header-nav header-nav-right">
        <button
          v-for="item in topRightTabs"
          :key="item.label"
          class="tab-chip"
          type="button"
          @click="handleTopTabClick(item)"
        >
          {{ item.label }}
        </button>
      </div>
    </header>

    <div class="screen-main">
      <aside class="left-col">
        <article class="panel-box info-card">
          <h2 class="card-title">设备基本信息</h2>
          <div class="meta-row">
            <span>设备: {{ deviceLabel }}</span>
            <span>时间: {{ displayTimestamp }}</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <p class="label">健康分数</p>
              <p class="value accent-pink">{{ healthScore }}</p>
            </div>
            <div class="stat-item">
              <p class="label">运行时长</p>
              <p class="value accent-cyan">{{ runtimeLabel }}</p>
            </div>
            <div class="stat-item">
              <p class="label">异常次数</p>
              <p class="value accent-yellow">{{ abnormalCount }}</p>
            </div>
            <div class="stat-item">
              <p class="label">设备状态</p>
              <p class="value accent-green">{{ systemStatusText }}</p>
            </div>
          </div>
        </article>

        <article class="panel-box chart-card">
          <h2 class="card-title">设备运行状态监测</h2>
          <div class="meta-row">
            <span>设备: {{ deviceLabel }}</span>
            <span>时间: {{ displayTimestamp }}</span>
          </div>
          <div class="ring-wrap">
            <div class="ring ring-a" :style="ringStyles[0]"><span>{{ ringValues[0] }}</span></div>
            <div class="ring ring-b" :style="ringStyles[1]"><span>{{ ringValues[1] }}</span></div>
          </div>
          <div class="legend-row">
            <span v-for="item in subsystemLegend" :key="item.id">
              <i class="dot" :class="item.dotClass"></i> {{ item.name }}：{{ item.text }}
            </span>
          </div>
        </article>

        <article class="panel-box list-card">
          <h2 class="card-title">电机运行状态监测</h2>
          <div class="row-head">
            <span>测点名称</span>
            <span>数据时间</span>
            <span>电流</span>
            <span>状态</span>
          </div>
          <div v-for="item in motors" :key="item.name" class="row-item">
            <span>{{ item.name }}</span>
            <span>{{ item.time }}</span>
            <span>{{ item.current }}</span>
            <span class="accent-cyan">{{ item.status }}</span>
          </div>
        </article>
      </aside>

      <main class="center-col">
        <article class="panel-box hero-card">
          <div class="hero-top">{{ heroTitle }}</div>
          <div class="hero-body">
            <div class="model-core">
              <div class="antenna-dish left"></div>
              <div class="antenna-dish right"></div>
              <div class="antenna-neck"></div>
              <div class="antenna-base"></div>
            </div>

            <div v-for="(box, idx) in leftCallouts" :key="idx" class="callout left">
              <p>{{ box.line1 }}</p>
              <p>{{ box.line2 }}</p>
            </div>
            <div v-for="(box, idx) in rightCallouts" :key="idx" class="callout right">
              <p>{{ box.line1 }}</p>
              <p>{{ box.line2 }}</p>
            </div>
          </div>
        </article>

        <div class="bottom-grid">
          <article class="panel-box table-card">
            <h2 class="card-title">设备故障日志</h2>
            <div class="row-head">
              <span>状态</span>
              <span>故障等级</span>
              <span>故障时间</span>
              <span>故障部位</span>
              <span>持续</span>
            </div>
            <div v-for="(item, i) in faults" :key="i" class="row-item">
              <span>{{ item.status }}</span>
              <span>{{ item.level }}</span>
              <span>{{ item.time }}</span>
              <span>{{ item.part }}</span>
              <span>{{ item.duration }}</span>
            </div>
          </article>

          <article class="panel-box trend-card">
            <h2 class="card-title">设备健康趋势</h2>
            <div class="trend-wrap">
              <svg viewBox="0 0 420 180" class="trend-svg">
                <polyline :points="trendPolylines.main" />
                <polyline :points="trendPolylines.secondary" class="line2" />
                <polyline :points="trendPolylines.third" class="line3" />
              </svg>
            </div>
          </article>
        </div>
      </main>

      <aside class="right-col">
        <article class="panel-box telemetry-card">
          <h2 class="card-title">天线反馈</h2>
          <div class="row-head">
            <span>测点名称</span>
            <span>数据时间</span>
            <span>实时数据</span>
            <span>状态</span>
          </div>
          <div v-for="item in feedback" :key="item.name" class="row-item">
            <span>{{ item.name }}</span>
            <span>{{ item.time }}</span>
            <span>{{ item.value }}</span>
            <span class="accent-green">{{ item.status }}</span>
          </div>
        </article>

        <article class="panel-box alarm-card alarm-entry" @click="goAlertsPage">
          <h2 class="card-title">报警信息</h2>
          <div class="alarm-row"><span>描述</span><p>{{ alarmInfo.description }}</p></div>
          <div class="alarm-row"><span>现象</span><p>{{ alarmInfo.phenomenon }}</p></div>
          <div class="alarm-row"><span>原因</span><p>{{ alarmInfo.cause }}</p></div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createDashboardSocket } from '../socket/dashboardSocket'

const router = useRouter()

const topLeftTabs = [
  { label: 'IP设置', route: '/demo/ip' },
  { label: '算法管理', route: '/health-algorithm' },
  { label: '系统自检' },
  { label: '状态监测' },
  { label: '健康评估', route: '/alerts' }
]

const topRightTabs = [
  { label: '用户管理' },
  { label: '历史查询', route: '/health-history' },
  { label: '诊断查询' },
  { label: '系统扩展' }
]

const handleTopTabClick = (item) => {
  if (item.route) {
    router.push(item.route)
  }
}

const goAlertsPage = () => {
  router.push('/fault-history')
}

const dashboardPayload = ref(null)
const lastUpdated = ref('')
let dashboardSocket = null

const clamp = (value, min = 0, max = 100) => {
  const n = Number(value)
  if (!Number.isFinite(n)) return min
  return Math.min(max, Math.max(min, n))
}

const formatTime = (date = new Date()) => {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

const statusTextByCode = (code) => {
  if (Number(code) === 1) return '正常'
  if (Number(code) === 2) return '关注'
  if (Number(code) === 3) return '告警'
  return '--'
}

const statusLevelByCode = (code) => {
  if (Number(code) === 3) return 3
  if (Number(code) === 2) return 2
  if (Number(code) === 1) return 1
  return 0
}

const dashboardData = computed(() => dashboardPayload.value?.data ?? {})
const overview = computed(() => dashboardData.value.overview ?? {})
const health = computed(() => dashboardData.value.health ?? {})
const subsystems = computed(() => (Array.isArray(overview.value.subsystems) ? overview.value.subsystems : []))
const signals = computed(() => {
  const raw = overview.value.signals
  return raw && typeof raw === 'object' ? raw : {}
})
const signalEntries = computed(() =>
  Object.entries(signals.value).map(([key, value], index) => ({
    key,
    index,
    label: key.replace(/_/g, ' '),
    value: Number(value) || 0
  }))
)

const historyTrend = computed(() => overview.value.history_trend ?? {})
const historyTimes = computed(() => (Array.isArray(historyTrend.value.times) ? historyTrend.value.times : []))
const historyValues = computed(() =>
  (Array.isArray(historyTrend.value.values) ? historyTrend.value.values : []).map((v) => clamp(v))
)

const radarData = computed(() => health.value.radar_data ?? {})
const radarDimensions = computed(() => (Array.isArray(radarData.value.dimensions) ? radarData.value.dimensions : []))
const radarScores = computed(() =>
  (Array.isArray(radarData.value.scores) ? radarData.value.scores : []).map((v) => clamp(v))
)

const displayTimestamp = computed(() => lastUpdated.value || '--')
const deviceLabel = computed(() => `天线节点${overview.value.system_mode ? `-${overview.value.system_mode}` : ''}`)
const healthScore = computed(() => Math.round(clamp(health.value.current_score, 0, 999)))
const runtimeLabel = computed(() => `${historyValues.value.length || 0}条`)
const abnormalCount = computed(() => subsystems.value.filter((item) => Number(item.status) !== 1).length)
const systemStatusText = computed(() => {
  const maxLevel = subsystems.value.reduce((max, item) => Math.max(max, statusLevelByCode(item.status)), 0)
  if (maxLevel >= 3) return '告警'
  if (maxLevel >= 2) return '关注'
  if (maxLevel >= 1) return '正常'
  return '--'
})

const ringValues = computed(() => {
  const values = signalEntries.value.map((item) => Math.round(clamp(item.value)))
  return [values[0] ?? 0, values[1] ?? 0]
})

const ringStyles = computed(() => ([
  { background: `conic-gradient(#2cecff 0 ${ringValues.value[0]}%, #123a72 ${ringValues.value[0]}% 100%)` },
  { background: `conic-gradient(#8f6cff 0 ${ringValues.value[1]}%, #123a72 ${ringValues.value[1]}% 100%)` }
]))

const subsystemLegend = computed(() =>
  subsystems.value.slice(0, 3).map((item, index) => ({
    id: item.id ?? `${item.name}-${index}`,
    name: item.name || `子系统${index + 1}`,
    text: statusTextByCode(item.status),
    dotClass: Number(item.status) === 3 ? 'dot-purple' : Number(item.status) === 2 ? 'dot-cyan' : 'dot-green'
  }))
)

const motors = computed(() =>
  subsystems.value.map((item, index) => ({
    name: item.name || `电机${index + 1}`,
    time: displayTimestamp.value,
    current: `${(signalEntries.value[index]?.value ?? 0).toFixed(1)} A`,
    status: statusTextByCode(item.status)
  }))
)

const feedback = computed(() => {
  const signalRows = signalEntries.value.map((item) => ({
    name: item.label,
    time: displayTimestamp.value,
    value: item.value.toFixed(1),
    status: '良好'
  }))
  const radarRows = radarDimensions.value.map((name, index) => ({
    name,
    time: displayTimestamp.value,
    value: `${Math.round(radarScores.value[index] ?? 0)}分`,
    status: (radarScores.value[index] ?? 0) >= 75 ? '良好' : '关注'
  }))
  return [...signalRows, ...radarRows].slice(0, 6)
})

const faults = computed(() =>
  subsystems.value
    .filter((item) => Number(item.status) > 1)
    .map((item) => ({
      status: statusTextByCode(item.status),
      level: Number(item.status) === 3 ? '3级' : '2级',
      time: displayTimestamp.value,
      part: item.name || '未知部位',
      duration: '--'
    }))
)

const leftCallouts = computed(() => [
  {
    line1: `信号1 ${signalEntries.value[0]?.value?.toFixed?.(1) ?? '0.0'}`,
    line2: `信号2 ${signalEntries.value[1]?.value?.toFixed?.(1) ?? '0.0'}`
  },
  {
    line1: `${subsystems.value[0]?.name || '子系统1'} ${statusTextByCode(subsystems.value[0]?.status)}`,
    line2: `${subsystems.value[1]?.name || '子系统2'} ${statusTextByCode(subsystems.value[1]?.status)}`
  },
  {
    line1: `信号3 ${signalEntries.value[2]?.value?.toFixed?.(1) ?? '0.0'}`,
    line2: `更新 ${displayTimestamp.value}`
  }
])

const rightCallouts = computed(() => [
  {
    line1: `模式 ${overview.value.system_mode || '--'}`,
    line2: `健康分 ${healthScore.value}`
  },
  {
    line1: `${radarDimensions.value[0] || '维度1'} ${Math.round(radarScores.value[0] ?? 0)}分`,
    line2: `${radarDimensions.value[1] || '维度2'} ${Math.round(radarScores.value[1] ?? 0)}分`
  },
  {
    line1: `${radarDimensions.value[2] || '维度3'} ${Math.round(radarScores.value[2] ?? 0)}分`,
    line2: `${radarDimensions.value[3] || '维度4'} ${Math.round(radarScores.value[3] ?? 0)}分`
  }
])

const heroTitle = computed(() => `${overview.value.system_mode || '--'} 模式 / 天线节点`)

const buildPolyline = (values) => {
  const safeValues = Array.isArray(values) && values.length ? values : [0, 0, 0, 0, 0, 0, 0]
  const startX = 20
  const endX = 380
  const step = safeValues.length === 1 ? 0 : (endX - startX) / (safeValues.length - 1)
  return safeValues
    .map((value, index) => {
      const x = Math.round(startX + step * index)
      const y = Math.round(160 - clamp(value) * 1.2)
      return `${x},${y}`
    })
    .join(' ')
}

const trendPolylines = computed(() => {
  const main = historyValues.value.length ? historyValues.value : [0, 0, 0, 0, 0, 0, 0]
  const secondary = main.map((value, index, arr) => {
    const prev = arr[index - 1] ?? value
    const next = arr[index + 1] ?? value
    return Math.round((prev + value + next) / 3)
  })
  const third = historyTimes.value.length
    ? historyTimes.value.map((_, index) => Math.round((radarScores.value[index % Math.max(radarScores.value.length, 1)] ?? 0) * 0.8))
    : main.map(() => Math.round((radarScores.value[0] ?? 0) * 0.8))

  return {
    main: buildPolyline(main),
    secondary: buildPolyline(secondary),
    third: buildPolyline(third)
  }
})

const alarmInfo = computed(() => {
  const firstAbnormal = subsystems.value.find((item) => Number(item.status) > 1)
  if (!firstAbnormal) {
    return {
      description: '当前未检测到子系统异常报警。',
      phenomenon: `系统模式 ${overview.value.system_mode || '--'}，整体状态 ${systemStatusText.value}。`,
      cause: '等待后端推送新的诊断结果。'
    }
  }

  return {
    description: `${firstAbnormal.name || '子系统'}状态为${statusTextByCode(firstAbnormal.status)}。`,
    phenomenon: `健康分 ${healthScore.value}，异常子系统数量 ${abnormalCount.value}。`,
    cause: '来源于 dashboard_json 子系统状态判定结果。'
  }
})

const maxAlarmLevel = computed(() =>
  subsystems.value.reduce((max, item) => Math.max(max, statusLevelByCode(item.status)), 0)
)

const hasActiveAlarm = computed(() => maxAlarmLevel.value >= 2)
const alarmSeverity = computed(() => (maxAlarmLevel.value >= 3 ? 'critical' : 'warning'))
const alarmBannerIcon = computed(() => (alarmSeverity.value === 'critical' ? '!' : '≈'))
const alarmBannerText = computed(() => {
  if (alarmSeverity.value === 'critical') {
    return `严重故障：${abnormalCount.value} 项异常，点击查看`
  }
  return `一般故障：${abnormalCount.value} 项异常，点击查看`
})

onMounted(() => {
  dashboardSocket = createDashboardSocket({
    onDashboardUpdate: (payload) => {
      dashboardPayload.value = payload
      lastUpdated.value = formatTime()
    }
  })
})

onUnmounted(() => {
  if (dashboardSocket) {
    dashboardSocket.disconnect()
    dashboardSocket = null
  }
})
</script>

<style scoped>
.health-screen {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: calc(100vh - 40px);
  color: #d4f7ff;
  background:
    radial-gradient(circle at 20% 20%, rgba(0, 192, 255, 0.15), transparent 30%),
    radial-gradient(circle at 80% 15%, rgba(64, 214, 255, 0.1), transparent 30%),
    linear-gradient(180deg, #02103a 0%, #031d5e 45%, #04144b 100%);
  border: 2px solid #0ac8f8;
  border-radius: 14px;
  padding: 12px;
  box-shadow:
    inset 0 0 40px rgba(15, 101, 193, 0.25),
    0 0 26px rgba(0, 176, 255, 0.22);
}

.corner-alarm {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  padding: 8px 12px 8px 10px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  cursor: pointer;
  color: #fff;
  background: rgba(8, 20, 46, 0.88);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.22);
  animation: alarmPulse 1s ease-in-out infinite;
}

.corner-alarm-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-weight: 800;
  line-height: 1;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.08);
}

.corner-alarm-text {
  font-size: 12px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.corner-alarm.severity-warning {
  border-color: rgba(255, 224, 102, 0.55);
  color: #fff6bf;
  background: linear-gradient(180deg, rgba(90, 66, 8, 0.92), rgba(58, 43, 6, 0.92));
  box-shadow:
    0 0 14px rgba(255, 217, 90, 0.35),
    inset 0 0 12px rgba(255, 202, 72, 0.16);
}

.corner-alarm.severity-warning .corner-alarm-icon {
  color: #2e2200;
  background: radial-gradient(circle, #ffe46f, #ffbf3d);
  box-shadow: 0 0 10px rgba(255, 216, 87, 0.45);
}

.corner-alarm.severity-critical {
  border-color: rgba(255, 107, 124, 0.62);
  color: #ffe1e6;
  background: linear-gradient(180deg, rgba(108, 14, 28, 0.92), rgba(69, 8, 16, 0.92));
  box-shadow:
    0 0 16px rgba(255, 82, 109, 0.36),
    inset 0 0 14px rgba(255, 95, 95, 0.18);
}

.corner-alarm.severity-critical .corner-alarm-icon {
  color: #fff;
  background: radial-gradient(circle, #ff5f74, #d31735);
  box-shadow: 0 0 12px rgba(255, 91, 114, 0.52);
}

@keyframes alarmPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.55;
    transform: scale(1.02);
  }
}

.health-screen::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background-image:
    linear-gradient(rgba(79, 167, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(79, 167, 255, 0.08) 1px, transparent 1px);
  background-size: 38px 38px;
}

.screen-header {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.screen-title {
  margin: 0;
  font-size: clamp(24px, 2vw, 36px);
  color: #f4fbff;
  letter-spacing: 4px;
  text-shadow: 0 0 16px rgba(114, 230, 255, 0.8);
  text-transform: uppercase;
}

.header-nav {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.header-nav-right {
  justify-content: flex-end;
}

.tab-chip {
  padding: 8px 12px;
  border: 1px solid #09cdf6;
  color: #91eaff;
  background: linear-gradient(180deg, rgba(8, 44, 96, 0.92), rgba(7, 33, 74, 0.92));
  clip-path: polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%);
  font-size: 13px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s ease;
}

.tab-chip:hover {
  transform: translateY(-1px);
  color: #e0f8ff;
  border-color: #50e1ff;
  box-shadow: 0 0 12px rgba(74, 213, 255, 0.35);
}

.screen-main {
  display: grid;
  gap: 12px;
  grid-template-columns: 280px 1fr 300px;
}

.panel-box {
  border: 1px solid rgba(25, 218, 255, 0.65);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(8, 31, 88, 0.92), rgba(4, 21, 68, 0.92));
  box-shadow:
    inset 0 0 18px rgba(0, 153, 255, 0.18),
    0 0 12px rgba(22, 176, 255, 0.25);
  backdrop-filter: blur(2px);
  position: relative;
}

.panel-box::after {
  content: "";
  position: absolute;
  inset: 5px;
  border: 1px solid rgba(100, 198, 255, 0.12);
  border-radius: 9px;
  pointer-events: none;
}

.card-title {
  margin: 0;
  font-size: 15px;
  color: #9be9ff;
}

.meta-row {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #7ddcff;
}

.left-col,
.right-col {
  display: grid;
  gap: 12px;
}

.info-card,
.chart-card,
.list-card,
.telemetry-card,
.alarm-card {
  padding: 12px;
}

.stats-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.stat-item {
  border: 1px solid rgba(63, 207, 255, 0.25);
  border-radius: 8px;
  background: rgba(9, 29, 77, 0.6);
  padding: 10px;
  box-shadow: inset 0 0 12px rgba(22, 162, 255, 0.18);
}

.label {
  margin: 0;
  color: #79cbe8;
  font-size: 12px;
}

.value {
  margin: 5px 0 0;
  font-size: 28px;
  font-weight: 700;
}

.ring-wrap {
  display: flex;
  justify-content: space-evenly;
  margin-top: 12px;
}

.ring {
  width: 94px;
  height: 94px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #f2fbff;
  font-weight: 700;
}

.ring span {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #042557;
  display: grid;
  place-items: center;
  border: 1px solid rgba(103, 227, 255, 0.45);
}

.ring-a {
  background: conic-gradient(#2cecff 0 65%, #123a72 65% 100%);
}

.ring-b {
  background: conic-gradient(#8f6cff 0 48%, #123a72 48% 100%);
}

.legend-row {
  margin-top: 12px;
  display: grid;
  gap: 6px;
  font-size: 12px;
}

.dot {
  width: 9px;
  height: 9px;
  display: inline-block;
  border-radius: 50%;
  margin-right: 6px;
}

.dot-cyan {
  background: #30e9ff;
}

.dot-green {
  background: #34ffa4;
}

.dot-purple {
  background: #8f78ff;
}

.center-col {
  display: grid;
  gap: 12px;
  grid-template-rows: auto auto;
}

.hero-card {
  padding: 8px 12px 12px;
}

.hero-top {
  text-align: center;
  color: #9adfff;
  padding: 4px 0 8px;
  border-bottom: 1px solid rgba(118, 214, 255, 0.22);
}

.hero-body {
  position: relative;
  min-height: 360px;
  display: grid;
  place-items: center;
  overflow: hidden;
}

.model-core {
  width: 230px;
  height: 290px;
  position: relative;
  transform: translateY(10px);
}

.antenna-dish {
  position: absolute;
  top: 0;
  width: 95px;
  height: 100px;
  background: linear-gradient(145deg, #49fcff, #1799da);
  border: 2px solid rgba(148, 250, 255, 0.45);
}

.antenna-dish.left {
  left: 12px;
  border-radius: 12px 80px 70px 30px;
  transform: rotate(12deg);
}

.antenna-dish.right {
  right: 12px;
  border-radius: 80px 12px 30px 70px;
  transform: rotate(-12deg);
}

.antenna-neck {
  position: absolute;
  left: 50%;
  top: 88px;
  transform: translateX(-50%);
  width: 60px;
  height: 100px;
  border-radius: 12px;
  background: linear-gradient(180deg, #e8edf4, #7d8fa9);
}

.antenna-base {
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 165px;
  height: 120px;
  border-radius: 36px 36px 18px 18px;
  background: linear-gradient(180deg, #f4b2ff, #b375da);
  border: 1px solid rgba(240, 205, 255, 0.45);
}

.callout {
  position: absolute;
  width: 220px;
  border: 1px dashed rgba(163, 250, 255, 0.5);
  background: rgba(2, 28, 54, 0.7);
  padding: 8px 12px;
  color: #39ff7d;
  font-size: 14px;
  line-height: 1.45;
  box-shadow: 0 0 12px rgba(54, 233, 147, 0.2);
}

.callout p {
  margin: 0;
}

.callout.left:nth-of-type(2) {
  top: 30px;
  left: 10px;
}

.callout.left:nth-of-type(3) {
  top: 130px;
  left: 0;
}

.callout.left:nth-of-type(4) {
  top: 228px;
  left: 10px;
}

.callout.right:nth-of-type(5) {
  top: 44px;
  right: 10px;
}

.callout.right:nth-of-type(6) {
  top: 144px;
  right: 0;
}

.callout.right:nth-of-type(7) {
  top: 238px;
  right: 10px;
}

.bottom-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: 1.2fr 1fr;
}

.table-card,
.trend-card {
  padding: 12px;
}

.row-head,
.row-item {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  font-size: 12px;
}

.table-card .row-head,
.table-card .row-item {
  grid-template-columns: 1fr 1fr 1.3fr 1fr 0.8fr;
}

.row-head {
  margin-top: 10px;
  color: #81dfff;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(125, 227, 255, 0.25);
}

.row-item {
  padding: 6px 0;
  color: #d9f6ff;
  border-bottom: 1px solid rgba(56, 143, 195, 0.2);
}

.trend-wrap {
  margin-top: 10px;
  background: rgba(6, 43, 91, 0.5);
  border: 1px solid rgba(83, 203, 255, 0.25);
  border-radius: 8px;
  padding: 8px;
  box-shadow: inset 0 0 12px rgba(80, 205, 255, 0.15);
}

.trend-svg {
  width: 100%;
  height: 180px;
}

.trend-svg polyline {
  fill: none;
  stroke: #ffb67b;
  stroke-width: 2.6;
}

.trend-svg .line2 {
  stroke: #59d9ff;
}

.trend-svg .line3 {
  stroke: #fff4ad;
}

.alarm-card {
  display: grid;
  gap: 8px;
}

.alarm-entry {
  cursor: pointer;
  transition: all 0.2s ease;
}

.alarm-entry:hover {
  transform: translateY(-1px);
  border-color: rgba(106, 229, 255, 0.92);
  box-shadow:
    inset 0 0 22px rgba(0, 180, 255, 0.24),
    0 0 14px rgba(45, 189, 255, 0.35);
}

.alarm-row {
  display: grid;
  grid-template-columns: 70px 1fr;
  border: 1px solid rgba(125, 220, 255, 0.23);
}

.alarm-row span {
  background: rgba(0, 136, 255, 0.35);
  padding: 10px;
  color: #b7f3ff;
  font-size: 13px;
}

.alarm-row p {
  margin: 0;
  padding: 10px;
  color: #d9f6ff;
  font-size: 13px;
}

.accent-green {
  color: #4bffa9;
}

.accent-cyan {
  color: #57eaff;
}

.accent-pink {
  color: #ff87cd;
}

.accent-yellow {
  color: #ffe56b;
}

@media (max-width: 1440px) {
  .screen-main {
    grid-template-columns: 1fr;
  }

  .hero-body {
    min-height: 340px;
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 880px) {
  .corner-alarm {
    position: static;
    width: 100%;
    justify-content: center;
    margin-bottom: 10px;
  }

  .screen-header {
    grid-template-columns: 1fr;
    justify-items: center;
  }

  .header-nav,
  .header-nav-right {
    justify-content: center;
  }

  .hero-body {
    min-height: 520px;
  }

  .callout {
    position: static;
    width: 100%;
    margin: 6px 0;
  }
}
</style>

