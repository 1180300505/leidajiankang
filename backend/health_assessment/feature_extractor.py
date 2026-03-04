# -*- coding: utf-8 -*-
"""
从数据库记录 / Info 对象中提取各子系统的特征向量
"""

import numpy as np
from typing import Dict, List, Any

# 转台系：转台系 + 大地系角度与偏差
TURNTABLE_COLS = [
    "tt_guide_az", "tt_guide_pt", "tt_guide_tl",
    "tt_curr_az", "tt_curr_pt", "tt_curr_tl",
    "tt_dev_az", "tt_dev_pt", "tt_dev_tl",
    "geo_guide_az", "geo_guide_pt", "geo_curr_az",
    "geo_curr_pt_alt", "geo_dev_az", "geo_dev_pt",
]

# 电馈系：信号参数 + 电机1 + 电机2
ELECTROFEED_COLS = [
    "sig_agc_threshold", "sig_agc_voltage",
    "sig_azimuth_err_v", "sig_pitch_err_v",
    "m1_current", "m1_voltage", "m1_inertia", "m1_temp",
    "m2_current", "m2_voltage", "m2_inertia", "m2_temp",
]


def _to_float(val: Any, default: float = 0.0) -> float:
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def extract_turntable_features(rows: List[Dict]) -> np.ndarray:
    """从 DB 行列表提取转台系特征矩阵"""
    X = []
    for r in rows:
        vec = [_to_float(r.get(c)) for c in TURNTABLE_COLS]
        X.append(vec)
    return np.array(X) if X else np.zeros((0, len(TURNTABLE_COLS)))


def extract_electrofeed_features(rows: List[Dict]) -> np.ndarray:
    """从 DB 行列表提取电馈系特征矩阵"""
    X = []
    for r in rows:
        vec = [_to_float(r.get(c)) for c in ELECTROFEED_COLS]
        X.append(vec)
    return np.array(X) if X else np.zeros((0, len(ELECTROFEED_COLS)))


def extract_turntable_from_info(info) -> np.ndarray:
    """从 Info 对象提取转台系特征（单样本）"""
    tt = info.turntable_system
    geo = info.geodetic_system
    return np.array([[
        tt.guide_azimuth, tt.guide_pitch, tt.guide_tilt,
        tt.current_azimuth, tt.current_pitch, tt.current_tilt,
        tt.deviation_azimuth, tt.deviation_pitch, tt.deviation_tilt,
        geo.guide_azimuth, geo.guide_pitch, geo.current_azimuth,
        geo.current_pitch_alt, geo.deviation_azimuth, geo.deviation_pitch,
    ]])


def extract_electrofeed_from_info(info) -> np.ndarray:
    """从 Info 对象提取电馈系特征（单样本）"""
    sig = info.signal_params
    m1 = info.motor_diagnostics.get("motor_1")
    m2 = info.motor_diagnostics.get("motor_2")
    m1 = m1 or type("M", (), {"current": 0, "voltage": 0, "inertia": 0, "temp": 0})()
    m2 = m2 or type("M", (), {"current": 0, "voltage": 0, "inertia": 0, "temp": 0})()
    return np.array([[
        sig.agc_threshold, sig.agc_voltage,
        sig.azimuth_error_voltage, sig.pitch_error_voltage,
        _to_float(getattr(m1, "current", 0)), _to_float(getattr(m1, "voltage", 0)),
        _to_float(getattr(m1, "inertia", 0)), _to_float(getattr(m1, "temp", 0)),
        _to_float(getattr(m2, "current", 0)), _to_float(getattr(m2, "voltage", 0)),
        _to_float(getattr(m2, "inertia", 0)), _to_float(getattr(m2, "temp", 0)),
    ]])


def extract_turntable_from_dict(data: dict) -> np.ndarray:
    """从原始 JSON 字典提取转台系特征（单样本）"""
    tt = data.get("tracking_data", {}).get("turntable_system", {})
    geo = data.get("tracking_data", {}).get("geodetic_system", {})
    return np.array([[
        _to_float(tt.get("guide_azimuth")), _to_float(tt.get("guide_pitch")), _to_float(tt.get("guide_tilt")),
        _to_float(tt.get("current_azimuth")), _to_float(tt.get("current_pitch")), _to_float(tt.get("current_tilt")),
        _to_float(tt.get("deviation_azimuth")), _to_float(tt.get("deviation_pitch")), _to_float(tt.get("deviation_tilt")),
        _to_float(geo.get("guide_azimuth")), _to_float(geo.get("guide_pitch")), _to_float(geo.get("current_azimuth")),
        _to_float(geo.get("current_pitch_alt")), _to_float(geo.get("deviation_azimuth")), _to_float(geo.get("deviation_pitch")),
    ]])


def extract_electrofeed_from_dict(data: dict) -> np.ndarray:
    """从原始 JSON 字典提取电馈系特征（单样本）"""
    sig = data.get("signal_params", {})
    m1 = data.get("motor_diagnostics", {}).get("motor_1", {})
    m2 = data.get("motor_diagnostics", {}).get("motor_2", {})
    return np.array([[
        _to_float(sig.get("agc_threshold")), _to_float(sig.get("agc_voltage")),
        _to_float(sig.get("azimuth_error_voltage")), _to_float(sig.get("pitch_error_voltage")),
        _to_float(m1.get("current")), _to_float(m1.get("voltage")), _to_float(m1.get("inertia")), _to_float(m1.get("temp")),
        _to_float(m2.get("current")), _to_float(m2.get("voltage")), _to_float(m2.get("inertia")), _to_float(m2.get("temp")),
    ]])


def db_row_to_dict(row: Dict) -> dict:
    """将 DB 行转为与 JSON 结构一致的字典，便于统一提取"""
    return {
        "tracking_data": {
            "turntable_system": {
                "guide_azimuth": row.get("tt_guide_az"),
                "guide_pitch": row.get("tt_guide_pt"),
                "guide_tilt": row.get("tt_guide_tl"),
                "current_azimuth": row.get("tt_curr_az"),
                "current_pitch": row.get("tt_curr_pt"),
                "current_tilt": row.get("tt_curr_tl"),
                "deviation_azimuth": row.get("tt_dev_az"),
                "deviation_pitch": row.get("tt_dev_pt"),
                "deviation_tilt": row.get("tt_dev_tl"),
            },
            "geodetic_system": {
                "guide_azimuth": row.get("geo_guide_az"),
                "guide_pitch": row.get("geo_guide_pt"),
                "current_azimuth": row.get("geo_curr_az"),
                "current_pitch_alt": row.get("geo_curr_pt_alt"),
                "deviation_azimuth": row.get("geo_dev_az"),
                "deviation_pitch": row.get("geo_dev_pt"),
            },
        },
        "signal_params": {
            "agc_threshold": row.get("sig_agc_threshold"),
            "agc_voltage": row.get("sig_agc_voltage"),
            "azimuth_error_voltage": row.get("sig_azimuth_err_v"),
            "pitch_error_voltage": row.get("sig_pitch_err_v"),
        },
        "motor_diagnostics": {
            "motor_1": {
                "current": row.get("m1_current"),
                "voltage": row.get("m1_voltage"),
                "inertia": row.get("m1_inertia"),
                "temp": row.get("m1_temp"),
            },
            "motor_2": {
                "current": row.get("m2_current"),
                "voltage": row.get("m2_voltage"),
                "inertia": row.get("m2_inertia"),
                "temp": row.get("m2_temp"),
            },
        },
    }
