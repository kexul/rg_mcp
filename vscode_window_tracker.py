import os
import json
import time
from datetime import datetime
import win32gui
import win32process
import psutil
from pathlib import Path

class VSCodeWindowTracker:
    def __init__(self):
        self.config_file = Path.home() / "vscode_window_config.json"
        
    def get_window_info(self, hwnd):
        """获取窗口信息"""
        try:
            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd)
            
            # 获取进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # 获取进程信息
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                exe_path = process.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
                exe_path = "Unknown"
                
            return {
                'window_title': window_title,
                'process_name': process_name,
                'exe_path': exe_path,
                'pid': pid,
                'hwnd': hwnd
            }
        except Exception as e:
            return None
    
    def is_vscode_window(self, window_info):
        """判断是否为VS Code窗口"""
        if not window_info:
            return False
            
        process_name = window_info['process_name'].lower()
        window_title = window_info['window_title'].lower()
        
        # 检查进程名是否包含vscode相关关键词
        vscode_processes = ['code.exe', 'code', 'vscode']
        process_match = any(vscode_proc in process_name for vscode_proc in vscode_processes)
        
        # 检查窗口标题是否包含vscode相关信息
        title_match = 'visual studio code' in window_title or 'vscode' in window_title
        
        return process_match or title_match
    
    def get_active_vscode_window(self):
        """获取当前活动的VS Code窗口"""
        try:
            # 获取当前焦点窗口
            active_hwnd = win32gui.GetForegroundWindow()
            
            if active_hwnd:
                window_info = self.get_window_info(active_hwnd)
                
                if window_info and self.is_vscode_window(window_info):
                    return window_info
                    
            # 如果当前焦点窗口不是VS Code，则查找所有VS Code窗口
            vscode_windows = []
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_info = self.get_window_info(hwnd)
                    if window_info and self.is_vscode_window(window_info):
                        windows.append(window_info)
                return True
            
            win32gui.EnumWindows(enum_windows_callback, vscode_windows)
            
            # 返回第一个找到的VS Code窗口
            if vscode_windows:
                return vscode_windows[0]
                
        except Exception as e:
            print(f"获取VS Code窗口时出错: {e}")
            
        return None
    
    def save_window_info(self, window_info):
        """保存窗口信息到配置文件"""
        try:
            # 准备保存的数据
            config_data = {
                'last_updated': datetime.now().isoformat(),
                'vscode_window': {
                    'window_title': window_info['window_title'],
                    'process_name': window_info['process_name'],
                    'exe_path': window_info['exe_path'],
                    'pid': window_info['pid']
                }
            }
            
            # 如果配置文件已存在，读取历史记录
            history = []
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        if 'history' in existing_data:
                            history = existing_data['history']
                except Exception as e:
                    print(f"读取历史记录时出错: {e}")
            
            # 添加当前记录到历史
            history.append({
                'timestamp': datetime.now().isoformat(),
                'window_title': window_info['window_title'],
                'process_name': window_info['process_name']
            })
            
            # 只保留最近10条记录
            if len(history) > 10:
                history = history[-10:]
            
            config_data['history'] = history
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
                
            print(f"VS Code窗口信息已保存到: {self.config_file}")
            print(f"窗口标题: {window_info['window_title']}")
            
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
    
    def extract_workspace_path(self, window_title):
        """从VS Code窗口标题中提取工作空间路径"""
        try:
            # 移除VS Code相关后缀
            path = window_title.replace(" - Visual Studio Code", "")
            path = path.replace("Visual Studio Code", "")
            
            # 移除未保存标记
            path = path.replace("● ", "")
            path = path.strip()
            
            # 直接返回路径（已配置为完整路径）
            if path and os.path.exists(path) and os.path.isdir(path):
                return path
            
            # 如果路径无效，返回当前工作目录
            return os.getcwd()
            
        except Exception as e:
            print(f"提取工作空间路径时出错: {e}")
            return os.getcwd()

    def get_current_workspace_path(self):
        """获取当前VS Code工作空间路径"""
        window_info = self.get_active_vscode_window()
        
        if window_info:
            workspace_path = self.extract_workspace_path(window_info['window_title'])
            print(f"检测到VS Code工作空间: {workspace_path}")
            return workspace_path
        else:
            # 如果没有找到VS Code窗口，尝试从配置文件读取
            return self.get_workspace_from_config()
    
    def get_workspace_from_config(self):
        """从配置文件获取上次保存的工作空间信息"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    if 'vscode_window' in config_data:
                        window_title = config_data['vscode_window']['window_title']
                        workspace_path = self.extract_workspace_path(window_title)
                        print(f"从配置文件获取工作空间: {workspace_path}")
                        return workspace_path
        except Exception as e:
            print(f"从配置文件读取工作空间时出错: {e}")
        
        # 如果所有方法都失败，返回当前目录
        fallback_path = os.getcwd()
        print(f"使用默认工作空间: {fallback_path}")
        return fallback_path

    def run(self):
        """主运行函数"""
        print("正在检测VS Code窗口...")
        
        window_info = self.get_active_vscode_window()
        
        if window_info:
            print(f"找到VS Code窗口: {window_info['window_title']}")
            self.save_window_info(window_info)
        else:
            print("未找到活动的VS Code窗口")
            print("请确保VS Code正在运行并且窗口可见")

def main():
    """主函数"""
    tracker = VSCodeWindowTracker()
    tracker.run()

if __name__ == "__main__":
    main()