from flask import Flask, jsonify, request
from flask_cors import CORS
from parse_info import parse_info
from DataClass import Info, SystemStatus, SignalParams, TurntableSystem, GeodeticSystem, MotorDetail
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# 允许跨域，否则前端 Axios 会报错
CORS(app)
# 初始化 SocketIO，允许跨域
socketio = SocketIO(app, cors_allowed_origins="*")


# 对应前端的 GET 请求 (接收数据)
# @app.route('/api/get-item', methods=['GET'])
# def get_item():
#     return jsonify({
#         "status": "success",
#         "content": db_data["message"],
#         "id": 1
#     })

# 对应前端的 POST 请求 (发送数据)
@app.route('/api/send-item', methods=['POST'])
def send_item():
    # 获取前端发来的 JSON 数据
    data = request.json
    print(f"收到前端数据: {data}")
    # 解析数据
    info_obj = parse_info(data)

    # 2. 模拟解析后的“仪表盘数据” (对应你之前的分类需求)
    print('模拟解析中...')


    # 在实际项目中，这里会根据 info_obj 的值进行逻辑计算
    dashboard_json = {
    "code": 200,
    "msg": "success",
    "data": {
        "overview": {
        "signals": {
            "signal_1": 45.2,
            "signal_2": 12.8,
            "signal_3": 88.0
        },
        "subsystems": [
            { "id": 1, "name": "伺服系统", "status": 1 }, 
            { "id": 2, "name": "馈源系统", "status": 2 },
            { "id": 3, "name": "接收机", "status": 3 }
        ],
        "history_trend": {
            "times": ["08:00", "12:00", "16:00", "20:00", "00:00", "04:00", "08:00"],
            "values": [95, 92, 88, 90, 85, 80, 91]
        }
        },
        "health": {
        "current_score": 85,
        "history_score": {
            "times": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "values": [98, 95, 90, 85, 88, 92, 85]
        },
        "radar_data": {
            "dimensions": ["功耗", "温控", "响应", "稳定性", "信号质量"],
            "scores": [80, 75, 90, 85, 70]
        }
        },
        "alerts": [
        {
            "type": "电压异常",
            "severity": "高", 
            "location_id": 1,
            "position_tag": "top", 
            "desc": "方位轴电机1电压波动过大"
        },
        {
            "type": "通信延迟",
            "severity": "中",
            "location_id": 2,
            "position_tag": "middle",
            "desc": "中位控制器响应超时"
        }
        ]
    }
    }

    # 3. 【核心】实时推送！将解析好的数据发给所有连接的前端
    socketio.emit('update_dashboard', dashboard_json)
    print("3. 推送指令已下达")

    return jsonify({"status": "success", "msg": "数据已接收并推送"})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)