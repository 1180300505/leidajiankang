后端的主要功能包括数据接收、日志管理、健康评估以及故障记录等。以下是各个功能的详细介绍及其实现方法： 
1. 数据接收与处理： 
   - 功能描述：接收前端发送的数据，并进行解析。
   - 实现方法：使用`Flask`框架中的`@app.route('/api/send-item', methods=['POST'])`装饰器来定义一个API路由，接收POST请求。通过`request.json`获取前端发送的JSON数据，并使用`parse_info`模块中的`parse_info`函数解析这些数据。随后，使用`socketio.emit('update_dashboard', dashboard_json)`推送解析后的数据到前端，供前端页面更新。

2. 日志管理： 
    - 功能描述：提供分页查询日志的功能，并支持删除日志记录。
    - 实现方法：使用`@app.route('/api/logs', methods=['GET'])`和`@app.route("/api/logs/\<int:log_id\>", methods=["DELETE"])`来定义API路由。通过`request.args.get`获取分页查询的参数（如页码、每页条数等），并使用数据库模块查询相应的日志记录。删除日志的功能通过指定的日志ID进行，删除后返回成功信息。

1. 健康评估： 
    - 功能描述：根据接收到的数据评估设备的健康状态，并提供导出健康报告的功能。
    - 实现方法：使用`@app.route('/api/health/algorithm', methods=['GET', 'POST'])`来定义API路由，用于获取和切换健康评估算法（如kmeans和som）。通过train_from_db函数训练健康评估模型，使用_health_algorithm全局变量来保存当前使用的算法。健康评估报告的导出通过`@app.route('/api/export/docx', methods=['GET'])`实现，调用`export_full_docx`或`export_health_report_docx`导出Word格式的报告。

1. 故障记录管理： 
   - 功能描述：查询和导出故障记录，支持分页查询和按ID查询。
   - 实现方法：使用`@app.route('/api/errors', methods=['GET'])`和`@app.route('/api/errors/\<int:error_id\>', methods=['GET'])`来定义API路由，分别用于分页查询和按ID查询故障记录。查询结果通过JSON格式返回给前端。导出故障报告的功能通过`@app.route('/api/errors/0\<int:error_id\>/export/docx', methods=['GET'])`实现，调用`export_fault_report_docx`导出Word格式的报告。

2. 配置管理： 
    - 功能描述：管理允许的IP地址和健康评估的阈值。
    - 实现方法：使用`@app.route('/api/config/ip', methods=['GET', 'POST'])`来定义API路由，用于获取和更新允许的IP地址。使用`@app.route('/api/health/thresholds', methods=['GET', 'POST'])`来定义API路由，用于获取和更新健康评估的阈值。

1. 数据训练： 
    - 功能描述：支持使用数据库中的数据重新训练健康评估模型。
    - 实现方法：通过`@app.route('/api/health/retrain', methods=['POST'])`定义API路由，使用`train_from_db`函数重新训练健康评估模型。

后端的实现主要依赖于`Flask`框架来构建API，使用`SocketIO`来实现实时数据推送。数据库操作通过`DeviceDB`类来完成，健康评估模型的训练和评估则通过`HealthService`类来实现。

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
