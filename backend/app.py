from flask import Flask, jsonify, request, send_file, make_response
import io
import json
from datetime import datetime, timedelta
from flask_cors import CORS
from parse_info import parse_info
from flask_socketio import SocketIO, emit
from database import get_or_create_db, DeviceDB
from typing import Optional
from docx_exporter import export_full_docx, export_health_report_docx, export_fault_report_docx
from central_controller import analyze_data
from health_assessment import train_from_db, HealthService

# 1. 初始化数据库
db_name = "device_monitor.db"
db = DeviceDB(db_name)

# 健康评估服务（懒加载，首次使用时从 DB 训练）
_health_service: Optional[HealthService] = None
_health_algorithm = "kmeans"
_health_threshold_normal = 90   # 分数>=此值为正常
_health_threshold_mild = 70     # 分数>=此值为轻度异常，否则重度异常


def _to_num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _norm_score(value, center=0.0, scale=1.0):
    ratio = abs(_to_num(value) - center) / max(scale, 1e-6)
    return max(0.0, min(100.0, 100.0 - ratio * 100.0))


def _build_subsystem_radar(data: dict, tt_score: float, ef_score: float):
    tracking = data.get("tracking_data", {})
    tt = tracking.get("turntable_system", {})
    geo = tracking.get("geodetic_system", {})
    sig = data.get("signal_params", {})
    motors = data.get("motor_diagnostics", {})
    m1 = motors.get("motor_1", {})
    m2 = motors.get("motor_2", {})

    turntable_values = [
        _norm_score(tt.get("deviation_azimuth"), 0.0, 5.0),
        _norm_score(tt.get("deviation_pitch"), 0.0, 3.0),
        _norm_score(tt.get("deviation_tilt"), 0.0, 3.0),
        _norm_score(geo.get("deviation_azimuth"), 0.0, 5.0),
        _norm_score(geo.get("deviation_pitch"), 0.0, 3.0),
    ]
    electrofeed_values = [
        _norm_score(sig.get("agc_voltage"), 2.5, 1.5),
        _norm_score(sig.get("azimuth_error_voltage"), 0.0, 1.0),
        _norm_score(sig.get("pitch_error_voltage"), 0.0, 1.0),
        _norm_score(m1.get("temp"), 55.0, 35.0),
        _norm_score(m2.get("temp"), 55.0, 35.0),
    ]

    turntable_values = [round((v * 0.45 + tt_score * 0.55), 1) for v in turntable_values]
    electrofeed_values = [round((v * 0.45 + ef_score * 0.55), 1) for v in electrofeed_values]

    return {
        "turntable": {
            "labels": ["方位偏差", "俯仰偏差", "倾斜偏差", "大地偏差", "稳定性"],
            "values": turntable_values,
        },
        "electrofeed": {
            "labels": ["AGC电压", "方位误差电压", "俯仰误差电压", "电机1温度", "电机2温度"],
            "values": electrofeed_values,
        },
    }


def _get_health_service() -> HealthService:
    global _health_service, _health_algorithm, _health_threshold_normal, _health_threshold_mild
    if _health_service is None:
        _health_service = train_from_db(
            db, algorithm=_health_algorithm,
            threshold_normal=_health_threshold_normal,
            threshold_mild=_health_threshold_mild
        )
    else:
        # 同步阈值（可能已被 API 修改）
        _health_service.threshold_normal = _health_threshold_normal
        _health_service.threshold_mild = _health_threshold_mild
    return _health_service
app = Flask(__name__)
# 关键点：expose_headers 必须包含内容处置头
CORS(app, expose_headers=["Content-Disposition"])
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

    # 健康度评估（KMeans/SOM 算法，整体 + 转台系 + 电馈系）
    try:
        svc = _get_health_service()
        health_result = svc.assess_from_dict(data)
    except Exception as e:
        print(f"健康评估异常: {e}")
        health_result = {"overall": "正常", "turntable": "正常", "electrofeed": "正常",
                         "overall_code": 0, "turntable_code": 0, "electrofeed_code": 0,
                         "overall_score": 95, "turntable_score": 95, "electrofeed_score": 95}

    # 打分制：直接使用算法输出的分数
    overall_score = round(health_result.get("overall_score", 95))
    tt_score = round(health_result.get("turntable_score", 95))
    ef_score = round(health_result.get("electrofeed_score", 95))
    subsystem_radar = _build_subsystem_radar(data, tt_score, ef_score)

    dashboard_json = {
        "code": 200,
        "msg": "success",
        "data": {
            "overview": {
                "system_mode": "指向",
                "signals": {"signal_1": 45.2, "signal_2": 12.8, "signal_3": 88.0},
                "subsystems": [
                    {"id": 1, "name": "转台系", "status": 1 if health_result["turntable_code"] == 0 else (2 if health_result["turntable_code"] == 1 else 3), "health_status": health_result["turntable"]},
                    {"id": 2, "name": "电馈系", "status": 1 if health_result["electrofeed_code"] == 0 else (2 if health_result["electrofeed_code"] == 1 else 3), "health_status": health_result["electrofeed"]},
                ],
                "history_trend": {
                    "times": ["08:00", "12:00", "16:00", "20:00", "00:00", "04:00", "08:00"],
                    "values": [95, 92, 88, 90, 85, 80, 91]
                }
            },
            "health": {
                "current_score": overall_score,
                "overall_status": health_result["overall"],
                "subsystems": {
                    "turntable": {"status": health_result["turntable"], "score": tt_score},
                    "electrofeed": {"status": health_result["electrofeed"], "score": ef_score},
                },
                "radar_data": {
                    "dimensions": ["转台系", "电馈系"],
                    "scores": [tt_score, ef_score]
                },
                "subsystem_radar": subsystem_radar
            }
        }
    }

    # 3. 健康分数落库（按算法隔离，不同算法不混合统计）
    try:
        db.insert_health_record({
            "timestamp": data.get("timestamp"),
            "algorithm": _health_algorithm,
            "threshold_normal": _health_threshold_normal,
            "threshold_mild": _health_threshold_mild,
            "overall_score": health_result.get("overall_score", 95),
            "overall_grade": health_result.get("overall", "正常"),
            "turntable_score": health_result.get("turntable_score", 95),
            "turntable_grade": health_result.get("turntable", "正常"),
            "electrofeed_score": health_result.get("electrofeed_score", 95),
            "electrofeed_grade": health_result.get("electrofeed", "正常"),
        })
    except Exception as e:
        print(f"健康记录落库异常: {e}")

    # 4. 实时推送
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

# 输出健康评估报告（Word）
@app.route('/api/export/docx', methods=['GET'])
def export_docx():
    start = request.args.get('start')
    end = request.args.get('end')
    algorithm = request.args.get('algorithm')
    
    if not start or not end:
        return jsonify({"error": "缺少 start 或 end 参数"}), 400
    if not algorithm or algorithm not in ('kmeans', 'som'):
        return jsonify({"error": "algorithm 必填，且须为 kmeans 或 som"}), 400
        
    health_records = db.query_health_records(start, end, algorithm)
    if not health_records:
        return jsonify({"error": f"所选时间范围内无 {algorithm} 算法的健康记录"}), 404

    system_logs = db.query_range(start, end)
    prev_records = []
    try:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                t_start = datetime.strptime(start, fmt)
                t_end = datetime.strptime(end, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError("无法解析时间格式")
        duration = t_end - t_start
        prev_end = t_start
        prev_start = t_start - duration
        prev_start_s = prev_start.strftime("%Y-%m-%d %H:%M:%S") if " " in start else prev_start.strftime("%Y-%m-%d")
        prev_end_s = prev_end.strftime("%Y-%m-%d %H:%M:%S") if " " in start else prev_end.strftime("%Y-%m-%d")
        prev_records = db.query_health_records(prev_start_s, prev_end_s, algorithm)
    except Exception:
        pass
    buf = io.BytesIO()
    export_health_report_docx(health_records, system_logs, start, end, algorithm, prev_records, filename=buf)
    buf.seek(0)

    # 1. 生成文件名
    filename = f"HealthReport_{start[:10]}_{algorithm}.docx"

    # 2. 构建响应
    response = make_response(send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ))

    # 3. 针对 Firefox 强制补齐 Headers
    # 显式告诉浏览器这是一个附件，并提供文件名
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    # 再次确保跨域环境下前端可见
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    
    return response


# --- 故障记录 API ---
@app.route('/api/errors', methods=['GET'])
def get_errors():
    """分页查询故障记录"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    sort_order = request.args.get('sort', 'DESC')
    data, total = db.query_errors(page, page_size, sort_order)
    # 解析 error_message 为 JSON，便于前端使用
    for item in data:
        try:
            item['fault_report'] = json.loads(item.get('error_message') or '{}')
        except Exception:
            item['fault_report'] = {}
    return jsonify({
        "items": data,
        "total": total,
        "page": page,
        "page_size": page_size
    })


@app.route('/api/errors/<int:error_id>', methods=['GET'])
def get_error_detail(error_id):
    """按 ID 查询单条故障详情"""
    record = db.query_error_by_id(error_id)
    if not record:
        return jsonify({"error": "未找到该故障记录"}), 404
    try:
        record['fault_report'] = json.loads(record.get('error_message') or '{}')
    except Exception:
        record['fault_report'] = {}
    return jsonify(record)


@app.route('/api/errors/<int:error_id>/export/docx', methods=['GET'])
def export_fault_docx(error_id):
    """导出单条故障的 DOCX 报告"""
    record = db.query_error_by_id(error_id)
    if not record:
        return jsonify({"error": "未找到该故障记录"}), 404
    try:
        fault_report = json.loads(record.get('error_message') or '{}')
    except Exception:
        fault_report = {}
    if not fault_report or fault_report.get('故障程度') == '无异常':
        return jsonify({"error": "该记录无有效故障报告"}), 400
    buf = io.BytesIO()
    export_fault_report_docx(fault_report, filename=buf)
    buf.seek(0)
    event_id = fault_report.get('event_id', f'FAULT-{error_id}')
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in event_id)
    filename = f"FaultReport_{safe_name}.docx"
    response = make_response(send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ))
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response


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

# 健康评估算法切换
@app.route('/api/health/algorithm', methods=['GET'])
def get_health_algorithm():
    return jsonify({"algorithm": _health_algorithm, "options": ["kmeans", "som"]})

@app.route('/api/health/algorithm', methods=['POST'])
def set_health_algorithm():
    global _health_service, _health_algorithm
    algo = request.json.get('algorithm') if request.json else None
    if algo not in ('kmeans', 'som'):
        return jsonify({"error": "algorithm 须为 kmeans 或 som"}), 400
    _health_algorithm = algo
    _health_service = None  # 下次使用时重新训练
    return jsonify({"message": f"已切换为 {algo}", "algorithm": _health_algorithm})

@app.route('/api/health/retrain', methods=['POST'])
def retrain_health():
    """强制用当前数据库数据重新训练健康评估模型"""
    global _health_service, _health_algorithm, _health_threshold_normal, _health_threshold_mild
    _health_service = train_from_db(
        db, algorithm=_health_algorithm,
        threshold_normal=_health_threshold_normal,
        threshold_mild=_health_threshold_mild
    )
    return jsonify({"message": "健康评估模型已重新训练", "algorithm": _health_algorithm})

# 分级阈值配置
@app.route('/api/health/thresholds', methods=['GET'])
def get_health_thresholds():
    return jsonify({
        "threshold_normal": _health_threshold_normal,
        "threshold_mild": _health_threshold_mild,
        "desc": "分数>=threshold_normal 为正常，>=threshold_mild 为轻度异常，否则为重度异常"
    })

@app.route('/api/health/thresholds', methods=['POST'])
def set_health_thresholds():
    global _health_threshold_normal, _health_threshold_mild, _health_service
    data = request.json or {}
    normal = data.get("threshold_normal")
    mild = data.get("threshold_mild")
    if normal is not None:
        try:
            _health_threshold_normal = float(normal)
        except (TypeError, ValueError):
            return jsonify({"error": "threshold_normal 须为数字"}), 400
    if mild is not None:
        try:
            _health_threshold_mild = float(mild)
        except (TypeError, ValueError):
            return jsonify({"error": "threshold_mild 须为数字"}), 400
    if _health_threshold_normal < _health_threshold_mild:
        return jsonify({"error": "threshold_normal 应大于 threshold_mild"}), 400
    if _health_service:
        _health_service.threshold_normal = _health_threshold_normal
        _health_service.threshold_mild = _health_threshold_mild
    return jsonify({
        "message": "阈值已更新",
        "threshold_normal": _health_threshold_normal,
        "threshold_mild": _health_threshold_mild
    })

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
