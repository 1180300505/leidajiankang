<template>
  <section class="history-screen">
    <header class="screen-header panel-box">
      <div class="header-left">数据概览页</div>
      <h1>健康评估历史查询</h1>
      <div class="header-right">
        <span>查询统计</span>
        <span>排名录入</span>
        <button @click="goHome">返回首页</button>
      </div>
    </header>

    <div class="main-layout">
      <aside class="left-menu panel-box">
        <button v-for="item in leftMenus" :key="item" class="menu-btn">{{ item }}</button>
      </aside>

      <main class="content">
        <section class="query-box panel-box">
          <div class="query-grid">
            <label>名称: <input /></label>
            <label>编号: <input /></label>
            <label>选择类型: <input /></label>
            <label>关键字: <input placeholder="请输入关键字" /></label>
            <label>起始日期: <input /></label>
            <label>终止日期: <input /></label>
            <label>星级: <input /></label>
            <label>关键字: <input placeholder="请输入关键字" /></label>
          </div>
          <div class="query-actions">
            <label><input type="checkbox" /> 方式一</label>
            <label><input type="checkbox" /> 方式二</label>
            <label><input type="checkbox" /> 方式三</label>
            <button>查询</button>
          </div>
        </section>

        <section class="info-row panel-box">
          <div>相关设备 <strong>CarDem1</strong></div>
          <div>平均信号变化 <strong>2-15</strong></div>
          <div>通信 <strong>三角波</strong></div>
          <div>平均故障情况 <strong>21.59h</strong></div>
          <div>传感器位置 <strong>主轴承2</strong></div>
        </section>

        <section class="chart-wrap panel-box">
          <aside class="vertical-title">多子系统评估历史</aside>
          <div class="chart-board">
            <svg viewBox="0 0 760 360">
              <g class="grid">
                <line x1="70" y1="40" x2="700" y2="40" />
                <line x1="70" y1="100" x2="700" y2="100" />
                <line x1="70" y1="160" x2="700" y2="160" />
                <line x1="70" y1="220" x2="700" y2="220" />
                <line x1="70" y1="280" x2="700" y2="280" />
              </g>
              <g class="axis-text">
                <text x="14" y="286">0</text>
                <text x="4" y="226">200</text>
                <text x="4" y="166">400</text>
                <text x="4" y="106">600</text>
                <text x="4" y="46">800</text>
              </g>

              <polyline points="70,210 160,215 250,225 340,210 430,235 520,230 610,235 700,220" class="line-red" />
              <polyline points="70,170 160,160 250,165 340,170 430,175 520,170 610,160 700,155" class="line-cyan" />
              <polyline points="70,130 160,120 250,115 340,118 430,90 520,80 610,72 700,66" class="line-orange" />

              <text x="60" y="205">120</text>
              <text x="150" y="200">132</text>
              <text x="240" y="210">101</text>
              <text x="330" y="202">134</text>
              <text x="420" y="227">74</text>
              <text x="510" y="220">130</text>
              <text x="690" y="210">210</text>

              <text x="60" y="166">220</text>
              <text x="150" y="156">182</text>
              <text x="240" y="161">191</text>
              <text x="330" y="166">234</text>
              <text x="420" y="170">260</text>
              <text x="510" y="165">330</text>
              <text x="690" y="160">310</text>

              <text x="60" y="126">120</text>
              <text x="150" y="116">102</text>
              <text x="240" y="111">121</text>
              <text x="330" y="114">124</text>
              <text x="420" y="86">110</text>
              <text x="510" y="76">120</text>
              <text x="690" y="62">110</text>
            </svg>

            <div class="action-box">
              <button>差值</button>
              <button>方差</button>
              <button>同期对比</button>
              <button>高级计算</button>
            </div>
            <div class="time-label">系统评估时间</div>
          </div>
        </section>
      </main>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const leftMenus = ['主界面', '主表格', '简易数学工具', '复杂数学工具', '切换健康模型', '视图调整工具', '生成对比报告']

const goHome = () => {
  router.push('/health')
}
</script>

<style scoped>
.history-screen {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: calc(100vh - 20px);
  color: #bdefff;
  background: linear-gradient(180deg, #031042 0%, #072d79 45%, #03185a 100%);
  border: 2px solid #0cbdf7;
  box-shadow:
    inset 0 0 36px rgba(23, 120, 214, 0.24),
    0 0 18px rgba(21, 177, 255, 0.24);
}

.history-screen::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background-image:
    linear-gradient(rgba(93, 180, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(93, 180, 255, 0.08) 1px, transparent 1px);
  background-size: 40px 40px;
}

.panel-box {
  border: 1px solid rgba(45, 197, 255, 0.55);
  background: linear-gradient(180deg, rgba(8, 34, 90, 0.88), rgba(4, 20, 63, 0.88));
  border-radius: 10px;
  backdrop-filter: blur(2px);
  position: relative;
}

.panel-box::after {
  content: "";
  position: absolute;
  inset: 5px;
  border: 1px solid rgba(99, 194, 255, 0.12);
  border-radius: 8px;
  pointer-events: none;
}

.screen-header {
  padding: 10px 14px;
  display: grid;
  grid-template-columns: 120px 1fr 330px;
  align-items: center;
}

.screen-header h1 {
  margin: 0;
  text-align: center;
  font-size: 42px;
  color: #edf8ff;
  text-shadow: 0 0 12px rgba(131, 220, 255, 0.32);
}

.header-left {
  font-size: 14px;
}

.header-right {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.header-right button {
  border: 1px solid #35bcff;
  background: #0f3e82;
  color: #c7f5ff;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.header-right button:hover {
  box-shadow: 0 0 12px rgba(98, 209, 255, 0.35);
  transform: translateY(-1px);
}

.main-layout {
  margin-top: 8px;
  display: grid;
  grid-template-columns: 190px 1fr;
  gap: 8px;
}

.left-menu {
  padding: 10px;
  display: grid;
  gap: 8px;
  align-content: start;
}

.menu-btn {
  border: 2px solid #4aaeff;
  background: linear-gradient(180deg, #0d2f72, #102d6a);
  color: #d1ecff;
  font-size: 30px;
  padding: 10px 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.menu-btn:hover {
  border-color: #7ce9ff;
  box-shadow: 0 0 14px rgba(110, 225, 255, 0.25);
  transform: translateY(-1px);
}

.content {
  display: grid;
  gap: 8px;
}

.query-box {
  padding: 10px;
}

.query-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(180px, 1fr));
  gap: 8px 14px;
}

.query-grid label {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 6px;
  align-items: center;
  font-size: 14px;
}

.query-grid input {
  height: 28px;
  border: 1px solid #3568a9;
  background: #3d4f66;
  color: #e8f7ff;
  border-radius: 4px;
}

.query-actions {
  display: flex;
  gap: 18px;
  align-items: center;
  margin-top: 10px;
}

.query-actions label {
  font-size: 14px;
}

.query-actions button {
  margin-left: 18px;
  background: linear-gradient(180deg, #4f80d8, #3e64c1);
  border: 1px solid #74b6ff;
  color: #e8f6ff;
  padding: 8px 20px;
  font-size: 28px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.query-actions button:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 12px rgba(118, 188, 255, 0.35);
}

.info-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  padding: 8px 10px;
  font-size: 13px;
}

.info-row strong {
  margin-left: 8px;
  color: #f8fbff;
}

.chart-wrap {
  min-height: 560px;
  display: grid;
  grid-template-columns: 70px 1fr;
  gap: 8px;
  padding: 12px;
}

.vertical-title {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  font-size: 36px;
  letter-spacing: 4px;
  border: 2px solid #4f8bff;
  display: grid;
  place-items: center;
  padding: 8px 0;
}

.chart-board {
  position: relative;
  border: 1px solid rgba(78, 164, 255, 0.3);
  background: rgba(4, 24, 76, 0.78);
  padding: 10px;
  border-radius: 8px;
  box-shadow: inset 0 0 18px rgba(81, 167, 255, 0.16);
}

.chart-board svg {
  width: 100%;
  height: 420px;
}

.grid line {
  stroke: rgba(198, 227, 255, 0.35);
  stroke-width: 1;
}

.axis-text text {
  fill: #9bbce7;
  font-size: 24px;
}

.line-red,
.line-cyan,
.line-orange {
  fill: none;
  stroke-width: 3;
}

.line-red {
  stroke: #f52b37;
}

.line-cyan {
  stroke: #9be8ff;
}

.line-orange {
  stroke: #e39674;
}

text {
  fill: #8796c4;
  font-size: 26px;
}

.action-box {
  position: absolute;
  right: 24px;
  bottom: 65px;
  display: grid;
  gap: 6px;
}

.action-box button {
  border: 2px solid #7cc6c7;
  background: #dfe9e8;
  color: #2b7777;
  font-size: 28px;
  padding: 6px 20px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.action-box button:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 12px rgba(124, 198, 199, 0.35);
}

.time-label {
  position: absolute;
  right: 16px;
  bottom: 12px;
  border: 2px solid #4f8bff;
  padding: 10px 30px;
  font-size: 28px;
}

@media (max-width: 1300px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .left-menu {
    grid-template-columns: repeat(3, 1fr);
  }

  .query-grid {
    grid-template-columns: repeat(2, minmax(180px, 1fr));
  }
}

@media (max-width: 900px) {
  .screen-header {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .screen-header h1 {
    font-size: 30px;
  }

  .header-right {
    justify-content: flex-start;
  }

  .left-menu {
    grid-template-columns: 1fr 1fr;
  }

  .info-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .chart-wrap {
    grid-template-columns: 1fr;
  }

  .vertical-title {
    writing-mode: horizontal-tb;
    font-size: 22px;
  }
}
</style>
