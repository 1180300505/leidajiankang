import sqlite3
import os
import datetime

def get_or_create_db(db_name="device_monitor.db"):
    # 1. 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, db_name)
    
    # 检查文件是否存在
    file_exists = os.path.exists(db_path)
    
    try:
        # 2. 尝试连接数据库
        # 如果文件不存在，connect 会自动创建一个空的
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if file_exists:
            # 3. 验证是否是合法的数据库（尝试读取系统表）
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                print(f"成功连接现有数据库: {db_path}")
            except sqlite3.DatabaseError:
                print("检测到文件但不是合法的数据库，正在重新初始化...")
                conn.close()
                os.remove(db_path)  # 删除损坏的文件
                return get_or_create_db(db_name) # 递归调用以重新创建
        else:
            print(f"未检测到数据库，正在新建: {db_path}")
            
        return conn
    except Exception as e:
        print(f"数据库操作异常: {e}")
        return None
    
class DeviceDB:
    def __init__(self, db_name="device_monitor.db"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, db_name)
        
        # 关键改动：添加 check_same_thread=False
        self.conn = sqlite3.connect(
            self.db_path, 
            check_same_thread=False
        ) 
        self.cursor = self.conn.cursor()
        self._create_table()
        self.source_ip = self.get_active_ip()

    def _create_table(self):
        """创建日志表及配置表"""
        # 1. 修改后的 system_logs 表，增加 source_ip
        sql_logs = '''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME UNIQUE,
            source_ip TEXT,  -- 新增：存储该条数据来源的上位机 IP
            -- 系统状态
            sys_mode TEXT, sys_signal_source TEXT, sys_source_status TEXT, 
            sys_lock_status TEXT, sys_lock_indicator TEXT,
            -- 信号参数
            sig_agc_threshold TEXT, sig_agc_voltage TEXT, 
            sig_azimuth_err_v TEXT, sig_pitch_err_v TEXT,
            -- 转台系 (turntable)
            tt_guide_az TEXT, tt_guide_pt TEXT, tt_guide_tl TEXT,
            tt_curr_az TEXT, tt_curr_pt TEXT, tt_curr_tl TEXT,
            tt_dev_az TEXT, tt_dev_pt TEXT, tt_dev_tl TEXT,
            -- 大地系 (geodetic)
            geo_guide_az TEXT, geo_guide_pt TEXT, geo_curr_az TEXT, 
            geo_curr_pt_alt TEXT, geo_dev_az TEXT, geo_dev_pt TEXT,
            -- 电机1 (motor_1)
            m1_power TEXT, m1_status TEXT, m1_current TEXT, 
            m1_voltage TEXT, m1_inertia TEXT, m1_temp TEXT,
            -- 电机2 (motor_2)
            m2_power TEXT, m2_status TEXT, m2_current TEXT, 
            m2_voltage TEXT, m2_inertia TEXT, m2_temp TEXT
        )
        '''

        sql_errors = '''
        CREATE TABLE IF NOT EXISTS system_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            error_type TEXT,
            error_message TEXT
        )
        '''
        
        self.cursor.execute(sql_logs)
        self.cursor.execute(sql_errors)
        self.conn.commit()
    
    # --- IP 配置核心逻辑 ---
    def get_active_ip(self):
        """
        获取当前生效的上位机 IP。
        优先级：配置表手动设置 > 数据库中最新一条记录的 IP > 默认 IP
        """

        # 尝试获取最新一条日志中的 IP
        self.cursor.execute("SELECT source_ip FROM system_logs ORDER BY timestamp DESC LIMIT 1")
        res = self.cursor.fetchone()
        if res and res[0]:
            return res[0]

        # 若都没有，返回默认本地测试 IP
        return "127.0.0.1"
    
    def set_active_ip(self, ip):
        """设置当前生效的上位机 IP。"""
        self.source_ip = ip

    def insert_data(self, data):
        """【增】解析 JSON 字典并插入数据库"""
        # 提取各个层级的数据
        sys = data['system_status']
        sig = data['signal_params']
        tt = data['tracking_data']['turntable_system']
        geo = data['tracking_data']['geodetic_system']
        m1 = data['motor_diagnostics']['motor_1']
        m2 = data['motor_diagnostics']['motor_2']

        sql = '''
        INSERT OR REPLACE INTO system_logs (
            timestamp, source_ip, sys_mode, sys_signal_source, sys_source_status, sys_lock_status, sys_lock_indicator,
            sig_agc_threshold, sig_agc_voltage, sig_azimuth_err_v, sig_pitch_err_v,
            tt_guide_az, tt_guide_pt, tt_guide_tl, tt_curr_az, tt_curr_pt, tt_curr_tl, tt_dev_az, tt_dev_pt, tt_dev_tl,
            geo_guide_az, geo_guide_pt, geo_curr_az, geo_curr_pt_alt, geo_dev_az, geo_dev_pt,
            m1_power, m1_status, m1_current, m1_voltage, m1_inertia, m1_temp,
            m2_power, m2_status, m2_current, m2_voltage, m2_inertia, m2_temp
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        '''
        
        params = (
            data['timestamp'], self.source_ip, sys['mode'], sys['signal_source'], sys['source_status'], sys['lock_status'], sys['lock_indicator'],
            sig['agc_threshold'], sig['agc_voltage'], sig['azimuth_error_voltage'], sig['pitch_error_voltage'],
            tt['guide_azimuth'], tt['guide_pitch'], tt['guide_tilt'], tt['current_azimuth'], tt['current_pitch'], tt['current_tilt'], tt['deviation_azimuth'], tt['deviation_pitch'], tt['deviation_tilt'],
            geo['guide_azimuth'], geo['guide_pitch'], geo['current_azimuth'], geo['current_pitch_alt'], geo['deviation_azimuth'], geo['deviation_pitch'],
            m1['power_on'], m1['status'], m1['current'], m1['voltage'], m1['inertia'], m1['temp'],
            m2['power_on'], m2['status'], m2['current'], m2['voltage'], m2['inertia'], m2['temp']
        )
        
        self.cursor.execute(sql, params)
        self.conn.commit()

    def query_by_time(self, start_time, end_time):
        """【查】查询指定时间段的数据"""
        sql = "SELECT * FROM system_logs WHERE timestamp BETWEEN ? AND ?"
        self.cursor.execute(sql, (start_time, end_time))
        return self.cursor.fetchall()

    def update_status(self, timestamp, new_mode):
        """【改】修改特定时间点的模式（示例）"""
        sql = "UPDATE system_logs SET sys_mode = ? WHERE timestamp = ?"
        self.cursor.execute(sql, (new_mode, timestamp))
        self.conn.commit()

    def delete_data(self, timestamp):
        """【删】删除特定时间的数据"""
        sql = "DELETE FROM system_logs WHERE timestamp = ?"
        self.cursor.execute(sql, (timestamp,))
        self.conn.commit()

    def close(self):
        self.conn.close()
    
    def query_paged(self, page=1, page_size=10, sort_order="DESC"):
        """
        sort_order: "DESC" (最新在前) 或 "ASC" (最早在前)
        """
        offset = (page - 1) * page_size
        
        # 关键修改：在 SQL 中动态加入排序参数
        # 注意：为了防止 SQL 注入，这里对 sort_order 做了简单检查
        order_str = "DESC" if sort_order.upper() == "DESC" else "ASC"
        
        sql = f"SELECT * FROM system_logs ORDER BY timestamp {order_str} LIMIT ? OFFSET ?"
        self.cursor.execute(sql, (page_size, offset))
        
        rows = self.cursor.fetchall()
        keys = [desc[0] for desc in self.cursor.description]
        data = [dict(zip(keys, row)) for row in rows]
        
        self.cursor.execute("SELECT COUNT(*) FROM system_logs")
        total = self.cursor.fetchone()[0]
        
        return data, total

    def query_range(self, start_time, end_time):
        """获取指定时间段内的所有记录"""
        sql = "SELECT * FROM system_logs WHERE datetime(timestamp) BETWEEN datetime(?) AND datetime(?)"
        print(f"DEBUG: 正在查询范围 {start_time} 到 {end_time}")
    
        # 先查一下数据库里最近的一条数据是什么时间，对比一下格式
        self.cursor.execute("SELECT timestamp FROM system_logs ORDER BY timestamp DESC LIMIT 1")
        last_record = self.cursor.fetchone()
        print(f"DEBUG: 数据库中最新的一条记录时间是: {last_record}")
        self.cursor.execute(sql, (start_time, end_time))
        rows = self.cursor.fetchall()
        print(f"查询到 {len(rows)} 条数据")
        keys = [desc[0] for desc in self.cursor.description]
        return [dict(zip(keys, row)) for row in rows]

    def insert_error(self, timestamp, error_type, error_message):
        """记录错误信息"""
        sql = "INSERT INTO system_errors (timestamp, error_type, error_message) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (timestamp, error_type, error_message))
        self.conn.commit()

    def calculate_daily_score(self, target_date_str):
        """
        计算指定日期的健康分
        :param target_date_str: 格式为 'YYYY-MM-DD'
        """
        # 1. 统计该天不同类型的故障数量
        query = """
            SELECT error_type, COUNT(*) 
            FROM system_errors 
            WHERE timestamp LIKE ? 
            GROUP BY error_type
        """
        self.cursor.execute(query, (f"{target_date_str}%",))
        results = self.cursor.fetchall()

        # 2. 初始满分 100
        score = 100
        details = {"严重故障": 0, "一般故障": 0}

        for err_type, count in results:
            if err_type == '严重故障':
                score -= (count * 2)
                details["严重故障"] = count
            elif err_type == '一般故障':
                score -= (count * 1)
                details["一般故障"] = count
        
        # 3. 边界限制
        score = max(0, score)
        return score, details

    def get_weekly_health_report(self):
        report = []
        today = datetime.date.today()

        for i in range(6, -1, -1):  # 包含今天在内的过去7天
            day = today - datetime.timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            
            score, details = self.calculate_daily_score(day_str)
            
            report.append({
                "date": day_str,
                "display_date": day.strftime('%m月%d日'),
                "score": score,
                "fault_count": details["严重故障"] + details["一般故障"],
                "status": "良好" if score >= 90 else ("警告" if score >= 70 else "危险")
            })
        return report

# --- 测试使用 ---
if __name__ == "__main__":
    db = DeviceDB()

    # 模拟你给出的 JSON 数据
    my_json = {
        "timestamp": "2026-02-13 11:12:15",
        "system_status": {"mode": "自动", "signal_source": "北斗", "source_status": "正常", "lock_status": "锁定", "lock_indicator": "绿"},
        "signal_params": {"agc_threshold": "1.0", "agc_voltage": "2.5", "azimuth_error_voltage": "0.01", "pitch_error_voltage": "0.02"},
        "tracking_data": {
            "turntable_system": {"guide_azimuth": "100", "guide_pitch": "45", "guide_tilt": "0", "current_azimuth": "100.1", "current_pitch": "45.1", "current_tilt": "0.1", "deviation_azimuth": "0.1", "deviation_pitch": "0.1", "deviation_tilt": "0.1"},
            "geodetic_system": {"guide_azimuth": "100", "guide_pitch": "45", "current_azimuth": "100.1", "current_pitch_alt": "45.1", "deviation_azimuth": "0.1", "deviation_pitch": "0.1"}
        },
        "motor_diagnostics": {
            "motor_1": {"power_on": "是", "status": "良好", "current": "2A", "voltage": "24V", "inertia": "0.5", "temp": "40"},
            "motor_2": {"power_on": "是", "status": "良好", "current": "1.8A", "voltage": "24V", "inertia": "0.5", "temp": "38"}
        }
    }

    # 1. 增
    db.insert_data(my_json)
    print("插入成功")

    # 2. 查
    results = db.query_by_time("2026-02-13 00:00:00", "2026-02-14 00:00:00")
    print(f"查询到 {len(results)} 条数据")

    # 3. 改
    db.update_status("2026-02-13 11:12:15", "手动模式")
    
    # 4. 删
    # db.delete_data("2026-02-13 11:12:15")

    db.close()