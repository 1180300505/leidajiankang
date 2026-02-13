from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class SystemStatus:
    mode: str = ""              # 当前模式
    signal_source: str = ""     # 当前信号源
    source_status: str = ""     # 信号源状态
    lock_status: str = ""       # 锁定状态
    lock_indicator: str = ""    # 锁定指示器状态

@dataclass
class SignalParams:
    agc_threshold: float = 0.0          # AGC (自动增益控制) 门限
    agc_voltage: float = 0.0            # AGC 电压
    azimuth_error_voltage: float = 0.0  # 方位误差电压
    pitch_error_voltage: float = 0.0    # 俯仰误差电压

@dataclass
class TurntableSystem:
    # 转台坐标系数据
    guide_azimuth: float = 0.0      # 转台系引导方位角
    guide_pitch: float = 0.0        # 转台系引导俯仰角
    guide_tilt: float = 0.0         # 转台系引导倾斜角
    current_azimuth: float = 0.0    # 转台系当前方位角
    current_pitch: float = 0.0      # 转台系当前俯仰角
    current_tilt: float = 0.0       # 转台系当前倾斜角
    deviation_azimuth: float = 0.0  # 转台系方位偏差
    deviation_pitch: float = 0.0    # 转台系俯仰偏差
    deviation_tilt: float = 0.0     # 转台系倾斜偏差

@dataclass
class GeodeticSystem:
    # 大地坐标系数据
    guide_azimuth: float = 0.0      # 大地系引导方位角
    guide_pitch: float = 0.0        # 大地系引导俯仰角
    current_azimuth: float = 0.0    # 大地系当前方位角
    current_pitch_alt: float = 0.0  # 大地系引导俯仰角 (修正/备份值)
    deviation_azimuth: float = 0.0  # 大地系方位偏差
    deviation_pitch: float = 0.0    # 大地系俯仰偏差

@dataclass
class MotorDetail:
    # 电机监控详细数据
    power_on: bool = False  # 电机上电状态
    status: str = ""        # 电机运行状态
    current: float = 0.0    # 电机电流
    voltage: float = 0.0    # 电机电压
    inertia: float = 0.0    # 电机转动惯量
    temp: float = 0.0       # 驱动器温度

@dataclass
class Info:
    timestamp: str = ""
    system_status: SystemStatus = field(default_factory=SystemStatus)
    signal_params: SignalParams = field(default_factory=SignalParams)
    turntable_system: TurntableSystem = field(default_factory=TurntableSystem)
    geodetic_system: GeodeticSystem = field(default_factory=GeodeticSystem)
    # 将电机存储为字典或列表，方便扩展
    motor_diagnostics: dict[str, MotorDetail] = field(default_factory=dict)