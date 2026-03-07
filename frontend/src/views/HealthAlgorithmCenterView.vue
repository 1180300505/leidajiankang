<template>
  <section class="algo-screen">
    <header class="screen-header panel">
      <div>
        <p class="eyebrow">HEALTH ALGORITHM CENTER</p>
        <h1>健康算法中心</h1>
      </div>
      <div class="header-actions">
        <el-button class="action-btn ghost" @click="goBack">返回健康页</el-button>
        <el-button class="action-btn ghost" :loading="retrainLoading" @click="handleRetrain">重训模型</el-button>
      </div>
    </header>

    <div class="screen-grid">
      <article class="panel sidebar">
        <h2>算法目录</h2>

        <section v-for="group in algorithmGroups" :key="group.key" class="group-block">
          <h3>{{ group.title }}</h3>
          <div class="algo-list">
            <button
              v-for="item in group.algorithms"
              :key="item.key"
              type="button"
              class="algo-card"
              :class="{ active: selectedAlgorithm.key === item.key }"
              @click="selectAlgorithm(item)"
            >
              <strong>{{ item.name }}</strong>
              <span>{{ item.desc }}</span>
            </button>
          </div>
        </section>
      </article>

      <article class="panel workspace">
        <div class="workspace-head">
          <p class="group-name">{{ selectedAlgorithm.groupTitle }}</p>
          <h2>{{ selectedAlgorithm.name }}界面</h2>
          <p class="algo-desc">{{ selectedAlgorithm.desc }}</p>
        </div>

        <div class="workspace-grid">
          <section class="info-box">
            <h4>输入数据</h4>
            <ul>
              <li v-for="item in selectedAlgorithm.input" :key="item">{{ item }}</li>
            </ul>
          </section>

          <section class="info-box">
            <h4>输出结果</h4>
            <ul>
              <li v-for="item in selectedAlgorithm.output" :key="item">{{ item }}</li>
            </ul>
          </section>
        </div>

        <section class="flow-box">
          <h4>处理流程</h4>
          <ol>
            <li v-for="step in selectedAlgorithm.steps" :key="step">{{ step }}</li>
          </ol>
        </section>

        <section class="status-box">
          <div class="status-item">
            <span>当前算法</span>
            <strong>{{ selectedAlgorithm.name }}</strong>
          </div>
          <div class="status-item">
            <span>更新时间</span>
            <strong>{{ nowText }}</strong>
          </div>
          <div class="status-item">
            <span>状态</span>
            <strong class="online">待配置</strong>
          </div>
        </section>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { API_PREFIX } from '../config/backend'

const router = useRouter()
const retrainLoading = ref(false)
const nowText = new Date().toLocaleString('zh-CN')

const algorithmGroups = [
  {
    key: 'signal-processing',
    title: '数据信号处理算法',
    algorithms: [
      {
        key: 'emd',
        name: 'EMD分解',
        groupTitle: '数据信号处理算法',
        desc: '将非平稳信号分解为多层固有模态函数，便于提取时频特征。',
        input: ['振动/电流原始时序', '采样频率', '分解层数设置'],
        output: ['IMF分量序列', '残余趋势项', '每层能量占比'],
        steps: ['数据预处理', 'EMD迭代筛分', 'IMF有效性评估', '特征提取']
      },
      {
        key: 'vmd',
        name: 'VMD分解',
        groupTitle: '数据信号处理算法',
        desc: '通过变分约束将信号分解为带限模态，抑制模态混叠。',
        input: ['原始监测信号', '模态数K', '惩罚因子alpha'],
        output: ['各模态中心频率', '带限模态分量', '分解收敛信息'],
        steps: ['参数初始化', '拉格朗日优化', '频域更新迭代', '模态重构']
      },
      {
        key: 'dwt',
        name: '离散小波变换',
        groupTitle: '数据信号处理算法',
        desc: '对信号进行多尺度分解，区分瞬态冲击与低频趋势。',
        input: ['原始信号', '小波基类型', '分解尺度'],
        output: ['近似系数A', '细节系数D', '各尺度能量谱'],
        steps: ['选择小波基', '多尺度分解', '阈值去噪', '重构与特征统计']
      }
    ]
  },
  {
    key: 'diagnosis-assessment',
    title: '健康诊断评估算法（自适应监测）',
    algorithms: [
      {
        key: 'lstm-ae',
        name: 'LSTM-AE检测',
        groupTitle: '健康诊断评估算法（自适应监测）',
        desc: '基于时序重构误差识别异常工况，适合长期趋势监测。',
        input: ['时序特征窗口', '重构误差阈值', '训练模型权重'],
        output: ['重构误差曲线', '异常告警点', '健康评分'],
        steps: ['窗口切分', 'LSTM-AE推理', '误差统计', '阈值判别']
      },
      {
        key: 'som',
        name: 'SOM监测',
        groupTitle: '健康诊断评估算法（自适应监测）',
        desc: '通过自组织映射网络聚类状态分布，实现状态漂移监测。',
        input: ['多维健康特征', '拓扑网格大小', '学习率设置'],
        output: ['获胜神经元分布', '距离热力图', '异常区域标注'],
        steps: ['特征标准化', 'SOM映射训练/推理', '拓扑距离计算', '异常区判定']
      },
      {
        key: 'kmeans',
        name: 'Kmeans监测',
        groupTitle: '健康诊断评估算法（自适应监测）',
        desc: '对设备状态特征进行聚类，快速识别偏离正常簇的数据。',
        input: ['状态特征向量', '聚类中心数K', '迭代上限'],
        output: ['簇中心位置', '样本簇标签', '簇内距离评分'],
        steps: ['初始化簇中心', '样本归类', '中心更新', '异常簇告警']
      },
      {
        key: 'hmm',
        name: 'HMM监测',
        groupTitle: '健康诊断评估算法（自适应监测）',
        desc: '通过隐马尔可夫状态转移概率建模设备工况演化。',
        input: ['观测序列', '隐状态数', '初始转移矩阵'],
        output: ['最优状态序列', '状态转移概率', '异常转移告警'],
        steps: ['参数估计', '前向后向计算', 'Viterbi解码', '异常状态判别']
      },
      {
        key: 'cae',
        name: 'CAE监测',
        groupTitle: '健康诊断评估算法（自适应监测）',
        desc: '利用卷积自编码器提取局部时频结构，检测复杂故障模式。',
        input: ['二维时频图', '编码维度', '重构阈值'],
        output: ['编码特征向量', '重构误差热图', '异常等级'],
        steps: ['构建时频图', 'CAE编码重构', '误差聚合', '故障等级评估']
      },
      {
        key: 'sae',
        name: 'SAE监测',
        groupTitle: '健康诊断评估算法（自适应监测）',
        desc: '堆叠自编码器实现深层特征压缩与健康状态识别。',
        input: ['高维统计特征', '层数配置', '稀疏约束系数'],
        output: ['低维表示', '重构偏差', '类别概率'],
        steps: ['逐层预训练', '端到端微调', '特征映射', '健康分类']
      },
      {
        key: 'ann',
        name: 'ANN监测',
        groupTitle: '健康诊断评估算法（自适应监测）',
        desc: '基于多层感知机完成健康状态分类和风险评分。',
        input: ['人工特征向量', '网络结构参数', '训练权重'],
        output: ['分类结果', '置信度', '风险评分'],
        steps: ['特征归一化', '前向推理', '类别判别', '风险输出']
      },
      {
        key: 'cnn',
        name: 'CNN监测',
        groupTitle: '健康诊断评估算法（自适应监测）',
        desc: '卷积网络自动学习故障图谱特征，适合多类故障识别。',
        input: ['频谱图/时频图', '卷积层配置', '模型权重'],
        output: ['故障类别', '类别概率分布', '特征激活图'],
        steps: ['数据成图', '卷积特征提取', '分类头推理', '结果可视化']
      }
    ]
  }
]

const allAlgorithms = algorithmGroups.flatMap((group) => group.algorithms)
const selectedAlgorithmKey = ref(allAlgorithms[0].key)

const selectedAlgorithm = computed(
  () => allAlgorithms.find((item) => item.key === selectedAlgorithmKey.value) || allAlgorithms[0]
)

const selectAlgorithm = (item) => {
  selectedAlgorithmKey.value = item.key
}

const handleRetrain = async () => {
  retrainLoading.value = true
  try {
    await axios.post(`${API_PREFIX}/health/retrain`)
    ElMessage.success('模型重训任务已提交')
  } catch (error) {
    ElMessage.error('模型重训失败')
  } finally {
    retrainLoading.value = false
  }
}

const goBack = () => {
  router.push('/health')
}
</script>

<style scoped>
.algo-screen {
  min-height: calc(100vh - 20px);
  padding: 12px;
  color: #d7f3ff;
  border: 2px solid #18bfff;
  border-radius: 12px;
  background:
    radial-gradient(circle at 20% 0%, rgba(66, 166, 255, 0.18), transparent 40%),
    linear-gradient(180deg, #05153d 0%, #07255f 48%, #06194b 100%);
  box-shadow: inset 0 0 35px rgba(23, 125, 220, 0.22), 0 0 16px rgba(24, 190, 255, 0.22);
}

.panel {
  border: 1px solid rgba(87, 201, 255, 0.4);
  border-radius: 10px;
  background: linear-gradient(180deg, rgba(8, 37, 92, 0.88), rgba(6, 24, 67, 0.9));
  box-shadow: inset 0 0 16px rgba(34, 154, 255, 0.16);
}

.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px;
}

.eyebrow {
  margin: 0;
  color: #86dfff;
  font-size: 11px;
  letter-spacing: 1.5px;
}

h1 {
  margin: 4px 0 0;
  font-size: 30px;
  color: #f2fbff;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  border-radius: 8px;
}

.action-btn.ghost {
  background: #143768;
  color: #c6ecff;
  border-color: #3779b9;
}

.screen-grid {
  margin-top: 12px;
  display: grid;
  gap: 12px;
  grid-template-columns: 380px 1fr;
}

.sidebar,
.workspace {
  padding: 14px;
}

h2 {
  margin: 0;
  color: #99e6ff;
  font-size: 18px;
}

.group-block {
  margin-top: 12px;
}

h3 {
  margin: 0 0 8px;
  color: #8fdaf6;
  font-size: 14px;
  font-weight: 600;
}

.algo-list {
  display: grid;
  gap: 8px;
}

.algo-card {
  text-align: left;
  border: 1px solid rgba(99, 205, 255, 0.3);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(13, 51, 111, 0.85), rgba(11, 35, 85, 0.85));
  color: #d7f4ff;
  padding: 10px 12px;
  cursor: pointer;
  transition: 0.2s ease;
}

.algo-card strong {
  display: block;
  font-size: 14px;
}

.algo-card span {
  display: block;
  margin-top: 4px;
  color: #8fd7ef;
  font-size: 12px;
  line-height: 1.45;
}

.algo-card:hover {
  border-color: rgba(125, 226, 255, 0.6);
}

.algo-card.active {
  border-color: #7be7ff;
  box-shadow: 0 0 12px rgba(95, 223, 255, 0.25);
}

.workspace-head {
  border-bottom: 1px solid rgba(95, 197, 255, 0.26);
  padding-bottom: 10px;
}

.group-name {
  margin: 0;
  color: #8ed4f4;
  font-size: 12px;
}

.algo-desc {
  margin: 8px 0 0;
  color: #b8eaff;
  font-size: 13px;
  line-height: 1.55;
}

.workspace-grid {
  margin-top: 14px;
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.info-box,
.flow-box,
.status-box {
  border: 1px solid rgba(96, 205, 255, 0.24);
  border-radius: 8px;
  background: rgba(8, 26, 64, 0.58);
  padding: 12px;
}

h4 {
  margin: 0;
  color: #9fe8ff;
  font-size: 14px;
}

ul,
ol {
  margin: 8px 0 0;
  padding-left: 18px;
  color: #c7efff;
  font-size: 13px;
  line-height: 1.6;
}

.flow-box,
.status-box {
  margin-top: 12px;
}

.status-box {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.status-item {
  border: 1px solid rgba(117, 216, 255, 0.24);
  border-radius: 8px;
  background: rgba(7, 23, 57, 0.5);
  padding: 10px;
}

.status-item span {
  display: block;
  color: #8bcfe8;
  font-size: 12px;
}

.status-item strong {
  display: block;
  margin-top: 6px;
  color: #effbff;
  font-size: 14px;
}

.status-item strong.online {
  color: #56ffc0;
}

@media (max-width: 1024px) {
  .screen-grid {
    grid-template-columns: 1fr;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .status-box {
    grid-template-columns: 1fr;
  }

  .screen-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
