#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片审查系统 - 应用启动脚本
支持HTTP和HTTPS模式
"""
import sys
import os
import ssl
from config_handler import get_config_handler
import generate_cert

def main():
    """主函数"""
    # 获取配置
    config = get_config_handler()
    
    # 确保必要目录存在
    config.ensure_directories_exist()
    
    # 获取主机和端口
    host = config.get_host()
    port = config.get_port()
    
    # 打印配置摘要
    print("="* 60)
    print("图片审查系统启动")
    print("=" * 60)
    print(config.get_config_summary())
    print("=" * 60)
    
    # 检查是否启用HTTPS
    use_https = True  # 默认使用HTTPS
    
    if len(sys.argv) > 1 and sys.argv[1] == '--no-https':
        use_https = False
        print("\n注意：以HTTP模式启动（不安全）")
    
    # 导入Flask应用
    from app import app
    
    if use_https:
        # HTTPS模式
        print("\n启动模式：HTTPS")
        
        # 确保证书存在
        cert_dir = "certs"
        cert_file = os.path.join(cert_dir, "server.crt")
        key_file = os.path.join(cert_dir, "server.key")
        
        if not os.path.exists(cert_file) or not os.path.exists(key_file):
            print("\n未找到SSL证书，正在生成...")
            if not generate_cert.generate_certificates():
                print("\n错误：无法生成SSL证书")
                print("您可以使用 --no-https 参数以HTTP模式启动")
                sys.exit(1)
        else:
            print(f"\n找到现有证书:")
            print(f"- 证书: {os.path.abspath(cert_file)}")
            print(f"- 密钥: {os.path.abspath(key_file)}")
        
        # 创建SSL上下文
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_file, key_file)
            
            print(f"\n应用启动在 https://{host}:{port}")
            print(f"\n浏览器访问: https://localhost:{port}")
            print("注意：首次访问时，浏览器可能会警告证书不受信任，这是正常的（因为是自签名证书）")
            print("请在浏览器中选择\"继续访问\"或\"高级\" -> \"继续前往\"")
            print("\n按 Ctrl+C 停止服务器")
            print("=" * 60)
            
            # 启动应用
            app.run(
                host=host,
                port=port,
                ssl_context=context,
                debug=False,
                threaded=True
            )
        except Exception as e:
            print(f"\n错误：启动HTTPS服务器失败: {str(e)}")
            print("\n您可以使用 --no-https 参数以HTTP模式启动")
            sys.exit(1)
    else:
        # HTTP模式
        print("\n启动模式：HTTP（不安全）")
        print(f"\n应用启动在 http://{host}:{port}")
        print(f"\n浏览器访问: http://localhost:{port}")
        print("\n按 Ctrl+C 停止服务器")
        print("=" * 60)
        
        # 启动应用
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n错误：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

