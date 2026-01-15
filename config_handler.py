#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片确认工具 - 配置处理模块
"""
import os
import json
import logging
from typing import Dict, Any


class ConfigHandler:
    """配置处理类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.app_dir, config_file)
        
        # 默认配置
        self.default_config = {
            "host": "0.0.0.0",
            "port": 8501,
            "root_directory": "data",
            "logs_dir": "logs",
            "scan_root": "images",
            "image_extensions": [".jpg", ".jpeg", ".png", ".bmp"],
            "default_folders": {
                "ok": "OK",
                "nok": "NOK"
            },
            "feishu_settings": {
                "nok_send_enabled": False,
                "chat_id": ""
            }
        }
        
        # 加载配置
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保所有必要字段存在
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            else:
                # 如果配置文件不存在，创建默认配置
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            print(f"警告: 加载配置文件失败: {str(e)}, 使用默认配置")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """保存配置文件"""
        try:
            config_to_save = config if config is not None else self.config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"错误: 保存配置文件失败: {str(e)}")
            return False
    
    def get_absolute_path(self, path: str, base_path: str = None) -> str:
        """获取绝对路径"""
        if not path:
            return ""
            
        # 处理环境变量
        path = os.path.expandvars(path)
        
        # 如果已经是绝对路径，直接返回
        if os.path.isabs(path):
            return os.path.normpath(path)
        
        # 相对路径处理
        if base_path is None:
            base_path = self.app_dir
        
        return os.path.normpath(os.path.join(base_path, path))
    
    def get_root_directory(self) -> str:
        """获取数据根目录的绝对路径"""
        # 优先使用环境变量
        root_dir = os.environ.get('ROOT_DIRECTORY')
        if root_dir:
            return self.get_absolute_path(root_dir)
        
        # 使用配置文件中的值
        root_dir = self.config.get("root_directory", "data")
        return self.get_absolute_path(root_dir)
    
    def get_logs_directory(self) -> str:
        """获取日志目录的绝对路径"""
        root_dir = self.get_root_directory()
        logs_dir_relative = self.config.get("logs_dir", "logs")
        return os.path.join(root_dir, logs_dir_relative)
    
    def get_scan_root(self) -> str:
        """获取图片扫描根目录的绝对路径"""
        root_dir = self.get_root_directory()
        scan_root_relative = self.config.get("scan_root", "images")
        return os.path.join(root_dir, scan_root_relative)
    
    def get_host(self) -> str:
        """获取主机地址"""
        return self.config.get("host", "0.0.0.0")
    
    def get_port(self) -> int:
        """获取端口号"""
        return self.config.get("port", 8501)
    
    def get_image_extensions(self) -> list:
        """获取支持的图片扩展名"""
        return self.config.get("image_extensions", [".jpg", ".jpeg", ".png", ".bmp"])
    
    def get_default_folders(self) -> Dict[str, str]:
        """获取默认文件夹配置"""
        return self.config.get("default_folders", {"ok": "OK", "nok": "NOK"})
    
    def get_feishu_settings(self) -> Dict[str, Any]:
        """获取飞书设置"""
        return self.config.get("feishu_settings", {
            "nok_send_enabled": False,
            "chat_id": ""
        })
    
    def update_feishu_settings(self, nok_send_enabled: bool = None, chat_id: str = None) -> bool:
        """更新飞书设置"""
        try:
            feishu_settings = self.get_feishu_settings()
            
            if nok_send_enabled is not None:
                feishu_settings["nok_send_enabled"] = nok_send_enabled
            
            if chat_id is not None:
                feishu_settings["chat_id"] = chat_id
            
            self.config["feishu_settings"] = feishu_settings
            return self.save_config()
        except Exception as e:
            print(f"错误: 更新飞书设置失败: {str(e)}")
            return False
    
    def ensure_directories_exist(self) -> None:
        """确保所有必要目录存在"""
        directories = [
            self.get_root_directory(),
            self.get_logs_directory(),
            self.get_scan_root()
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"目录确认: {directory}")
            except Exception as e:
                print(f"警告: 无法创建目录 {directory}: {str(e)}")
    
    def is_docker(self) -> bool:
        """检查是否在Docker环境中运行"""
        try:
            # 检查 /.dockerenv 文件
            if os.path.exists('/.dockerenv'):
                return True
            
            # 检查 /proc/self/cgroup 文件中是否包含 docker
            cgroup_path = '/proc/self/cgroup'
            if os.path.exists(cgroup_path):
                with open(cgroup_path, 'r') as f:
                    return any('docker' in line for line in f)
            
            return False
        except Exception:
            return False
    
    def setup_logging(self) -> logging.Logger:
        """设置日志记录"""
        log_dir = self.get_logs_directory()
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "app.log")
        
        # 创建logger
        logger = logging.getLogger('image_gui')
        logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not logger.handlers:
            # 文件handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 格式器
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加handler
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def get_config_summary(self) -> str:
        """获取配置摘要信息"""
        summary = f"""
配置摘要:
- 数据根目录: {self.get_root_directory()}
- 日志目录: {self.get_logs_directory()}
- 图片扫描目录: {self.get_scan_root()}
- 服务器地址: {self.get_host()}:{self.get_port()}
- 支持的图片格式: {', '.join(self.get_image_extensions())}
- 默认文件夹: OK={self.get_default_folders()['ok']}, NOK={self.get_default_folders()['nok']}
- Docker环境: {'是' if self.is_docker() else '否'}
        """
        return summary


# 创建全局配置实例
config_handler = ConfigHandler()


def get_config_handler() -> ConfigHandler:
    """获取配置处理器实例"""
    return config_handler

