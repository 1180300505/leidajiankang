from DataClass import Info, SystemStatus, SignalParams, TurntableSystem, GeodeticSystem, MotorDetail
from database import DeviceDB
import json

# 进行数据故障分析
def analyze_data(info: Info, db: DeviceDB) -> dict:
    # 暂时只检查转台系，大地系，电机1，电机2
    ts_status = info.turntable_system
    gs_status = info.geodetic_system
    motor1_status = info.motor_diagnostics['motor_1']
    motor2_status = info.motor_diagnostics['motor_2']

    alter_json = {}
    if ts_status.guide_azimuth > 124 or ts_status.guide_azimuth < 116.5:
        alter_json['turntable_system'] = '转台系方位角异常'
    if gs_status.guide_azimuth > 114 or gs_status.guide_azimuth < 106:
        alter_json['geodetic_system'] = '大地系方位角异常'
    if motor1_status.voltage < 217 or motor1_status.voltage > 223:
        alter_json['motor_1'] = '电机1电压异常'
    if motor2_status.voltage < 217 or motor2_status.voltage > 223:
        alter_json['motor_2'] = '电机2电压异常'
    
    # 评价故障程度
    if len(alter_json) > 2:
        alter_json['故障程度'] = '严重故障'
        db.insert_error(info.timestamp, alter_json['故障程度'], json.dumps(alter_json))
    elif len(alter_json) >= 1:
        alter_json['故障程度'] = '一般故障'
        db.insert_error(info.timestamp, alter_json['故障程度'], json.dumps(alter_json))
    else:
        alter_json['故障程度'] = '无异常'
    
    return alter_json


