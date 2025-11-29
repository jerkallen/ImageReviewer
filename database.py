#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片审查系统 - 数据库模块
使用SQLite存储用户信息、操作记录和撤回历史
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: str = "data/app.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self.init_database()
    
    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使查询结果可以按列名访问
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT UNIQUE NOT NULL,
                    name TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建操作记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_ip TEXT NOT NULL,
                    user_name TEXT,
                    operation_type TEXT NOT NULL,
                    image_name TEXT NOT NULL,
                    source_folder TEXT NOT NULL,
                    target_folder TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建撤回历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS undo_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_ip TEXT NOT NULL,
                    operation_id INTEGER,
                    image_name TEXT NOT NULL,
                    from_folder TEXT NOT NULL,
                    to_folder TEXT NOT NULL,
                    txt_file_exists INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引以提高查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_operations_user_ip 
                ON operations(user_ip)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_operations_timestamp 
                ON operations(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_undo_history_user_ip 
                ON undo_history(user_ip)
            ''')
            
            print("数据库初始化完成")
    
    def get_or_create_user(self, ip: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取或创建用户
        
        Args:
            ip: 用户IP地址
            name: 用户名称（可选）
        
        Returns:
            用户信息字典
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 尝试获取现有用户
            cursor.execute('SELECT * FROM users WHERE ip = ?', (ip,))
            user = cursor.fetchone()
            
            if user:
                # 更新最后活跃时间
                cursor.execute('''
                    UPDATE users 
                    SET last_active = CURRENT_TIMESTAMP 
                    WHERE ip = ?
                ''', (ip,))
                
                # 如果提供了名称且不同，更新名称
                if name and name != user['name']:
                    cursor.execute('''
                        UPDATE users 
                        SET name = ? 
                        WHERE ip = ?
                    ''', (name, ip))
                
                # 重新获取更新后的用户信息
                cursor.execute('SELECT * FROM users WHERE ip = ?', (ip,))
                user = cursor.fetchone()
            else:
                # 创建新用户
                cursor.execute('''
                    INSERT INTO users (ip, name) 
                    VALUES (?, ?)
                ''', (ip, name))
                
                cursor.execute('SELECT * FROM users WHERE ip = ?', (ip,))
                user = cursor.fetchone()
            
            return dict(user) if user else {}
    
    def update_user_name(self, ip: str, name: str) -> bool:
        """
        更新用户名称
        
        Args:
            ip: 用户IP地址
            name: 新名称
        
        Returns:
            是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET name = ?, last_active = CURRENT_TIMESTAMP 
                    WHERE ip = ?
                ''', (name, ip))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"更新用户名称失败: {str(e)}")
            return False
    
    def log_operation(self, ip: str, user_name: Optional[str], op_type: str, 
                     image_name: str, source_folder: str, 
                     target_folder: Optional[str] = None) -> int:
        """
        记录操作
        
        Args:
            ip: 用户IP
            user_name: 用户名称
            op_type: 操作类型 (classify_ok, classify_nok, undo)
            image_name: 图片名称
            source_folder: 源文件夹
            target_folder: 目标文件夹
        
        Returns:
            操作记录ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO operations 
                (user_ip, user_name, operation_type, image_name, source_folder, target_folder)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ip, user_name, op_type, image_name, source_folder, target_folder))
            
            return cursor.lastrowid
    
    def add_undo_record(self, ip: str, image_name: str, from_folder: str, 
                       to_folder: str, txt_file_exists: bool, 
                       operation_id: Optional[int] = None) -> bool:
        """
        添加撤回记录
        
        Args:
            ip: 用户IP
            image_name: 图片名称
            from_folder: 源文件夹
            to_folder: 目标文件夹
            txt_file_exists: 是否存在txt标注文件
            operation_id: 关联的操作记录ID
        
        Returns:
            是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 添加新的撤回记录
                cursor.execute('''
                    INSERT INTO undo_history 
                    (user_ip, operation_id, image_name, from_folder, to_folder, txt_file_exists)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (ip, operation_id, image_name, from_folder, to_folder, int(txt_file_exists)))
                
                # 删除超过3条的旧记录（FIFO）
                cursor.execute('''
                    DELETE FROM undo_history 
                    WHERE user_ip = ? 
                    AND id NOT IN (
                        SELECT id FROM undo_history 
                        WHERE user_ip = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 3
                    )
                ''', (ip, ip))
                
                return True
        except Exception as e:
            print(f"添加撤回记录失败: {str(e)}")
            return False
    
    def get_undo_records(self, ip: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        获取用户的撤回历史
        
        Args:
            ip: 用户IP
            limit: 返回记录数量
        
        Returns:
            撤回记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM undo_history 
                WHERE user_ip = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (ip, limit))
            
            records = cursor.fetchall()
            return [dict(row) for row in records]
    
    def pop_undo_record(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        弹出并删除最新的撤回记录
        
        Args:
            ip: 用户IP
        
        Returns:
            撤回记录字典，如果没有则返回None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取最新的撤回记录
            cursor.execute('''
                SELECT * FROM undo_history 
                WHERE user_ip = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (ip,))
            
            record = cursor.fetchone()
            
            if record:
                # 删除该记录
                cursor.execute('''
                    DELETE FROM undo_history 
                    WHERE id = ?
                ''', (record['id'],))
                
                return dict(record)
            
            return None
    
    def query_operations(self, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None,
                        user_ip: Optional[str] = None,
                        operation_type: Optional[str] = None,
                        limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        查询操作记录
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            user_ip: 用户IP筛选
            operation_type: 操作类型筛选
            limit: 返回记录数量
            offset: 偏移量
        
        Returns:
            操作记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM operations WHERE 1=1'
            params = []
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(f"{start_date} 00:00:00")
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(f"{end_date} 23:59:59")
            
            if user_ip:
                query += ' AND user_ip = ?'
                params.append(user_ip)
            
            if operation_type:
                query += ' AND operation_type = ?'
                params.append(operation_type)
            
            query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            return [dict(row) for row in records]
    
    def get_operation_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        获取操作统计信息
        
        Args:
            days: 统计最近多少天的数据
        
        Returns:
            统计信息字典
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 总操作数
            cursor.execute('''
                SELECT COUNT(*) as total FROM operations 
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ''', (days,))
            total = cursor.fetchone()['total']
            
            # 按操作类型统计
            cursor.execute('''
                SELECT operation_type, COUNT(*) as count 
                FROM operations 
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY operation_type
            ''', (days,))
            by_type = {row['operation_type']: row['count'] for row in cursor.fetchall()}
            
            # 按用户统计
            cursor.execute('''
                SELECT user_ip, user_name, COUNT(*) as count 
                FROM operations 
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY user_ip 
                ORDER BY count DESC 
                LIMIT 10
            ''', (days,))
            by_user = [dict(row) for row in cursor.fetchall()]
            
            # 今日操作数
            cursor.execute('''
                SELECT COUNT(*) as today_count FROM operations 
                WHERE date(timestamp) = date('now')
            ''')
            today_count = cursor.fetchone()['today_count']
            
            return {
                'total': total,
                'by_type': by_type,
                'by_user': by_user,
                'today_count': today_count,
                'days': days
            }
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        获取所有用户列表
        
        Returns:
            用户列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY last_active DESC')
            users = cursor.fetchall()
            return [dict(row) for row in users]


# 创建全局数据库实例
_db_instance = None


def get_database(db_path: str = "data/app.db") -> Database:
    """获取数据库实例（单例模式）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance


if __name__ == "__main__":
    # 测试代码
    db = get_database("test.db")
    
    # 测试用户操作
    user = db.get_or_create_user("192.168.1.100", "张三")
    print(f"创建用户: {user}")
    
    # 测试记录操作
    op_id = db.log_operation("192.168.1.100", "张三", "classify_ok", 
                             "test.jpg", "project1", "project1/OK")
    print(f"记录操作ID: {op_id}")
    
    # 测试添加撤回记录
    db.add_undo_record("192.168.1.100", "test.jpg", "project1", 
                      "project1/OK", True, op_id)
    
    # 测试获取撤回记录
    undo_records = db.get_undo_records("192.168.1.100")
    print(f"撤回记录: {undo_records}")
    
    # 测试统计
    stats = db.get_operation_stats()
    print(f"统计信息: {stats}")
    
    # 清理测试数据库
    if os.path.exists("test.db"):
        os.remove("test.db")
    print("测试完成")

