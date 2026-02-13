from DataClass import Info, SystemStatus, SignalParams, TurntableSystem, GeodeticSystem, MotorDetail


def parse_info(data: dict) -> Info:
    # 提取电机数据
    motors = {
        name: MotorDetail(**details) 
        for name, details in data.get("motor_diagnostics", {}).items()
    }
    
    # 组装 Info 对象
    info_obj = Info(
        timestamp=data.get("timestamp"),
        system_status=SystemStatus(**data.get("system_status", {})),
        signal_params=SignalParams(**data.get("signal_params", {})),
        turntable_system=TurntableSystem(**data.get("tracking_data", {}).get("turntable_system", {})),
        geodetic_system=GeodeticSystem(**data.get("tracking_data", {}).get("geodetic_system", {})),
        motor_diagnostics=motors
    )
    return info_obj

# 使用示例
# raw_json = {...} 
# my_info = parse_info(raw_json)
# print(my_info.motor_diagnostics['motor_1'].temp)