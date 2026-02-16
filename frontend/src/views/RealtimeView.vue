<template>
  <section class="rt-screen">
    <header class="rt-header panel">
      <button class="header-btn" @click="goMainPage">主菜单</button>
      <h1>系统动态实时数据</h1>
      <button class="header-btn">生成数据报告</button>
    </header>

    <div class="rt-grid">
      <article class="panel block chart-line">
        <h2>多航迹趋势预测</h2>
        <svg viewBox="0 0 360 170">
          <line x1="40" y1="20" x2="40" y2="150" class="axis" />
          <line x1="40" y1="150" x2="340" y2="150" class="axis" />
          <polyline points="60,55 115,95 170,45 225,110 280,65" class="line-cyan" />
          <polyline points="60,80 115,115 170,48 225,85 280,62" class="line-yellow" />
          <polyline points="60,92 115,120 170,50 225,128 280,70" class="line-red" />
        </svg>
      </article>

      <article class="panel block eval">
        <h2>算法评估</h2>
        <div class="table-head"><span>指标</span><span>算法1</span><span>算法2</span><span>算法3</span></div>
        <div class="table-row"><span>精确度</span><span class="ok">5.0</span><span class="warn">9.5</span><span class="bad">12.2</span></div>
        <div class="table-row"><span>一致性</span><span class="ok">4.8</span><span class="warn">9.5</span><span class="bad">12.2</span></div>
        <div class="table-row"><span>计算效率</span><span class="ok">4.8</span><span class="warn">9.5</span><span class="bad">12.2</span></div>
      </article>

      <article class="panel block kpi">
        <h2>关键指标</h2>
        <div class="bar-item"><span>误报率</span><div class="bar"><i style="width: 18%"></i></div><em>12.2</em></div>
        <div class="bar-item"><span>漏报率</span><div class="bar"><i style="width: 8%"></i></div><em>8</em></div>
        <div class="bar-item"><span>相应时间</span><div class="bar"><i style="width: 52%"></i></div><em>50ms</em></div>
      </article>

      <article class="panel block bars">
        <h2>关键信号变数值</h2>
        <div v-for="(v, i) in signalBars" :key="i" class="hbar">
          <span>x{{ i + 1 }}</span>
          <div class="htrack"><i :style="{ width: v + '%' }"></i></div>
        </div>
      </article>

      <article class="panel block gauge">
        <h2>系统健康状态</h2>
        <div class="dial-wrap">
          <div class="dial">
            <div class="dial-inner">危险</div>
          </div>
        </div>
      </article>

      <article class="panel block subsystem">
        <h2>子系统健康状态</h2>
        <div class="sys-grid">
          <p v-for="(item, i) in subsystems" :key="i">
            <span>{{ item.name }}</span>
            <strong>{{ item.score }}</strong>
          </p>
        </div>
      </article>

      <article class="panel block radar radar-1">
        <h2>方位轴状态雷达图</h2>
        <div class="radar-plot">
          <svg viewBox="0 0 170 140">
            <polygon points="85,15 145,55 122,120 48,120 25,55" class="mesh" />
            <polygon points="85,35 126,61 111,105 59,105 44,61" class="mesh" />
            <polygon points="85,55 108,69 100,90 70,90 62,69" class="mesh" />
            <polygon points="85,28 130,55 115,110 57,105 43,60" class="shape" />
          </svg>
        </div>
      </article>

      <article class="panel block radar radar-2">
        <h2>俯仰轴状态雷达图</h2>
        <div class="radar-plot">
          <svg viewBox="0 0 170 140">
            <polygon points="85,15 145,55 122,120 48,120 25,55" class="mesh" />
            <polygon points="85,35 126,61 111,105 59,105 44,61" class="mesh" />
            <polygon points="85,55 108,69 100,90 70,90 62,69" class="mesh" />
            <polygon points="85,42 117,60 107,96 64,92 51,64" class="shape" />
          </svg>
        </div>
      </article>

      <article class="panel block radar radar-3">
        <h2>方位轴状态雷达图</h2>
        <div class="radar-plot">
          <svg viewBox="0 0 170 140">
            <polygon points="85,15 145,55 122,120 48,120 25,55" class="mesh" />
            <polygon points="85,35 126,61 111,105 59,105 44,61" class="mesh" />
            <polygon points="85,55 108,69 100,90 70,90 62,69" class="mesh" />
            <polygon points="85,24 136,55 118,116 52,111 38,62" class="shape" />
          </svg>
        </div>
      </article>

      <article class="panel block actions">
        <button>数据钻取</button>
        <button>部件实时数据</button>
        <button>数据显示设置</button>
      </article>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goMainPage = () => {
  router.push('/health')
}

const signalBars = [78, 22, 65, 20, 24]
const subsystems = [
  { name: '子系统0', score: '5.0' },
  { name: '子系统1', score: '5.3' },
  { name: '子系统2', score: '4.8' },
  { name: '子系统3', score: '4.8' },
  { name: '子系统4', score: '5.0' },
  { name: '子系统5', score: '5.0' },
  { name: '子系统6', score: '4.8' },
  { name: '子系统7', score: '4.8' }
]
</script>

<style scoped>
.rt-screen {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: calc(100vh - 20px);
  padding: 8px;
  color: #b8efff;
  background:
    radial-gradient(circle at 20% 20%, rgba(0, 188, 255, 0.18), transparent 35%),
    linear-gradient(180deg, #041241 0%, #062a78 50%, #031a5f 100%);
  border: 2px solid #0dc0ff;
  box-shadow:
    inset 0 0 40px rgba(27, 120, 229, 0.24),
    0 0 22px rgba(0, 167, 255, 0.28);
}

.rt-screen::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background-image:
    linear-gradient(rgba(90, 180, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(90, 180, 255, 0.08) 1px, transparent 1px);
  background-size: 34px 34px;
}

.panel {
  border: 1px solid rgba(39, 197, 255, 0.5);
  background: linear-gradient(180deg, rgba(6, 51, 113, 0.84), rgba(6, 35, 90, 0.84));
  box-shadow: inset 0 0 22px rgba(31, 152, 245, 0.2);
  border-radius: 10px;
  backdrop-filter: blur(2px);
  position: relative;
}

.panel::after {
  content: "";
  position: absolute;
  inset: 4px;
  border-radius: 8px;
  border: 1px solid rgba(98, 194, 255, 0.14);
  pointer-events: none;
}

.rt-header {
  display: grid;
  grid-template-columns: 140px 1fr 160px;
  align-items: center;
  gap: 12px;
  padding: 8px;
}

.rt-header h1 {
  margin: 0;
  text-align: center;
  color: #eff9ff;
  font-size: 38px;
  letter-spacing: 2px;
}

.header-btn {
  border: 1px solid #2eb2ff;
  background: linear-gradient(180deg, #3c7fdd, #1a4fa6);
  color: #d8f3ff;
  padding: 8px 10px;
  font-size: 16px;
  transition: all 0.2s ease;
}

.header-btn:hover {
  border-color: #5ee7ff;
  transform: translateY(-1px);
  box-shadow: 0 0 14px rgba(86, 212, 255, 0.35);
}

.rt-grid {
  margin-top: 8px;
  display: grid;
  gap: 8px;
  grid-template-columns: 1.15fr 1fr 1fr 0.9fr;
  grid-template-areas:
    "line line eval kpi"
    "bars gauge subsystem subsystem"
    "radar1 radar2 radar3 actions";
}

.block {
  padding: 8px 10px;
}

h2 {
  margin: 0 0 8px;
  font-size: 26px;
  color: #9de8ff;
  letter-spacing: 1px;
}

.chart-line {
  grid-area: line;
}

.chart-line svg {
  width: 100%;
  height: 170px;
}

.axis {
  stroke: #d2f9ff;
  stroke-width: 2;
}

.line-cyan,
.line-yellow,
.line-red {
  fill: none;
  stroke-width: 3;
}

.line-cyan {
  stroke: #38f5de;
}

.line-yellow {
  stroke: #efef4d;
}

.line-red {
  stroke: #f13b48;
}

.eval {
  grid-area: eval;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: 1.3fr 1fr 1fr 1fr;
  font-size: 22px;
  padding: 6px 0;
}

.table-head {
  color: #9bd9ff;
  border-bottom: 1px solid rgba(117, 212, 255, 0.35);
}

.ok {
  color: #37ff9f;
}

.warn {
  color: #fbdf4d;
}

.bad {
  color: #ff5159;
}

.kpi {
  grid-area: kpi;
}

.bar-item {
  display: grid;
  grid-template-columns: 70px 1fr 55px;
  gap: 10px;
  align-items: center;
  margin-bottom: 14px;
  font-size: 19px;
}

.bar {
  height: 16px;
  background: rgba(102, 190, 255, 0.18);
  border: 1px solid rgba(77, 172, 255, 0.35);
}

.bar i {
  height: 100%;
  display: block;
  background: linear-gradient(90deg, #2cd7ff, #1c72ff);
}

.bars {
  grid-area: bars;
}

.hbar {
  display: grid;
  grid-template-columns: 34px 1fr;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.htrack {
  height: 16px;
  background: rgba(204, 236, 255, 0.14);
}

.htrack i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #97b5ff, #4e69c9);
}

.gauge {
  grid-area: gauge;
}

.dial-wrap {
  display: grid;
  place-items: center;
  padding-top: 8px;
}

.dial {
  width: 190px;
  height: 190px;
  border-radius: 50%;
  background: conic-gradient(#ff2f46 0 48%, #d6f3ff 48% 78%, transparent 78% 100%);
  display: grid;
  place-items: center;
}

.dial-inner {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: #0a3a6b;
  display: grid;
  place-items: center;
  color: #ff2f46;
  font-size: 48px;
  font-weight: 700;
}

.subsystem {
  grid-area: subsystem;
}

.sys-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 14px;
  margin-top: 8px;
}

.sys-grid p {
  margin: 0;
  font-size: 30px;
  display: flex;
  justify-content: space-between;
}

.sys-grid strong {
  color: #41ff87;
}

.radar {
  min-height: 210px;
}

.radar-1 {
  grid-area: radar1;
}

.radar-2 {
  grid-area: radar2;
}

.radar-3 {
  grid-area: radar3;
}

.radar-plot {
  background:
    radial-gradient(circle at 50% 30%, rgba(111, 173, 255, 0.22), transparent 60%),
    rgba(6, 20, 58, 0.95);
  border: 1px solid rgba(98, 177, 255, 0.42);
  border-radius: 6px;
  height: 165px;
  display: grid;
  place-items: center;
}

.radar-plot svg {
  width: 165px;
  height: 130px;
}

.mesh {
  fill: none;
  stroke: rgba(159, 197, 255, 0.55);
  stroke-width: 1;
}

.shape {
  fill: rgba(49, 114, 255, 0.18);
  stroke: #3f65d8;
  stroke-width: 2;
}

.actions {
  grid-area: actions;
  display: grid;
  gap: 10px;
}

.actions button {
  height: 46px;
  border: 1px solid #13cfff;
  background: linear-gradient(180deg, rgba(24, 174, 238, 0.55), rgba(10, 109, 158, 0.55));
  color: #abf0ff;
  font-size: 26px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.actions button:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 12px rgba(72, 221, 255, 0.3);
}

@media (max-width: 1400px) {
  .rt-header h1 {
    font-size: 30px;
  }

  h2 {
    font-size: 20px;
  }

  .table-head,
  .table-row,
  .sys-grid p,
  .actions button {
    font-size: 16px;
  }
}

@media (max-width: 980px) {
  .rt-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "line"
      "eval"
      "kpi"
      "bars"
      "gauge"
      "subsystem"
      "radar1"
      "radar2"
      "radar3"
      "actions";
  }

  .rt-header {
    grid-template-columns: 1fr;
  }
}
</style>
