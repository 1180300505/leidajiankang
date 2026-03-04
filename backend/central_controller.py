# -*- coding: utf-8 -*-
"""
故障诊断控制器：基于 data.csv 阈值与 Demo 概率逻辑进行故障分析
"""
from DataClass import Info, SystemStatus, SignalParams, TurntableSystem, GeodeticSystem, MotorDetail
from database import DeviceDB
import json
import random
from pathlib import Path
from datetime import datetime

# 默认阈值（当 data.csv 不存在时使用，参考 data_simulator 默认值与工程经验）
DEFAULT_THRESHOLDS = {
    "turntable_azimuth": {"min": 116.5, "max": 124.0, "nominal": 120.0},
    "turntable_pitch": {"min": 10.0, "max": 25.0, "nominal": 16.0},
    "geodetic_azimuth": {"min": 106.0, "max": 114.0, "nominal": 110.0},
    "geodetic_pitch": {"min": 10.0, "max": 25.0, "nominal": 16.0},
    "motor_voltage": {"min": 217.0, "max": 223.0, "nominal": 220.0},
    "motor_current": {"min": 0.0, "max": 5.0, "nominal": 2.0},
    "motor_temp": {"min": 0.0, "max": 90.0, "nominal": 45.0},
}

# Demo 概率：一般故障 30%，严重故障 50%，无异常 20%
PROB_NO_FAULT = 0.2
PROB_GENERAL_FAULT = 0.3
# PROB_SEVERE_FAULT = 0.5  # 即 1 - 0.2 - 0.3

# 故障类型与异常参数说明
FAULT_DESCRIPTIONS = {
    "turntable_system": {
        "fault_device": "天线站A - 方位轴驱动子系统",
        "fault_component": "转台系方位轴",
        "fault_type": "方位角跟踪偏差",
        "params": [
            {"name": "转台系方位角偏差", "desc": "超出允许跟踪误差，可能影响指向精度"},
            {"name": "转台系俯仰角偏差", "desc": "超出允许跟踪误差，可能影响指向精度"},
        ],
    },
    "geodetic_system": {
        "fault_device": "天线站A - 方位轴驱动子系统",
        "fault_component": "大地系方位轴",
        "fault_type": "大地系方位角异常",
        "params": [
            {"name": "大地系方位角偏差", "desc": "与地理坐标不一致，影响地理指向"},
            {"name": "大地系俯仰角偏差", "desc": "与地理坐标不一致，影响地理指向"},
        ],
    },
    "motor_1": {
        "fault_device": "天线站A - 方位轴驱动子系统",
        "fault_component": "方位轴电机1 (编码器: AZ-MOTOR-01)",
        "fault_type": "电机绕组不平衡",
        "params": [
            {"name": "电机相电流不平衡度", "desc": "电流异常升高，可能存在过载或绕组故障"},
            {"name": "电机绕组温度", "desc": "超过安全温度，存在过热风险"},
            {"name": "电机电压", "desc": "电压偏离额定范围，可能影响转矩与寿命"},
        ],
    },
    "motor_2": {
        "fault_device": "天线站A - 方位轴驱动子系统",
        "fault_component": "方位轴电机2 (编码器: AZ-MOTOR-02)",
        "fault_type": "电机绕组不平衡",
        "params": [
            {"name": "电机相电流不平衡度", "desc": "电流异常升高，可能存在过载或绕组故障"},
            {"name": "电机绕组温度", "desc": "超过安全温度，存在过热风险"},
            {"name": "电机电压", "desc": "电压偏离额定范围，可能影响转矩与寿命"},
        ],
    },
}


def _safe_float(val, default=0.0):
    """安全转浮点数"""
    try:
        if val is None:
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def _load_thresholds_from_csv() -> dict:
    """从 data.csv 加载并统计阈值，若文件不存在返回默认值"""
    csv_path = Path(__file__).parent / "data.csv"
    if not csv_path.exists():
        return DEFAULT_THRESHOLDS.copy()

    try:
        import pandas as pd
        df = pd.read_csv(csv_path, encoding="gbk")
        if df.empty:
            return DEFAULT_THRESHOLDS.copy()
    except Exception:
        return DEFAULT_THRESHOLDS.copy()

    th = DEFAULT_THRESHOLDS.copy()

    # 转台系
    if "转台系引导方位角" in df.columns:
        col = pd.to_numeric(df["转台系引导方位角"], errors="coerce").dropna()
        if len(col) > 0:
            mu, std = col.mean(), col.std()
            th["turntable_azimuth"] = {
                "min": mu - 2 * max(std, 2),
                "max": mu + 2 * max(std, 2),
                "nominal": mu,
            }
    if "转台系引导俯仰角" in df.columns:
        col = pd.to_numeric(df["转台系引导俯仰角"], errors="coerce").dropna()
        if len(col) > 0:
            mu, std = col.mean(), col.std()
            th["turntable_pitch"] = {
                "min": mu - 2 * max(std, 2),
                "max": mu + 2 * max(std, 2),
                "nominal": mu,
            }

    # 大地系
    if "大地系引导方位角" in df.columns:
        col = pd.to_numeric(df["大地系引导方位角"], errors="coerce").dropna()
        if len(col) > 0:
            mu, std = col.mean(), col.std()
            th["geodetic_azimuth"] = {
                "min": mu - 2 * max(std, 2),
                "max": mu + 2 * max(std, 2),
                "nominal": mu,
            }
    if "大地系引导俯仰角" in df.columns:
        col = pd.to_numeric(df["大地系引导俯仰角"], errors="coerce").dropna()
        if len(col) > 0:
            mu, std = col.mean(), col.std()
            th["geodetic_pitch"] = {
                "min": mu - 2 * max(std, 2),
                "max": mu + 2 * max(std, 2),
                "nominal": mu,
            }

    # 电机
    for prefix, key in [("方位轴电机1", "motor_1"), ("方位轴电机2", "motor_2")]:
        if f"{prefix}电压" in df.columns:
            col = pd.to_numeric(df[f"{prefix}电压"], errors="coerce").dropna()
            if len(col) > 0:
                mu, std = col.mean(), col.std()
                th["motor_voltage"] = {
                    "min": mu - 2 * max(std, 3),
                    "max": mu + 2 * max(std, 3),
                    "nominal": mu,
                }
        if f"{prefix}电流" in df.columns:
            col = pd.to_numeric(df[f"{prefix}电流"], errors="coerce").dropna()
            if len(col) > 0:
                mu, std = col.mean(), col.std()
                th["motor_current"] = {
                    "min": 0,
                    "max": mu + 2 * max(std, 0.5),
                    "nominal": mu,
                }
        if f"{prefix}驱动器温度" in df.columns:
            col = pd.to_numeric(df[f"{prefix}驱动器温度"], errors="coerce").dropna()
            if len(col) > 0:
                mu, std = col.mean(), col.std()
                th["motor_temp"] = {
                    "min": 0,
                    "max": min(90, mu + 2 * max(std, 5)),
                    "nominal": mu,
                }
        break  # 两个电机共用同一套阈值

    return th


def _generate_event_id() -> str:
    """生成事件ID，如 FAULT-2025-0112-001"""
    now = datetime.now()
    suffix = random.randint(1, 999)
    return f"FAULT-{now.strftime('%Y-%m%d')}-{suffix:03d}".replace("-", "")


def _build_abnormal_params(info: Info, components: list, thresholds: dict) -> list:
    """根据异常部件和当前数据构建异常参数列表"""
    params = []
    ts = info.turntable_system
    gs = info.geodetic_system
    m1 = info.motor_diagnostics.get("motor_1")
    m2 = info.motor_diagnostics.get("motor_2")

    if "turntable_system" in components:
        az = _safe_float(getattr(ts, "guide_azimuth", 0) or getattr(ts, "current_azimuth", 0), 120)
        th = thresholds["turntable_azimuth"]
        params.append({
            "name": "转台系方位角偏差",
            "current": f"{az:.1f}°",
            "threshold": f"{th['min']:.1f}° ~ {th['max']:.1f}°",
            "desc": "超出允许跟踪误差，可能影响指向精度",
        })
        pt = _safe_float(getattr(ts, "guide_pitch", 0) or getattr(ts, "current_pitch", 0), 16)
        th_pt = thresholds["turntable_pitch"]
        params.append({
            "name": "转台系俯仰角偏差",
            "current": f"{pt:.1f}°",
            "threshold": f"{th_pt['min']:.1f}° ~ {th_pt['max']:.1f}°",
            "desc": "超出允许跟踪误差，可能影响指向精度",
        })

    if "geodetic_system" in components:
        az = _safe_float(getattr(gs, "guide_azimuth", 0) or getattr(gs, "current_azimuth", 0), 110)
        th = thresholds["geodetic_azimuth"]
        params.append({
            "name": "大地系方位角偏差",
            "current": f"{az:.1f}°",
            "threshold": f"{th['min']:.1f}° ~ {th['max']:.1f}°",
            "desc": "与地理坐标不一致，影响地理指向",
        })
        pt = _safe_float(getattr(gs, "guide_pitch", 0) or getattr(gs, "current_pitch_alt", 0), 16)
        th_pt = thresholds["geodetic_pitch"]
        params.append({
            "name": "大地系俯仰角偏差",
            "current": f"{pt:.1f}°",
            "threshold": f"{th_pt['min']:.1f}° ~ {th_pt['max']:.1f}°",
            "desc": "与地理坐标不一致，影响地理指向",
        })

    if "motor_1" in components and m1:
        v = _safe_float(m1.voltage, 220)
        th = thresholds["motor_voltage"]
        params.append({
            "name": "电机1电压",
            "current": f"{v:.1f}V",
            "threshold": f"{th['min']:.1f}~{th['max']:.1f}V",
            "desc": "电压偏离额定范围，可能影响转矩与寿命",
        })
        c = _safe_float(m1.current, 2)
        th_c = thresholds["motor_current"]
        params.append({
            "name": "电机1电流",
            "current": f"{c:.2f}A",
            "threshold": f"<{th_c['max']:.1f}A",
            "desc": "电流异常升高，可能存在过载或绕组故障",
        })
        t = _safe_float(m1.temp, 45)
        th_t = thresholds["motor_temp"]
        params.append({
            "name": "电机1绕组温度",
            "current": f"{t:.0f}℃",
            "threshold": f"<{th_t['max']:.0f}℃",
            "desc": "超过安全温度，存在过热风险",
        })

    if "motor_2" in components and m2:
        v = _safe_float(m2.voltage, 220)
        th = thresholds["motor_voltage"]
        params.append({
            "name": "电机2电压",
            "current": f"{v:.1f}V",
            "threshold": f"{th['min']:.1f}~{th['max']:.1f}V",
            "desc": "电压偏离额定范围，可能影响转矩与寿命",
        })
        c = _safe_float(m2.current, 2)
        th_c = thresholds["motor_current"]
        params.append({
            "name": "电机2电流",
            "current": f"{c:.2f}A",
            "threshold": f"<{th_c['max']:.1f}A",
            "desc": "电流异常升高，可能存在过载或绕组故障",
        })
        t = _safe_float(m2.temp, 45)
        th_t = thresholds["motor_temp"]
        params.append({
            "name": "电机2绕组温度",
            "current": f"{t:.0f}℃",
            "threshold": f"<{th_t['max']:.0f}℃",
            "desc": "超过安全温度，存在过热风险",
        })

    return params


def _pick_fault_components(severity: str) -> list:
    """按故障程度随机选取异常部件：一般1个，严重2~4个"""
    all_components = ["turntable_system", "geodetic_system", "motor_1", "motor_2"]
    if severity == "一般故障":
        return [random.choice(all_components)]
    n = random.randint(2, min(4, len(all_components)))
    return random.sample(all_components, n)


def analyze_data(info: Info, db: DeviceDB) -> dict:
    """
    进行数据故障分析（Demo 模式：概率驱动）
    - 无异常 20%，一般故障 30%，严重故障 50%
    - 返回完整故障报告结构，供前端展示与 DOCX 导出
    """
    thresholds = _load_thresholds_from_csv()
    r = random.random()

    if r < PROB_NO_FAULT:
        return {"故障程度": "无异常"}

    if r < PROB_NO_FAULT + PROB_GENERAL_FAULT:
        severity = "一般故障"
        severity_level = "中等"
    else:
        severity = "严重故障"
        severity_level = "高"

    components = _pick_fault_components(severity)
    abnormal_params = _build_abnormal_params(info, components, thresholds)

    # 取第一个部件作为主要故障部件
    main_comp = components[0]
    cfg = FAULT_DESCRIPTIONS.get(main_comp, {})
    fault_device = cfg.get("fault_device", "天线站A - 方位轴驱动子系统")
    fault_component = cfg.get("fault_component", main_comp)
    fault_type = cfg.get("fault_type", "未知故障")
    confidence = random.randint(85, 98)

    alter_json = {
        "故障程度": severity,
        "严重等级": severity_level,
        "event_id": _generate_event_id(),
        "故障时间": getattr(info, "timestamp", "") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "故障设备": fault_device,
        "故障部件": fault_component,
        "故障类型": f"{fault_type} (置信度: {confidence}%)",
        "异常参数": abnormal_params,
        "异常部件列表": components,
        "turntable_system": "转台系方位角异常" if "turntable_system" in components else None,
        "geodetic_system": "大地系方位角异常" if "geodetic_system" in components else None,
        "motor_1": "电机1电压异常" if "motor_1" in components else None,
        "motor_2": "电机2电压异常" if "motor_2" in components else None,
    }
    alter_json = {k: v for k, v in alter_json.items() if v is not None}

    error_id = db.insert_error(
        alter_json.get("故障时间", info.timestamp),
        severity,
        json.dumps(alter_json, ensure_ascii=False),
    )
    alter_json["error_id"] = error_id
    return alter_json
