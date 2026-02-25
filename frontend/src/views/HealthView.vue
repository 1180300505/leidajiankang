<template>
  <section class="health-screen">
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
            <span>设备: 节点1</span>
            <span>时间: 2025-11</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <p class="label">健康分数</p>
              <p class="value accent-pink">95</p>
            </div>
            <div class="stat-item">
              <p class="label">运行时长</p>
              <p class="value accent-cyan">105d</p>
            </div>
            <div class="stat-item">
              <p class="label">异常次数</p>
              <p class="value accent-yellow">0</p>
            </div>
            <div class="stat-item">
              <p class="label">设备状态</p>
              <p class="value accent-green">运行中</p>
            </div>
          </div>
        </article>

        <article class="panel-box chart-card">
          <h2 class="card-title">设备运行状态监测</h2>
          <div class="meta-row">
            <span>设备: 节点1</span>
            <span>时间: 2025-11</span>
          </div>
          <div class="ring-wrap">
            <div class="ring ring-a"><span>18</span></div>
            <div class="ring ring-b"><span>30</span></div>
          </div>
          <div class="legend-row">
            <span><i class="dot dot-cyan"></i> 动作停止</span>
            <span><i class="dot dot-green"></i> 速度控制器</span>
            <span><i class="dot dot-purple"></i> 伺服驱动</span>
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
          <div class="hero-top">101 天线节点</div>
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
                <polyline points="20,130 80,80 140,110 200,60 260,100 320,50 380,95" />
                <polyline points="20,100 80,120 140,70 200,90 260,75 320,95 380,70" class="line2" />
                <polyline points="20,150 80,145 140,132 200,140 260,120 320,128 380,122" class="line3" />
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
          <div class="alarm-row"><span>描述</span><p>方位电机短时电流波动超阈值。</p></div>
          <div class="alarm-row"><span>现象</span><p>瞬态抖动，控制恢复后回到稳定区间。</p></div>
          <div class="alarm-row"><span>原因</span><p>环境突变与负载瞬时偏移叠加导致。</p></div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const topLeftTabs = [
  { label: 'IP设置', route: '/demo/ip' },
  { label: '设备管理' },
  { label: '系统自检' },
  { label: '状态监测' },
  { label: '数据管理', route: '/realtime' }
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
  router.push('/alerts')
}

const leftCallouts = [
  { line1: '俯仰电机1电流    4.37', line2: '俯仰驱动器        加电' },
  { line1: '方位减速机1      正常', line2: '方位减速机2      正常' },
  { line1: '方位电机1电流    4.37', line2: '方位驱动器        加电' }
]

const rightCallouts = [
  { line1: '当前俯仰角      2.37°', line2: '俯仰命令角      2.15°' },
  { line1: '当前方位角      8.98°', line2: '方位命令角      7.24°' },
  { line1: '方位电机2电流    2.87', line2: '方位驱动器        加电' }
]

const motors = [
  { name: '电机1', time: '2026-02-01 12:30:54', current: '1.24 A', status: '良好' },
  { name: '电机2', time: '2026-02-01 11:35:57', current: '1.74 A', status: '良好' },
  { name: '电机3', time: '2026-02-01 10:09:33', current: '1.24 A', status: '良好' },
  { name: '电机4', time: '2026-02-01 09:27:04', current: '2.01 A', status: '良好' }
]

const faults = [
  { status: '电流波动', level: '3级', time: '2025-10-05 18:01:21', part: '方位电机1', duration: '1小时' },
  { status: '转速异常', level: '3级', time: '2025-10-05 18:01:21', part: '方位电机1', duration: '1小时' },
  { status: '振动异常', level: '2级', time: '2025-10-05 18:01:21', part: '方位减速器2', duration: '5小时' },
  { status: '变形偏差', level: '1级', time: '2025-10-05 18:01:21', part: '主轴', duration: '2小时' }
]

const feedback = [
  { name: '当前俯仰角输出', time: '2026-02-01 05:03:40', value: '1.37°', status: '良好' },
  { name: '预计方位角输出', time: '2026-02-01 04:18:12', value: '5.35°', status: '良好' },
  { name: '预计俯仰角输出', time: '2026-02-01 03:55:52', value: '0.52°', status: '良好' },
  { name: '测量方位角输出', time: '2026-02-01 02:20:17', value: '1.14°', status: '良好' }
]
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

