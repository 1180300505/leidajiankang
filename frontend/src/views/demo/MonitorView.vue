<template>
  <div class="container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <div class="title">设备运行日志监控 (SQLite + Flask)</div>
          <div class="actions">
            <el-button @click="fetchData(currentPage)">刷新列表</el-button>
          </div>
        </div>
      </template>

      <div class="export-bar">
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="导出开始时间"
          end-placeholder="导出结束时间"
          value-format="YYYY-MM-DD HH:mm:ss"
          :default-time="[new Date(2000, 1, 1, 0, 0, 0), new Date(2000, 1, 1, 23, 59, 59)]"
        />
        <el-button 
          type="warning" 
          :icon="Download" 
          @click="handleExport" 
          style="margin-left: 10px;">
          导出详细 Word 报告
        </el-button>
      </div>

      <el-table 
        :data="tableData" 
        stripe 
        border 
        v-loading="loading"
        @sort-change="handleSortChange"
        style="width: 100%">
        
        <el-table-column prop="id" label="ID" width="70" align="center" />
        
        <el-table-column 
          prop="timestamp" 
          label="记录时间" 
          width="180" 
          sortable="custom" 
        />
        
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
            <el-popconfirm 
              title="确定要删除这条记录吗？"
              @confirm="handleDelete(scope.row.id)">
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { API_PREFIX } from '../../config/backend'

// 状态定义
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const currentSort = ref('DESC')
const dateRange = ref([]) // 用于 Word 导出的日期范围

// 基础 API 地址
const API_BASE = API_PREFIX

// 获取数据
const fetchData = async (page) => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/logs`, {
      params: {
        page: page,
        page_size: pageSize.value,
        sort: currentSort.value
      }
    })
    tableData.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

// 核心：处理导出 Word
const handleExport = () => {
  if (!dateRange.value || dateRange.value.length < 2) {
    ElMessage.warning('请先选择需要导出的日期范围')
    return
  }
  const start = dateRange.value[0]
  const end = dateRange.value[1]
  
  // 构建导出链接
  const exportUrl = `${API_BASE}/export/docx?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`
  
  // 通过新窗口下载文件
  window.open(exportUrl, '_blank')
  ElMessage.success('正在准备报表，请稍候...')
}

// 排序处理
const handleSortChange = ({ prop, order }) => {
  if (prop === 'timestamp') {
    currentSort.value = order === 'ascending' ? 'ASC' : 'DESC'
    currentPage.value = 1
    fetchData(1)
  }
}

// 分页处理
const handlePageChange = (val) => {
  currentPage.value = val
  fetchData(val)
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchData(1)
}

// 删除数据
const handleDelete = async (id) => {
  try {
    await axios.delete(`${API_BASE}/logs/${id}`)
    ElMessage.success('记录已删除')
    if (tableData.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    fetchData(currentPage.value)
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchData(1)
})
</script>

<style scoped>
.container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 18px;
  font-weight: bold;
}
.export-bar {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 4px;
  border: 1px dashed #dcdfe6;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.box-card {
  max-width: 1300px;
  margin: 0 auto;
}
</style>
