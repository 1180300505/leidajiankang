import os
import subprocess

def run_build():
    entry_point = "app.py"
    
    cmd = [
        "pyinstaller",
        "--onedir",
        "--noconfirm",
        "--clean",
        "--name", "RadarBackend",
        # 核心：直接收集整个 dns 及其所有子模块，不再手动列举
        "--collect-submodules", "dns",
        "--collect-submodules", "eventlet",
    ]
    
    # 1. 依然保留 eventlet 的 hubs 隐藏导入（保险起见）
    hubs = ['epolls', 'kqueue', 'selects', 'poll', 'pyevent']
    for hub in hubs:
        cmd.extend(["--hidden-import", f"eventlet.hubs.{hub}"])
    
    # 2. 补充 eventlet 必须的驱动
    cmd.extend(["--hidden-import", "engineio.async_drivers.eventlet"])
    
    # 3. 针对 dns.btree 的特别补丁
    # 有些版本的 dnspython 将 btree 放在了非常隐蔽的地方
    cmd.extend(["--hidden-import", "dns.btree"]) 
    
    cmd.append(entry_point)
    
    print(f"🚀 执行最终修正版打包...\n")
    subprocess.check_call(cmd)

if __name__ == "__main__":
    run_build()