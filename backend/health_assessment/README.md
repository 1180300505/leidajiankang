# 健康评估模块

基于 KMeans 与 SOM（自组织映射神经网络）的健康度监测，支持整体与子系统评估，算法及数据处理器可互相替换。

## 目录

- [健康状态与子系统](#健康状态与子系统)
- [接口设计](#接口设计)
- [API 使用](#api-使用)
- [代码使用](#代码使用)
- [依赖安装](#依赖安装)

---

## 打分制与阈值分级

本模块采用 **打分制** + **阈值分级**：
- **打分**：算法输出 0–100 分数（越高越健康）
- **分级**：按可配置阈值将分数映射为 正常 / 轻度异常 / 重度异常

| 分数范围           | 等级     |
|--------------------|----------|
| ≥ threshold_normal | 正常     |
| ≥ threshold_mild   | 轻度异常 |
| < threshold_mild   | 重度异常 |

默认：`threshold_normal=90`，`threshold_mild=70`。

## 健康状态与子系统

### 健康状态

| 状态     | 说明                   |
|----------|------------------------|
| 正常     | 分数 ≥ 正常阈值        |
| 轻度异常 | 分数 ≥ 轻度阈值        |
| 重度异常 | 分数 < 轻度阈值        |

### 子系统划分

| 子系统 | 说明 | 包含特征 |
|--------|------|----------|
| **转台系** | 转台坐标系 + 大地坐标系 | 引导/当前方位角、俯仰角、倾斜角及偏差 |
| **电馈系** | 信号与电机系统 | AGC 参数、方位/俯仰误差电压、电机电流/电压/惯量/温度 |

---

## 接口设计

### 数据处理接口 (DataProcessorInterface)

不同健康评估算法可搭配不同的数据预处理方式：

| 处理器                  | 说明               | 适用算法 |
|-------------------------|--------------------|----------|
| StandardScalerProcessor | 零均值、单位方差   | KMeans   |
| MinMaxProcessor         | [0,1] 归一化       | SOM      |

### 健康评估接口 (HealthAssessorInterface)

| 算法            | 说明                                      |
|-----------------|-------------------------------------------|
| KMeansAssessor  | 以到最近聚类中心的距离换算 0–100 分数     |
| SOMAssessor     | 以到 BMU 的量化误差换算 0–100 分数        |

---

## API 使用

### 获取当前算法

```http
GET /api/health/algorithm
```

**响应示例：**
```json
{
  "algorithm": "kmeans",
  "options": ["kmeans", "som"]
}
```

### 切换算法

```http
POST /api/health/algorithm
Content-Type: application/json

{
  "algorithm": "som"
}
```

**说明：** 切换后，下次接收数据时会使用新算法重新训练。

### 强制重新训练

```http
POST /api/health/retrain
```

使用当前数据库中的历史数据重新训练健康评估模型。

### 分级阈值配置

```http
GET /api/health/thresholds
```

**响应示例：**
```json
{
  "threshold_normal": 90,
  "threshold_mild": 70,
  "desc": "分数>=threshold_normal 为正常，>=threshold_mild 为轻度异常，否则为重度异常"
}
```

```http
POST /api/health/thresholds
Content-Type: application/json

{
  "threshold_normal": 85,
  "threshold_mild": 60
}
```

---

## 代码使用

### 从数据库训练并评估

```python
from health_assessment import train_from_db, HealthService
from database import DeviceDB

db = DeviceDB("device_monitor.db")

# 使用 KMeans 算法
svc = train_from_db(db, algorithm="kmeans", max_samples=500)

# 使用 SOM 算法
svc = train_from_db(db, algorithm="som", max_samples=500)

# 从 JSON 字典评估单条数据
result = svc.assess_from_dict(data)
# result = {
#     "overall": "正常",
#     "turntable": "正常",
#     "electrofeed": "轻度异常",
#     "overall_code": 1,
#     "turntable_code": 0,
#     "electrofeed_code": 1,
#     "overall_score": 88.5,      # 0-100 分数
#     "turntable_score": 92.1,
#     "electrofeed_score": 75.3
# }
```

### 自定义创建服务

```python
from health_assessment import HealthService

svc = HealthService(
    algorithm="kmeans",
    min_train_samples=10,
    threshold_normal=90,
    threshold_mild=70
)

# 使用 DB 行列表训练
rows = [...]  # database.query_paged 返回的字典列表
svc.fit(rows)

# 评估
result = svc.assess_from_dict(data)
```

### 健康状态码与标签

```python
from health_assessment import STATUS_LABELS

# STATUS_LABELS = {0: "正常", 1: "轻度异常", 2: "重度异常"}
```

---

## 依赖安装

```bash
pip install minisom numpy
```

或使用项目 requirements.txt：

```bash
pip install -r requirements.txt
```

---

## 模块结构

```
health_assessment/
├── __init__.py          # 模块入口
├── interfaces.py        # DataProcessorInterface, HealthAssessorInterface
├── data_processors.py   # StandardScalerProcessor, MinMaxProcessor
├── assessors.py         # KMeansAssessor, SOMAssessor
├── feature_extractor.py # 特征提取（转台系、电馈系）
├── health_service.py    # HealthService, train_from_db
└── README.md            # 本文档
```
