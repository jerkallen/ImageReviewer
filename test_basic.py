#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本功能测试脚本
"""
import os
import sys

def test_imports():
    """测试所有模块能否正常导入"""
    print("测试模块导入...")
    try:
        import config_handler
        import database
        import image_handler
        import user_handler
        import generate_cert
        print("✓ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 模块导入失败: {str(e)}")
        return False

def test_config():
    """测试配置处理"""
    print("\n测试配置处理...")
    try:
        from config_handler import get_config_handler
        config = get_config_handler()
        
        # 测试获取配置
        host = config.get_host()
        port = config.get_port()
        root_dir = config.get_root_directory()
        
        print(f"  主机: {host}")
        print(f"  端口: {port}")
        print(f"  根目录: {root_dir}")
        print("✓ 配置处理测试通过")
        return True
    except Exception as e:
        print(f"✗ 配置处理测试失败: {str(e)}")
        return False

def test_database():
    """测试数据库操作"""
    print("\n测试数据库操作...")
    try:
        from database import Database
        
        # 使用临时数据库
        db = Database("test_temp.db")
        
        # 测试用户创建
        user = db.get_or_create_user("192.168.1.100", "测试用户")
        assert user['ip'] == "192.168.1.100"
        assert user['name'] == "测试用户"
        print("  ✓ 用户创建成功")
        
        # 测试操作记录
        op_id = db.log_operation(
            "192.168.1.100", "测试用户", "classify_ok",
            "test.jpg", "project1", "project1/OK"
        )
        assert op_id > 0
        print("  ✓ 操作记录成功")
        
        # 测试撤回记录
        db.add_undo_record(
            "192.168.1.100", "test.jpg", "project1",
            "project1/OK", True, op_id
        )
        undo_records = db.get_undo_records("192.168.1.100")
        assert len(undo_records) > 0
        print("  ✓ 撤回记录成功")
        
        # 测试统计
        stats = db.get_operation_stats()
        assert 'total' in stats
        print("  ✓ 统计查询成功")
        
        # 清理测试数据库
        if os.path.exists("test_temp.db"):
            os.remove("test_temp.db")
        
        print("✓ 数据库操作测试通过")
        return True
    except Exception as e:
        print(f"✗ 数据库操作测试失败: {str(e)}")
        # 清理
        if os.path.exists("test_temp.db"):
            os.remove("test_temp.db")
        return False

def test_image_handler():
    """测试图片处理"""
    print("\n测试图片处理...")
    try:
        from image_handler import scan_project_folders, get_image_list
        
        # 创建测试目录
        test_dir = "test_images"
        os.makedirs(test_dir, exist_ok=True)
        os.makedirs(f"{test_dir}/project1", exist_ok=True)
        
        # 测试扫描文件夹
        folders = scan_project_folders(test_dir)
        assert "project1" in folders
        print("  ✓ 文件夹扫描成功")
        
        # 测试获取图片列表
        image_list = get_image_list(f"{test_dir}/project1")
        assert isinstance(image_list, list)
        print("  ✓ 图片列表获取成功")
        
        # 清理测试目录
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        print("✓ 图片处理测试通过")
        return True
    except Exception as e:
        print(f"✗ 图片处理测试失败: {str(e)}")
        # 清理
        import shutil
        if os.path.exists("test_images"):
            shutil.rmtree("test_images")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n测试目录结构...")
    try:
        required_dirs = [
            "static",
            "static/css",
            "static/js",
            "templates",
            "data",
            "data/images",
            "data/logs"
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                print(f"  ✓ {dir_path}")
            else:
                print(f"  ✗ {dir_path} (不存在)")
                all_exist = False
        
        if all_exist:
            print("✓ 目录结构完整")
        else:
            print("✗ 部分目录缺失")
        
        return all_exist
    except Exception as e:
        print(f"✗ 目录结构测试失败: {str(e)}")
        return False

def test_files():
    """测试必要文件"""
    print("\n测试必要文件...")
    try:
        required_files = [
            "app.py",
            "config.json",
            "config_handler.py",
            "database.py",
            "image_handler.py",
            "user_handler.py",
            "generate_cert.py",
            "run_app.py",
            "requirements.txt",
            "README.md",
            "static/css/style.css",
            "static/js/main.js",
            "static/js/history.js",
            "static/js/review.js",
            "templates/index.html",
            "templates/history.html",
            "templates/review.html"
        ]
        
        all_exist = True
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ {file_path} (不存在)")
                all_exist = False
        
        if all_exist:
            print("✓ 所有必要文件存在")
        else:
            print("✗ 部分文件缺失")
        
        return all_exist
    except Exception as e:
        print(f"✗ 文件测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("="* 60)
    print("图片审查系统 - 基本功能测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("配置处理", test_config),
        ("数据库操作", test_database),
        ("图片处理", test_image_handler),
        ("目录结构", test_directory_structure),
        ("必要文件", test_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name}测试异常: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print("=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！系统准备就绪。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

