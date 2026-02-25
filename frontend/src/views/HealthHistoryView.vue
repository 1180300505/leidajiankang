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
        <button
          v-for="item in leftMenus"
          :key="item"
          class="menu-btn"
          :class="{ 'is-active': activeMenu === item }"
          @click="selectLeftMenu(item)"
        >
          {{ item }}
        </button>
      </aside>

      <main class="content">
        <template v-if="activeMenu === leftMenus[0]">
        <section class="workspace-panel panel-box">
          <div class="workspace-headline">
            <div class="workspace-title">历史查询与数据监控中心</div>
            <div class="workspace-meta">查询条件 + 摘要信息 + 监控日志一体化展示</div>
          </div>

          <div class="top-controls">
            <section class="query-box workspace-card">
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

            <section class="info-row workspace-card">
              <div>相关设备 <strong>CarDem1</strong></div>
              <div>平均信号变化 <strong>2-15</strong></div>
              <div>通信 <strong>三角波</strong></div>
              <div>平均故障情况 <strong>21.59h</strong></div>
              <div>传感器位置 <strong>主轴承2</strong></div>
            </section>
          </div>

        <section class="monitor-panel workspace-card">
          <div class="monitor-header">
            <div class="monitor-title">设备运行日志监控 (SQLite + Flask)</div>
            <div class="monitor-actions">
              <el-button type="primary" @click="fetchData(currentPage)">刷新列表</el-button>
            </div>
          </div>

          <div class="monitor-toolbar">
            <el-date-picker
              v-model="dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="导出开始时间"
              end-placeholder="导出结束时间"
              value-format="YYYY-MM-DD HH:mm:ss"
              :default-time="[new Date(2000, 1, 1, 0, 0, 0), new Date(2000, 1, 1, 23, 59, 59)]"
            />
            <el-button type="warning" :icon="Download" @click="handleExport">
              导出详细 Word 报告
            </el-button>
          </div>

          <el-table
            :data="tableData"
            stripe
            border
            v-loading="loading"
            @sort-change="handleSortChange"
            class="monitor-table"
          >
            <el-table-column prop="id" label="ID" width="70" align="center" />
            <el-table-column prop="timestamp" label="记录时间" width="180" sortable="custom" />

            <el-table-column label="系统状态">
              <el-table-column prop="sys_mode" label="模式" width="90" />
              <el-table-column prop="sys_lock_status" label="锁定状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.sys_lock_status === '已锁定' ? 'success' : 'warning'">
                    {{ scope.row.sys_lock_status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table-column>

            <el-table-column label="电机参数">
              <el-table-column prop="m1_temp" label="电机1温度" width="110">
                <template #default="scope">{{ scope.row.m1_temp }} °C</template>
              </el-table-column>
              <el-table-column prop="m2_temp" label="电机2温度" width="110">
                <template #default="scope">{{ scope.row.m2_temp }} °C</template>
              </el-table-column>
            </el-table-column>

            <el-table-column label="操作" width="100" fixed="right" align="center">
              <template #default="scope">
                <el-popconfirm title="确定要删除这条记录吗？" @confirm="handleDelete(scope.row.id)">
                  <template #reference>
                    <el-button type="danger" size="small" link>删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </section>
        </section>
        </template>

        <section v-else class="placeholder-panel panel-box">
          <div class="placeholder-header">
            <h2 class="placeholder-title">{{ activeMenu }}</h2>
            <span class="placeholder-subtitle">功能预留（右侧界面样式切换示例）</span>
          </div>
          <div class="placeholder-body" :data-variant="activeMenu">
            <div class="placeholder-grid">
              <div class="placeholder-card wide"></div>
              <div class="placeholder-card"></div>
              <div class="placeholder-card"></div>
              <div class="placeholder-card tall"></div>
              <div class="placeholder-card"></div>
              <div class="placeholder-card"></div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { API_PREFIX } from '../config/backend'

const router = useRouter()
const leftMenus = ['主界面', '主表格', '简易数学工具', '复杂数学工具', '切换健康模型', '视图调整工具', '生成对比报告']
const activeMenu = ref(leftMenus[0])

const goHome = () => {
  router.push('/health')
}

const selectLeftMenu = (item) => {
  activeMenu.value = item
}

const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const currentSort = ref('DESC')
const dateRange = ref([])

const fetchData = async (page = 1) => {
  loading.value = true
  try {
    const response = await axios.get(`${API_PREFIX}/logs`, {
      params: {
        page,
        page_size: pageSize.value,
        sort: currentSort.value
      }
    })
    tableData.value = response.data.items || []
    total.value = response.data.total || 0
  } catch {
    ElMessage.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

const handleExport = () => {
  if (!dateRange.value || dateRange.value.length < 2) {
    ElMessage.warning('请先选择需要导出的日期范围')
    return
  }
  const [start, end] = dateRange.value
  const exportUrl = `${API_PREFIX}/export/docx?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`
  window.open(exportUrl, '_blank')
  ElMessage.success('正在准备报告，请稍候...')
}

const handleSortChange = ({ prop, order }) => {
  if (prop === 'timestamp') {
    currentSort.value = order === 'ascending' ? 'ASC' : 'DESC'
    currentPage.value = 1
    fetchData(1)
  }
}

const handlePageChange = (val) => {
  currentPage.value = val
  fetchData(val)
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchData(1)
}

const handleDelete = async (id) => {
  try {
    await axios.delete(`${API_PREFIX}/logs/${id}`)
    ElMessage.success('记录已删除')
    if (tableData.value.length === 1 && currentPage.value > 1) {
      currentPage.value -= 1
    }
    fetchData(currentPage.value)
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchData(1)
})
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
  box-shadow: inset 0 0 36px rgba(23, 120, 214, 0.24), 0 0 18px rgba(21, 177, 255, 0.24);
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

.menu-btn.is-active {
  border-color: #89f0ff;
  color: #effbff;
  background:
    linear-gradient(180deg, rgba(53, 120, 228, 0.9), rgba(26, 72, 164, 0.95));
  box-shadow:
    inset 0 0 14px rgba(146, 235, 255, 0.16),
    0 0 16px rgba(91, 220, 255, 0.28);
}

.content {
  display: grid;
  gap: 8px;
}

.workspace-panel {
  padding: 12px;
}

.workspace-headline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 8px 10px 12px;
  margin-bottom: 10px;
  border-bottom: 1px solid rgba(88, 196, 255, 0.18);
}

.workspace-title {
  font-size: 18px;
  font-weight: 700;
  color: #b8efff;
  letter-spacing: 1px;
}

.workspace-meta {
  font-size: 12px;
  color: #87dfff;
}

.top-controls {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}

.workspace-card {
  position: relative;
  border-radius: 10px;
  border: 1px solid rgba(73, 191, 255, 0.24);
  background:
    linear-gradient(180deg, rgba(11, 39, 95, 0.74), rgba(7, 24, 67, 0.82));
  box-shadow:
    inset 0 0 16px rgba(76, 171, 255, 0.08),
    0 0 8px rgba(33, 128, 218, 0.08);
}

.workspace-card::after {
  content: "";
  position: absolute;
  inset: 4px;
  border-radius: 8px;
  border: 1px solid rgba(97, 202, 255, 0.08);
  pointer-events: none;
}

.placeholder-panel {
  min-height: 920px;
  padding: 16px;
}

.placeholder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.placeholder-title {
  margin: 0;
  font-size: 20px;
  color: #b9efff;
  letter-spacing: 2px;
}

.placeholder-subtitle {
  color: #84dfff;
  font-size: 13px;
}

.placeholder-body {
  min-height: 840px;
  border: 1px solid rgba(88, 193, 255, 0.2);
  border-radius: 10px;
  padding: 12px;
  background:
    radial-gradient(circle at 20% 20%, rgba(72, 206, 255, 0.12), transparent 40%),
    linear-gradient(180deg, rgba(7, 28, 74, 0.75), rgba(4, 17, 54, 0.8));
  box-shadow: inset 0 0 22px rgba(60, 160, 255, 0.14);
}

.placeholder-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: 1.4fr 1fr 1fr;
  grid-auto-rows: 160px;
}

.placeholder-card {
  border-radius: 10px;
  border: 1px solid rgba(98, 198, 255, 0.26);
  background:
    linear-gradient(180deg, rgba(11, 45, 109, 0.8), rgba(8, 25, 71, 0.8));
  box-shadow:
    inset 0 0 18px rgba(77, 174, 255, 0.12),
    0 0 10px rgba(32, 124, 214, 0.12);
}

.placeholder-card.wide {
  grid-column: 1 / span 2;
}

.placeholder-card.tall {
  grid-row: span 2;
}

.placeholder-body[data-variant='主表格'] .placeholder-card {
  background:
    linear-gradient(180deg, rgba(12, 62, 110, 0.8), rgba(9, 36, 77, 0.8));
}

.placeholder-body[data-variant='简易数学工具'] .placeholder-card {
  background:
    linear-gradient(180deg, rgba(25, 78, 118, 0.78), rgba(9, 35, 68, 0.82));
}

.placeholder-body[data-variant='复杂数学工具'] .placeholder-card {
  background:
    linear-gradient(180deg, rgba(40, 72, 132, 0.78), rgba(15, 28, 76, 0.82));
}

.placeholder-body[data-variant='切换健康模型'] .placeholder-card {
  background:
    linear-gradient(180deg, rgba(24, 95, 132, 0.78), rgba(10, 34, 77, 0.82));
}

.placeholder-body[data-variant='视图调整工具'] .placeholder-card {
  background:
    linear-gradient(180deg, rgba(22, 66, 122, 0.78), rgba(8, 25, 68, 0.82));
}

.placeholder-body[data-variant='生成对比报告'] .placeholder-card {
  background:
    linear-gradient(180deg, rgba(44, 76, 136, 0.78), rgba(14, 29, 77, 0.82));
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
}

.info-row {
  display: grid;
  grid-template-columns: 1fr;
  align-content: start;
  gap: 8px;
  padding: 10px;
  font-size: 13px;
}

.info-row > div {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(91, 191, 255, 0.14);
  background: rgba(11, 36, 83, 0.45);
}

.info-row strong {
  margin-left: 8px;
  color: #f8fbff;
  font-weight: 700;
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

.line-red { stroke: #f52b37; }
.line-cyan { stroke: #9be8ff; }
.line-orange { stroke: #e39674; }

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
}

.time-label {
  position: absolute;
  right: 16px;
  bottom: 12px;
  border: 2px solid #4f8bff;
  padding: 10px 30px;
  font-size: 28px;
}

.monitor-panel {
  padding: 12px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-bottom: 10px;
  margin-bottom: 6px;
  border-bottom: 1px solid rgba(88, 196, 255, 0.14);
}

.monitor-title {
  color: #aeeaff;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 1px;
}

.monitor-toolbar {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid rgba(94, 190, 255, 0.16);
  background: rgba(9, 31, 78, 0.42);
}

.monitor-table {
  margin-top: 12px;
}

.pagination-container {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid rgba(88, 196, 255, 0.12);
}

:deep(.monitor-table .el-table) {
  --el-table-bg-color: rgba(8, 28, 70, 0.9);
  --el-table-tr-bg-color: rgba(8, 28, 70, 0.9);
  --el-table-header-bg-color: rgba(14, 52, 120, 0.95);
  --el-table-border-color: rgba(86, 187, 255, 0.25);
  --el-table-row-hover-bg-color: rgba(42, 114, 204, 0.18);
  --el-table-text-color: #d9f4ff;
  --el-table-header-text-color: #9fe7ff;
  --el-fill-color-blank: transparent;
  background: transparent;
}

:deep(.monitor-table .el-table__inner-wrapper::before) {
  background-color: rgba(86, 187, 255, 0.25);
}

:deep(.monitor-table .el-table__header-wrapper),
:deep(.monitor-table .el-table__body-wrapper),
:deep(.monitor-table .el-table__footer-wrapper),
:deep(.monitor-table .el-table__fixed),
:deep(.monitor-table .el-table__fixed-right),
:deep(.monitor-table .el-table__fixed-body-wrapper),
:deep(.monitor-table .el-table__fixed-header-wrapper) {
  background: transparent !important;
}

:deep(.monitor-table .el-table th.el-table__cell) {
  background: rgba(14, 52, 120, 0.82) !important;
}

:deep(.monitor-table .el-table td.el-table__cell),
:deep(.monitor-table .el-table tr) {
  background: transparent !important;
}

:deep(.monitor-table .el-table__expanded-cell) {
  background: rgba(8, 28, 70, 0.5) !important;
}

:deep(.monitor-toolbar .el-input__wrapper),
:deep(.monitor-toolbar .el-range-editor.el-input__wrapper) {
  background: rgba(8, 28, 70, 0.9);
  box-shadow: 0 0 0 1px rgba(83, 192, 255, 0.35) inset;
}

:deep(.monitor-toolbar .el-input__inner) {
  color: #d9f4ff;
}

:deep(.pagination-container .el-pagination) {
  --el-pagination-text-color: #cfeeff;
  --el-pagination-button-color: #cfeeff;
  --el-pagination-button-bg-color: rgba(11, 41, 94, 0.9);
  --el-pagination-hover-color: #7ee6ff;
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

  .top-controls {
    grid-template-columns: 1fr;
  }

  .monitor-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .placeholder-grid {
    grid-template-columns: 1fr 1fr;
  }

  .placeholder-card.wide {
    grid-column: 1 / -1;
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
    gap: 6px;
  }

  .chart-wrap {
    grid-template-columns: 1fr;
  }

  .vertical-title {
    writing-mode: horizontal-tb;
    font-size: 22px;
  }

  .workspace-headline {
    flex-direction: column;
    align-items: flex-start;
  }

  .placeholder-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .placeholder-grid {
    grid-template-columns: 1fr;
    grid-auto-rows: 120px;
  }

  .placeholder-card.wide {
    grid-column: auto;
  }

  .placeholder-card.tall {
    grid-row: span 1;
  }
}
</style>
