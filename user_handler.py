#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片审查系统 - 用户管理模块
处理用户IP识别和用户名管理
"""
from flask import Request
from typing import Optional
from database import get_database


def get_client_ip(request: Request) -> str:
    """
    从Flask request获取客户端IP地址
    优先获取真实IP（处理代理情况）
    
    Args:
        request: Flask请求对象
    
    Returns:
        客户端IP地址
    """
    # 尝试从X-Forwarded-For头获取（处理代理/负载均衡情况）
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For可能包含多个IP，取第一个（客户端真实IP）
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return ip
    
    # 尝试从X-Real-IP头获取
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP').strip()
    
    # 最后使用remote_addr
    return request.remote_addr or '未知IP'


def get_user_display_name(ip: str, db=None) -> str:
    """
    获取用户显示名称
    如果用户设置了名称则返回名称，否则返回IP
    
    Args:
        ip: 用户IP地址
        db: 数据库实例（可选）
    
    Returns:
        用户显示名称
    """
    if db is None:
        db = get_database()
    
    user = db.get_or_create_user(ip)
    
    if user.get('name'):
        return f"{user['name']}({ip})"
    else:
        return ip


def format_user_info(user: dict) -> dict:
    """
    格式化用户信息用于前端显示
    
    Args:
        user: 数据库用户记录
    
    Returns:
        格式化后的用户信息
    """
    return {
        'ip': user.get('ip', '未知IP'),
        'name': user.get('name', ''),
        'display_name': user.get('name') if user.get('name') else user.get('ip', '未知IP'),
        'first_seen': user.get('first_seen'),
        'last_active': user.get('last_active')
    }


if __name__ == "__main__":
    # 测试代码
    from flask import Flask
    from werkzeug.test import Client
    
    app = Flask(__name__)
    
    @app.route('/test')
    def test():
        from flask import request
        ip = get_client_ip(request)
        display_name = get_user_display_name(ip)
        return f"IP: {ip}, Display: {display_name}"
    
    with app.test_client() as client:
        # 测试基本请求
        response = client.get('/test')
        print(f"基本请求: {response.data.decode()}")
        
        # 测试带X-Forwarded-For的请求
        response = client.get('/test', headers={'X-Forwarded-For': '192.168.1.100, 10.0.0.1'})
        print(f"X-Forwarded-For请求: {response.data.decode()}")
    
    print("测试完成")

