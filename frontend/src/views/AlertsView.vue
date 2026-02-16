<template>
  <section class="alert-screen">
    <header class="screen-header">
      <button class="nav-btn" @click="goBack">返回</button>
      <h1>故障告警</h1>
      <button class="nav-btn">生成故障报告</button>
    </header>

    <div class="top-grid">
      <article class="panel">
        <h2>设备健康状态</h2>
        <div class="pie-wrap">
          <div class="pie"></div>
          <ul>
            <li><i class="c1"></i> 正常: 405</li>
            <li><i class="c2"></i> 事件: 40</li>
            <li><i class="c3"></i> 异常: 30</li>
          </ul>
        </div>
      </article>

      <article class="panel center-panel">
        <h2>故障位置评估</h2>
        <div class="fault-bars">
          <div v-for="(item, i) in positionBars" :key="i" class="fault-row">
            <span>{{ item.name }}</span>
            <div class="track"><i :style="{ width: item.value }"></i></div>
            <em>{{ item.value }}</em>
          </div>
        </div>
        <div class="severity-box">
          <h3>故障严重程度评估</h3>
          <div class="severity-track">
            <i style="width: 65.5%"></i>
            <i style="width: 10.5%"></i>
            <i style="width: 10.5%"></i>
            <i style="width: 9.5%"></i>
          </div>
          <p class="severity-text">中等严重</p>
        </div>
      </article>

      <article class="panel device-panel">
        <h2>故障子系统</h2>
        <div class="device-model">
          <div class="dish left"></div>
          <div class="dish right"></div>
          <div class="neck"></div>
          <div class="base"></div>
          <span class="line l1"></span>
          <span class="line l2"></span>
          <span class="line l3"></span>
        </div>
      </article>
    </div>

    <div class="bottom-grid">
      <article class="panel chart">
        <h2>故障信号及数值</h2>
        <svg viewBox="0 0 320 180">
          <rect x="40" y="130" width="34" height="40" class="b1" />
          <rect x="95" y="75" width="34" height="95" class="b2" />
          <rect x="150" y="35" width="34" height="135" class="b3" />
          <rect x="205" y="75" width="34" height="95" class="b4" />
          <line x1="30" y1="170" x2="300" y2="170" class="axis" />
          <text x="45" y="176">NN</text>
          <text x="100" y="176">IP</text>
          <text x="155" y="176">NP</text>
          <text x="210" y="176">CPU</text>
        </svg>
      </article>

      <article class="panel chart">
        <h2>故障风险预测</h2>
        <svg viewBox="0 0 320 180">
          <polyline points="40,150 90,70 140,65 190,45 240,8" class="pline" />
          <line x1="30" y1="170" x2="300" y2="170" class="axis" />
          <text x="30" y="176">00:00</text>
          <text x="120" y="176">12:00</text>
          <text x="220" y="176">24:00</text>
        </svg>
      </article>

      <article class="panel chart">
        <h2>故障类型评估</h2>
        <div class="mini-bars">
          <div v-for="(item, i) in typeBars" :key="i" class="mini-row">
            <span>{{ item.name }}</span>
            <div class="multi-track">
              <i class="m1" :style="{ width: item.v1 }"></i>
              <i class="m2" :style="{ width: item.v2 }"></i>
              <i class="m3" :style="{ width: item.v3 }"></i>
              <i class="m4" :style="{ width: item.v4 }"></i>
            </div>
          </div>
        </div>
      </article>

      <article class="panel chart">
        <h2>故障评估分布</h2>
        <svg viewBox="0 0 320 180">
          <polygon points="160,20 250,70 220,150 100,150 70,70" class="mesh" />
          <polygon points="160,45 215,75 198,130 122,130 105,75" class="mesh" />
          <polygon points="160,30 230,70 206,142 114,120 82,78" class="shape1" />
          <polygon points="160,52 198,78 188,116 130,122 112,86" class="shape2" />
        </svg>
      </article>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push('/health')
}

const positionBars = [
  { name: '检查项一', value: '88.88%' },
  { name: '检查项二', value: '77.77%' },
  { name: '检查项三', value: '66.66%' },
  { name: '检查项四', value: '44.44%' },
  { name: '检查项五', value: '33.33%' }
]

const typeBars = [
  { name: '检查点一', v1: '18%', v2: '15%', v3: '22%', v4: '20%' },
  { name: '检查点二', v1: '16%', v2: '14%', v3: '21%', v4: '19%' },
  { name: '检查点三', v1: '14%', v2: '12%', v3: '24%', v4: '19%' },
  { name: '检查点四', v1: '13%', v2: '10%', v3: '18%', v4: '17%' },
  { name: '检查点五', v1: '9%', v2: '8%', v3: '13%', v4: '14%' }
]
</script>

<style scoped>
:root {
  --bg-1: #07153e;
  --bg-2: #0a2e73;
  --bg-3: #071a50;
  --line: rgba(83, 199, 255, 0.52);
  --line-soft: rgba(83, 199, 255, 0.2);
  --text-main: #d8f4ff;
  --text-dim: #9cdcf2;
  --danger: #ff5757;
  --accent: #65ddff;
}

.alert-screen {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: calc(100vh - 20px);
  padding: 10px;
  color: var(--text-main);
  border: 2px solid #1ec4ff;
  background:
    radial-gradient(1200px 500px at 50% -100px, rgba(95, 157, 255, 0.25), transparent 70%),
    radial-gradient(800px 360px at 90% 5%, rgba(39, 206, 255, 0.16), transparent 72%),
    linear-gradient(180deg, var(--bg-1), var(--bg-2) 48%, var(--bg-3));
  box-shadow:
    inset 0 0 44px rgba(14, 123, 224, 0.28),
    0 0 24px rgba(13, 177, 255, 0.35);
}

.alert-screen::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background-image:
    linear-gradient(rgba(97, 188, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(97, 188, 255, 0.08) 1px, transparent 1px);
  background-size: 34px 34px;
}

.screen-header {
  display: grid;
  grid-template-columns: 120px 1fr 170px;
  gap: 10px;
  align-items: center;
}

.screen-header h1 {
  margin: 0;
  text-align: center;
  background: linear-gradient(180deg, #143e8a, #102f6f);
  border: 1px solid var(--line);
  border-radius: 8px;
  color: #ff6a6a;
  font-size: 40px;
  letter-spacing: 4px;
  padding: 10px 0;
  text-shadow: 0 0 14px rgba(255, 102, 102, 0.45);
  box-shadow:
    inset 0 0 14px rgba(74, 164, 255, 0.25),
    0 0 12px rgba(38, 177, 255, 0.22);
}

.nav-btn {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, #2a61bf, #1d468f);
  color: #e6f8ff;
  font-size: 19px;
  border-radius: 8px;
  padding: 9px 10px;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  border-color: #8ce6ff;
  transform: translateY(-1px);
  box-shadow: 0 0 14px rgba(98, 213, 255, 0.38);
}

.panel {
  position: relative;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(8, 40, 102, 0.9), rgba(7, 27, 79, 0.9));
  box-shadow:
    inset 0 0 22px rgba(30, 171, 255, 0.2),
    0 0 10px rgba(35, 149, 255, 0.2);
  padding: 12px;
  backdrop-filter: blur(2px);
}

.panel::after {
  content: "";
  position: absolute;
  inset: 5px;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  pointer-events: none;
}

h2 {
  margin: 0 0 10px;
  display: inline-block;
  padding: 5px 12px;
  font-size: 16px;
  font-weight: 600;
  color: #9ce9ff;
  border: 1px solid rgba(96, 206, 255, 0.4);
  background: linear-gradient(180deg, rgba(28, 85, 170, 0.92), rgba(18, 54, 113, 0.92));
  border-radius: 6px;
}

.top-grid {
  margin-top: 10px;
  display: grid;
  gap: 10px;
  grid-template-columns: 1fr 1.5fr 1fr;
}

.pie-wrap {
  display: grid;
  place-items: center;
}

.pie {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: conic-gradient(#5f9dff 0 81%, #ff9d42 81% 92%, #d5ddf4 92% 100%);
  border: 1px solid rgba(138, 206, 255, 0.45);
  box-shadow: 0 0 16px rgba(88, 183, 255, 0.3);
}

.pie-wrap ul {
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
  width: 100%;
  display: flex;
  justify-content: space-around;
  font-size: 13px;
  color: var(--text-dim);
}

.pie-wrap i {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  display: inline-block;
  margin-right: 5px;
}

.c1 { background: #5f9dff; }
.c2 { background: #ff9d42; }
.c3 { background: #c6d2f9; }

.fault-row {
  display: grid;
  grid-template-columns: 72px 1fr 74px;
  gap: 8px;
  align-items: center;
  margin-bottom: 7px;
  font-size: 13px;
}

.fault-row span {
  color: var(--text-dim);
}

.track {
  height: 8px;
  border-radius: 999px;
  background: rgba(102, 189, 255, 0.2);
  overflow: hidden;
}

.track i {
  height: 100%;
  display: block;
  border-radius: 999px;
  background: linear-gradient(90deg, #7ee4ff, #4a8dff 60%, #ff6f6f);
}

.fault-row em {
  font-style: normal;
  color: #b9f0ff;
}

.severity-box {
  margin-top: 12px;
}

.severity-box h3 {
  margin: 0 0 8px;
  display: inline-block;
  font-size: 14px;
  font-weight: 600;
  color: #8ee8ff;
  border: 1px solid rgba(96, 206, 255, 0.4);
  background: linear-gradient(180deg, rgba(26, 83, 166, 0.9), rgba(17, 51, 106, 0.9));
  border-radius: 6px;
  padding: 4px 10px;
}

.severity-track {
  display: flex;
  height: 14px;
  border-radius: 999px;
  border: 1px solid rgba(125, 217, 255, 0.4);
  overflow: hidden;
}

.severity-track i:nth-child(1) { background: #22c55e; }
.severity-track i:nth-child(2) { background: #3b82f6; }
.severity-track i:nth-child(3) { background: #818cf8; }
.severity-track i:nth-child(4) { background: #ef4444; }

.severity-text {
  margin: 12px 0 0;
  text-align: center;
  color: #ff8080;
  font-size: 58px;
  font-weight: 700;
  letter-spacing: 2px;
  text-shadow: 0 0 18px rgba(255, 94, 94, 0.4);
}

.device-model {
  position: relative;
  height: 290px;
  display: grid;
  place-items: center;
}

.dish {
  position: absolute;
  top: 20px;
  width: 90px;
  height: 90px;
  background: linear-gradient(145deg, #53f7ff, #1b9bd9);
  border: 1px solid rgba(110, 230, 255, 0.45);
}

.dish.left {
  left: 55px;
  border-radius: 12px 75px 65px 26px;
  transform: rotate(10deg);
}

.dish.right {
  right: 55px;
  border-radius: 75px 12px 26px 65px;
  transform: rotate(-10deg);
}

.neck {
  position: absolute;
  top: 105px;
  width: 56px;
  height: 100px;
  border-radius: 10px;
  background: linear-gradient(180deg, #f4f8ff, #8ea0bb);
}

.base {
  position: absolute;
  bottom: 15px;
  width: 150px;
  height: 110px;
  border-radius: 30px 30px 16px 16px;
  background: linear-gradient(180deg, #f4b3ff, #b277de);
}

.line {
  position: absolute;
  left: 10px;
  right: 10px;
  height: 2px;
  background: #ff4b4b;
  box-shadow: 0 0 10px rgba(255, 84, 84, 0.45);
}

.l1 { top: 78px; }
.l2 { top: 126px; }
.l3 { top: 170px; }

.bottom-grid {
  margin-top: 10px;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(4, 1fr);
}

.chart svg {
  width: 100%;
  height: 200px;
  filter: drop-shadow(0 0 6px rgba(78, 174, 255, 0.2));
}

.axis {
  stroke: rgba(173, 229, 255, 0.55);
  stroke-width: 1.5;
}

.b1 { fill: #5384f0; }
.b2 { fill: #4b89fb; }
.b3 { fill: #5680ff; }
.b4 { fill: #4f81ea; }

.pline {
  fill: none;
  stroke: #74a5ff;
  stroke-width: 3;
}

.mini-bars {
  margin-top: 8px;
  display: grid;
  gap: 8px;
}

.mini-row {
  display: grid;
  grid-template-columns: 52px 1fr;
  gap: 6px;
  align-items: center;
  font-size: 12px;
}

.mini-row span {
  color: var(--text-dim);
}

.multi-track {
  height: 12px;
  display: flex;
  border-radius: 999px;
  overflow: hidden;
}

.multi-track i { display: block; height: 100%; }
.m1 { background: #ff9d3a; }
.m2 { background: #4e8ffe; }
.m3 { background: #66adff; }
.m4 { background: #9e89e9; }

.mesh {
  fill: none;
  stroke: rgba(109, 161, 255, 0.45);
}

.shape1 {
  fill: rgba(104, 72, 245, 0.58);
}

.shape2 {
  fill: rgba(67, 215, 255, 0.56);
}

@media (max-width: 1200px) {
  .top-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }

  .severity-text {
    font-size: 42px;
  }
}

@media (max-width: 900px) {
  .screen-header {
    grid-template-columns: 1fr;
  }

  .screen-header h1 {
    font-size: 30px;
  }
}
</style>
