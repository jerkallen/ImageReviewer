#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片审查系统 - Flask主应用
提供所有Web接口和API
"""
import os
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from config_handler import get_config_handler
from database import get_database
from user_handler import get_client_ip, get_user_display_name, format_user_info
from image_handler import (
    scan_project_folders, get_image_list, get_image_count,
    load_and_process_image, move_image_with_txt, create_thumbnail
)

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'image_reviewer_secret_key_2024'

# 配置ProxyFix中间件，正确处理代理请求以获取真实客户端IP
# x_for=1: 信任X-Forwarded-For头的第一个值（客户端IP）
# x_proto=1: 信任X-Forwarded-Proto头（http/https）
# x_host=1: 信任X-Forwarded-Host头
# x_prefix=1: 信任X-Forwarded-Prefix头
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# 加载配置
config = get_config_handler()
db = get_database()

# 全局状态（多用户共享）
global_state = {
    'current_folder': None,
    'current_index': 0
}

# 获取配置值
root_directory = config.get_root_directory()
scan_root = config.get_scan_root()
ok_folder_name = config.get_default_folders().get('ok', 'OK')
nok_folder_name = config.get_default_folders().get('nok', 'NOK')

print(f"根目录: {root_directory}")
print(f"扫描目录: {scan_root}")


# ==================== 页面路由 ====================

@app.route('/')
def index():
    """主审查页面"""
    return render_template('index.html')


@app.route('/history')
def history():
    """操作历史页面"""
    return render_template('history.html')


@app.route('/review')
def review():
    """结果确认页面"""
    return render_template('review.html')


# ==================== 基础API ====================

@app.route('/api/folders')
def api_folders():
    """获取项目文件夹列表"""
    try:
        folders = scan_project_folders(scan_root, ok_folder_name, nok_folder_name)
        
        # 为每个文件夹添加图片数量统计
        folder_list = []
        for name, info in folders.items():
            待审查_count = get_image_count(info['path'])
            ok_count = get_image_count(info['ok_folder'])
            nok_count = get_image_count(info['nok_folder'])
            
            folder_list.append({
                'name': name,
                'path': info['path'],
                'pending_count': 待审查_count,
                'ok_count': ok_count,
                'nok_count': nok_count,
                'total_count': 待审查_count + ok_count + nok_count
            })
        
        # 按名称排序
        folder_list.sort(key=lambda x: x['name'])
        
        return jsonify({
            'success': True,
            'folders': folder_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/images')
def api_images():
    """获取指定文件夹的图片列表"""
    folder = request.args.get('folder')
    
    if not folder:
        return jsonify({'success': False, 'error': '未指定文件夹'}), 400
    
    try:
        folder_path = os.path.join(scan_root, folder)
        
        if not os.path.exists(folder_path):
            return jsonify({'success': False, 'error': '文件夹不存在'}), 404
        
        image_list = get_image_list(folder_path, config.get_image_extensions())
        
        return jsonify({
            'success': True,
            'folder': folder,
            'images': image_list,
            'count': len(image_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/image')
def api_image():
    """获取图片（base64编码，含边界框）"""
    folder = request.args.get('folder')
    index = request.args.get('index', 0, type=int)
    rotate = request.args.get('rotate', 0, type=int)
    bbox = request.args.get('bbox', 1, type=int)
    
    if not folder:
        return jsonify({'success': False, 'error': '未指定文件夹'}), 400
    
    try:
        folder_path = os.path.join(scan_root, folder)
        image_list = get_image_list(folder_path, config.get_image_extensions())
        
        if index < 0 or index >= len(image_list):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        image_name = image_list[index]
        image_path = os.path.join(folder_path, image_name)
        
        # 加载并处理图片
        img_base64, img_info = load_and_process_image(
            image_path,
            rotate=bool(rotate),
            show_bbox=bool(bbox)
        )
        
        if img_base64 is None:
            return jsonify({'success': False, 'error': '加载图片失败'}), 500
        
        # 获取文件修改时间
        modify_time = os.path.getmtime(image_path)
        modify_time_str = datetime.fromtimestamp(modify_time).strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'image': img_base64,
            'name': image_name,
            'index': index,
            'total': len(image_list),
            'info': img_info,
            'modify_time': modify_time_str
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/preload')
def api_preload():
    """预加载图片（用于后台预加载）"""
    folder = request.args.get('folder')
    index = request.args.get('index', 0, type=int)
    
    if not folder:
        return jsonify({'success': False, 'error': '未指定文件夹'}), 400
    
    try:
        folder_path = os.path.join(scan_root, folder)
        image_list = get_image_list(folder_path, config.get_image_extensions())
        
        if index < 0 or index >= len(image_list):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        image_name = image_list[index]
        image_path = os.path.join(folder_path, image_name)
        
        # 简单加载图片（不处理边界框以加快速度）
        img_base64, _ = load_and_process_image(
            image_path,
            rotate=False,
            show_bbox=False
        )
        
        return jsonify({
            'success': True,
            'image': img_base64,
            'index': index
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 全局状态API ====================

@app.route('/api/state', methods=['GET'])
def api_get_state():
    """获取全局状态"""
    return jsonify({
        'success': True,
        'state': global_state
    })


@app.route('/api/state', methods=['POST'])
def api_update_state():
    """更新全局状态"""
    data = request.json
    
    if 'current_folder' in data:
        global_state['current_folder'] = data['current_folder']
    
    if 'current_index' in data:
        global_state['current_index'] = data['current_index']
    
    return jsonify({
        'success': True,
        'state': global_state
    })


# ==================== 用户API ====================

@app.route('/api/user', methods=['GET'])
def api_get_user():
    """获取当前用户信息"""
    ip = get_client_ip(request)
    user = db.get_or_create_user(ip)
    
    return jsonify({
        'success': True,
        'user': format_user_info(user)
    })


@app.route('/api/user/name', methods=['POST'])
def api_update_user_name():
    """更新用户名称"""
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'error': '名称不能为空'}), 400
    
    ip = get_client_ip(request)
    success = db.update_user_name(ip, name)
    
    if success:
        user = db.get_or_create_user(ip)
        return jsonify({
            'success': True,
            'user': format_user_info(user)
        })
    else:
        return jsonify({'success': False, 'error': '更新失败'}), 500


# ==================== 分类操作API ====================

@app.route('/api/classify', methods=['POST'])
def api_classify():
    """分类图片（OK/NOK）"""
    data = request.json
    folder = data.get('folder')
    image_name = data.get('image_name')
    category = data.get('category', 'ok').lower()
    
    if not folder or not image_name:
        return jsonify({'success': False, 'error': '参数不完整'}), 400
    
    if category not in ['ok', 'nok']:
        return jsonify({'success': False, 'error': '无效的分类'}), 400
    
    try:
        # 获取用户信息
        ip = get_client_ip(request)
        user = db.get_or_create_user(ip)
        user_name = user.get('name')
        
        # 构建路径
        source_folder = os.path.join(scan_root, folder)
        src_path = os.path.join(source_folder, image_name)
        
        target_folder_name = ok_folder_name if category == 'ok' else nok_folder_name
        target_folder = os.path.join(source_folder, target_folder_name)
        dst_path = os.path.join(target_folder, image_name)
        
        if not os.path.exists(src_path):
            return jsonify({'success': False, 'error': '源文件不存在'}), 404
        
        # 移动文件
        txt_exists = move_image_with_txt(src_path, dst_path)
        
        # 记录操作
        op_type = 'classify_ok' if category == 'ok' else 'classify_nok'
        op_id = db.log_operation(
            ip, user_name, op_type, image_name,
            source_folder, target_folder
        )
        
        # 添加到撤回历史
        db.add_undo_record(
            ip, image_name, source_folder, target_folder,
            txt_exists, op_id
        )
        
        return jsonify({
            'success': True,
            'message': f'已将 {image_name} 移动到 {target_folder_name} 文件夹',
            'category': category
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 撤回功能API ====================

@app.route('/api/undo/available', methods=['GET'])
def api_undo_available():
    """检查是否有可撤回操作"""
    ip = get_client_ip(request)
    records = db.get_undo_records(ip, limit=1)
    
    return jsonify({
        'success': True,
        'available': len(records) > 0,
        'count': len(db.get_undo_records(ip, limit=3))
    })


@app.route('/api/undo', methods=['POST'])
def api_undo():
    """执行撤回操作"""
    try:
        ip = get_client_ip(request)
        user = db.get_or_create_user(ip)
        user_name = user.get('name')
        
        # 获取最新的撤回记录
        record = db.pop_undo_record(ip)
        
        if not record:
            return jsonify({'success': False, 'error': '没有可撤回的操作'}), 400
        
        # 构建文件路径
        image_name = record['image_name']
        from_folder = record['from_folder']
        to_folder = record['to_folder']
        txt_exists = bool(record['txt_file_exists'])
        
        src_path = os.path.join(to_folder, image_name)
        dst_path = os.path.join(from_folder, image_name)
        
        if not os.path.exists(src_path):
            return jsonify({'success': False, 'error': '文件已被移动或删除'}), 404
        
        # 移动文件回源位置
        move_image_with_txt(src_path, dst_path)
        
        # 记录撤回操作
        db.log_operation(
            ip, user_name, 'undo', image_name,
            to_folder, from_folder
        )
        
        # 提取文件夹名称用于显示
        from_folder_name = os.path.basename(from_folder)
        to_folder_name = os.path.basename(to_folder)
        
        return jsonify({
            'success': True,
            'message': f'已撤回：{image_name} 从 {to_folder_name} 移回 {from_folder_name}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 操作历史API ====================

@app.route('/api/operations', methods=['GET'])
def api_operations():
    """查询操作记录"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_ip = request.args.get('user_ip')
    operation_type = request.args.get('operation_type')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    try:
        operations = db.query_operations(
            start_date, end_date, user_ip, operation_type, limit, offset
        )
        
        return jsonify({
            'success': True,
            'operations': operations,
            'count': len(operations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/operations/stats', methods=['GET'])
def api_operations_stats():
    """获取操作统计"""
    days = request.args.get('days', 7, type=int)
    
    try:
        stats = db.get_operation_stats(days)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users', methods=['GET'])
def api_users():
    """获取所有用户列表"""
    try:
        users = db.get_all_users()
        formatted_users = [format_user_info(u) for u in users]
        
        return jsonify({
            'success': True,
            'users': formatted_users
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 结果确认页面API ====================

@app.route('/api/review/images', methods=['GET'])
def api_review_images():
    """获取OK或NOK文件夹的图片列表"""
    folder = request.args.get('folder')
    category = request.args.get('category', 'ok').lower()
    
    if not folder:
        return jsonify({'success': False, 'error': '未指定文件夹'}), 400
    
    if category not in ['ok', 'nok']:
        return jsonify({'success': False, 'error': '无效的分类'}), 400
    
    try:
        folder_name = ok_folder_name if category == 'ok' else nok_folder_name
        folder_path = os.path.join(scan_root, folder, folder_name)
        
        if not os.path.exists(folder_path):
            return jsonify({'success': False, 'error': '文件夹不存在'}), 404
        
        image_list = get_image_list(folder_path, config.get_image_extensions())
        
        return jsonify({
            'success': True,
            'folder': folder,
            'category': category,
            'images': image_list,
            'count': len(image_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/review/image', methods=['GET'])
def api_review_image():
    """获取OK/NOK中的图片"""
    folder = request.args.get('folder')
    category = request.args.get('category', 'ok').lower()
    index = request.args.get('index', 0, type=int)
    thumbnail = request.args.get('thumbnail', 0, type=int)
    
    if not folder:
        return jsonify({'success': False, 'error': '未指定文件夹'}), 400
    
    try:
        folder_name = ok_folder_name if category == 'ok' else nok_folder_name
        folder_path = os.path.join(scan_root, folder, folder_name)
        image_list = get_image_list(folder_path, config.get_image_extensions())
        
        if index < 0 or index >= len(image_list):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        image_name = image_list[index]
        image_path = os.path.join(folder_path, image_name)
        
        if thumbnail:
            # 返回缩略图
            img_base64 = create_thumbnail(image_path, (300, 300))
        else:
            # 返回完整图片
            img_base64, _ = load_and_process_image(
                image_path, rotate=False, show_bbox=False
            )
        
        return jsonify({
            'success': True,
            'image': img_base64,
            'name': image_name,
            'index': index,
            'total': len(image_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 健康检查 ====================

@app.route('/health')
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '页面未找到'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    # 确保必要目录存在
    config.ensure_directories_exist()
    
    # 开发模式运行
    host = config.get_host()
    port = config.get_port()
    
    print(f"应用启动在 http://{host}:{port}")
    print(f"使用配置文件: {config.config_path}")
    print(config.get_config_summary())
    
    app.run(host=host, port=port, debug=True)

