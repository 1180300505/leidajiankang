from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from parse_info import parse_info
from flask_socketio import SocketIO, emit
from database import get_or_create_db, DeviceDB
from typing import Optional
from docx_exporter import export_full_docx
from central_controller import analyze_data

# 1. 初始化数据库
db_name = "device_monitor.db"
db = DeviceDB(db_name)
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
    # 获取发送方的实际 IP
    sender_ip = request.remote_addr
    if sender_ip != db.source_ip:
        msg = "IP 地址不正确，当前IP:" + sender_ip + "，所需IP:" + db.source_ip
        # 不再传输数据
        return jsonify({"status": "error", "msg": msg})

    # 插入数据到数据库
    db.insert_data(data)

    # 解析数据
    info_obj = parse_info(data)

    # 2. 模拟解析后的“仪表盘数据” (对应你之前的分类需求)
    print('模拟解析中...')
    alter_json = analyze_data(info_obj, db)
    if alter_json["故障程度"] != "无异常":
        # 推送专门的报警事件
        socketio.emit('fault_alarm', alter_json)
        print(f"检测到异常: {alter_json['故障程度']}，已实时推送报警！")

    # 在实际项目中，这里会根据 info_obj 的值进行逻辑计算
    dashboard_json = {
    "code": 200,
    "msg": "success",
    "data": {
        "overview": {
        "system_mode": "指向",
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
        "radar_data": {
            "dimensions": ["功耗", "温控", "响应", "稳定性", "信号质量"],
            "scores": [80, 75, 90, 85, 70]
        }
        },
    }
    }

    # 3. 【核心】实时推送！将解析好的数据发给所有连接的前端
    socketio.emit('update_dashboard', dashboard_json)
    print("3. 推送指令已下达")

    return jsonify({"status": "success", "msg": "数据已接收并推送"})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    sort_order = request.args.get('sort', 'DESC') # 接收排序参数，默认降序
    
    data, total = db.query_paged(page, page_size, sort_order)
    
    return jsonify({
        "items": data,
        "total": total,
        "page": page,
        "page_size": page_size
    })

# --- 3. 删除操作 (Flask 版本) ---
@app.route("/api/logs/<int:log_id>", methods=["DELETE"])
def delete_log(log_id):
    """
    根据 ID 删除单条数据
    """
    # 执行删除
    db.cursor.execute("DELETE FROM system_logs WHERE id = ?", (log_id,))
    row_count = db.cursor.rowcount # 获取受影响的行数
    db.conn.commit()
    
    print(f"DEBUG: 删除了 {row_count} 条数据, ID: {log_id}")
    
    if row_count == 0:
        return jsonify({"message": "未找到该 ID 的数据"}), 404
        
    return jsonify({"message": f"ID {log_id} 已成功删除", "status": "success"})

# 输出日志文件
@app.route('/api/export/docx', methods=['GET'])
def export_docx():
    start = request.args.get('start')
    end = request.args.get('end')
    
    if not start or not end:
        return "Missing parameters", 400
        
    # 从数据库获取该时间段所有数据
    data = db.query_range(start, end)
    
    if not data:
        return "No data found in this range", 404

    # 生成文件
    path = export_full_docx(data, start, end)
    
    # 返回文件流
    return send_file(
        path,
        as_attachment=True,
        download_name=f"Report_{start[:10]}.docx",
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

# 获取当前允许的 IP
@app.route('/api/config/ip', methods=['GET'])
def get_config_ip():
    return jsonify({"current_ip": db.source_ip})

# 设置新的允许 IP
@app.route('/api/config/ip', methods=['POST'])
def update_config_ip():
    new_ip = request.json.get('new_ip')
    if not new_ip:
        return "Invalid IP", 400
    db.set_active_ip(new_ip)
    return jsonify({"message": "IP updated successfully"})

@app.route('/api/health/daily-report', methods=['GET'])
def daily_report():
    data = db.get_weekly_health_report()
    return jsonify({
        "status": "success",
        "data": data,
        "summary": {
            "today_score": data[-1]['score'],  # 今天的实时分数
            "average_score": sum(d['score'] for d in data) // 7
        }
    })

if __name__ == '__main__':
    # 必须使用 socketio.run
    # host='0.0.0.0' 确保局域网手机能访问
    # allow_unsafe_werkzeug=True 是为了在开发环境下强制运行
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)