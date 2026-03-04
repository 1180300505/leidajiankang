#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据模拟发送程序 - 独立运行
从 data.csv 中随机抽取一行，对数字施加 ±5% 波动后，以可调频率向后端 POST 发送 JSON 数据。
"""

import argparse
import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


# 默认配置
DEFAULT_CSV_PATH = Path(__file__).parent / "data.csv"
DEFAULT_API_URL = "http://127.0.0.1:5000/api/send-item"
DEFAULT_INTERVAL = 0.8  # 秒，小于 1 秒
DEFAULT_VARIANCE = 0.05  # ±5%


def _safe_float(value, default: float = 0.0):
    """安全转为浮点数，NaN/invalid 返回默认值"""
    try:
        num = float(value)
        return default if pd.isna(num) else num
    except (TypeError, ValueError):
        return default


def apply_variance(value, variance: float = DEFAULT_VARIANCE, default: float = 0.0):
    """对数字施加 ±variance 的随机波动，NaN/invalid 返回默认值"""
    num = _safe_float(value, default)
    factor = 1 + random.uniform(-variance, variance)
    return round(num * factor, 6)


def _safe_str(value, default: str = ""):
    """安全转为字符串，NaN/invalid 返回默认值"""
    try:
        if value is None or pd.isna(value):
            return default
    except (TypeError, ValueError):
        return default
    s = str(value).strip()
    return default if s.lower() in ("nan", "none", "nat", "") else s


def row_to_json(row: pd.Series, variance: float) -> dict:
    """将 CSV 一行转换为后端期望的 JSON 格式，NaN 使用各自默认值"""
    def v(k, default=0.0):
        val = row.get(k, default) if k in row else default
        return apply_variance(val, variance, default)

    def s(k, default=""):
        val = row.get(k, default) if k in row else default
        return _safe_str(val, default)

    def v_opt(k_alt, k_main, default=0.0):
        """优先取 k_alt，否则 k_main"""
        val = row.get(k_alt, row.get(k_main, default)) if k_alt in row else row.get(k_main, default)
        return apply_variance(val, variance, default)

    # 时间戳：使用当前时间模拟实时数据
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "timestamp": timestamp,
        "system_status": {
            "mode": s("当前模式", "指向"),
            "signal_source": _safe_str(row.get("当前信号源"), "0"),
            "source_status": s("信号源状态", "未连接"),
            "lock_status": s("锁定状态", "未锁定"),
            "lock_indicator": s("锁定指示", "未锁定"),
        },
        "signal_params": {
            "agc_threshold": v("AGC门限", 2.5),
            "agc_voltage": v("AGC电压", 0.0),
            "azimuth_error_voltage": v("方位误差电压", 5.0),
            "pitch_error_voltage": v("俯仰误差电压", 5.0),
        },
        "tracking_data": {
            "turntable_system": {
                "guide_azimuth": v("转台系引导方位角", 219.0),
                "guide_pitch": v("转台系引导俯仰角", 16.0),
                "guide_tilt": v("转台系引导倾斜角", 1.0),
                "current_azimuth": v("转台系方位角", 219.0),
                "current_pitch": v("转台系俯仰角", 16.0),
                "current_tilt": v("转台系倾斜角", 1.0),
                "deviation_azimuth": v("转台系方位偏差", 0.0),
                "deviation_pitch": v("转台系俯仰偏差", 0.0),
                "deviation_tilt": v("转台系倾斜偏差", 0.0),
            },
            "geodetic_system": {
                "guide_azimuth": v("大地系引导方位角", 218.0),
                "guide_pitch": v("大地系引导俯仰角", 16.0),
                "current_azimuth": v("大地系方位角", 218.0),
                "current_pitch_alt": v_opt("大地系引导俯仰角.1", "大地系引导俯仰角", 16.0),
                "deviation_azimuth": v("大地系方位偏差", 0.0),
                "deviation_pitch": v("大地系俯仰偏差", 0.0),
            },
        },
        "motor_diagnostics": {
            "motor_1": {
                "power_on": s("方位轴电机1上电", "是"),
                "status": s("方位轴电机1状态", "良好"),
                "current": v("方位轴电机1电流", 0.0),
                "voltage": v("方位轴电机1电压", 0.0),
                "inertia": v("方位轴电机1转动惯量", 0.0),
                "temp": v("方位轴电机1驱动器温度", 0.0),
            },
            "motor_2": {
                "power_on": s("方位轴电机2上电", "是"),
                "status": s("方位轴电机2状态", "良好"),
                "current": v("方位轴电机2电流", 0.0),
                "voltage": v("方位轴电机2电压", 0.0),
                "inertia": v("方位轴电机2转动惯量", 0.0),
                "temp": v("方位轴电机2驱动器温度", 0.0),
            },
        },
    }


def load_csv(path: Path) -> pd.DataFrame:
    """加载 CSV，支持 gbk 编码"""
    return pd.read_csv(path, encoding="gbk")


def send_data(url: str, data: dict) -> bool:
    """发送 JSON 到后端"""
    try:
        r = requests.post(url, json=data, timeout=5)
        if r.status_code == 200:
            resp = r.json()
            if resp.get("status") == "success":
                return True
            print(f"[警告] {resp.get('msg', r.text)}")
        else:
            print(f"[错误] HTTP {r.status_code}: {r.text[:200]}")
    except requests.exceptions.ConnectionError:
        print("[错误] 无法连接后端，请确认服务已启动 (python app.py)")
    except Exception as e:
        print(f"[错误] {e}")
    return False


def main():
    parser = argparse.ArgumentParser(description="数据模拟发送程序 - 从 data.csv 随机抽行发送到后端")
    parser.add_argument(
        "-c", "--csv",
        default=str(DEFAULT_CSV_PATH),
        help=f"CSV 文件路径 (默认: {DEFAULT_CSV_PATH})",
    )
    parser.add_argument(
        "-u", "--url",
        default=DEFAULT_API_URL,
        help=f"后端 API 地址 (默认: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help=f"发送间隔(秒)，需小于 1 秒 (默认: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "-v", "--variance",
        type=float,
        default=DEFAULT_VARIANCE,
        help="数字随机波动幅度，如 0.05 表示 ±5%% (默认: 0.05)",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="静默模式，不打印每次发送结果",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[错误] 找不到 CSV 文件: {csv_path}")
        return 1

    if args.interval >= 1:
        print("[警告] 间隔 >= 1 秒，将使用 0.5 秒")
        interval = 0.5
    else:
        interval = args.interval

    print(f"加载 CSV: {csv_path}")
    df = load_csv(csv_path)
    if len(df) == 0:
        print("[错误] CSV 无有效数据行")
        return 1
    print(f"共 {len(df)} 行数据，发送间隔 {interval}s，波动 ±{args.variance*100:.0f}%")
    print(f"目标: {args.url}")
    print("提示: 若被拒绝，请先用 POST /api/config/ip 将允许 IP 设为 127.0.0.1")
    print("按 Ctrl+C 停止\n")

    count = 0
    try:
        while True:
            row = df.sample(1).iloc[0]
            data = row_to_json(row, args.variance)

            if send_data(args.url, data):
                count += 1
                if not args.quiet:
                    print(f"[{count}] 发送成功 @ {data['timestamp']}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n已停止，共发送 {count} 条")


if __name__ == "__main__":
    exit(main() or 0)
