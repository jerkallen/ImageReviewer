import os
import sys
import datetime
import traceback
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_certificates():
    """使用Python的cryptography库生成自签名SSL证书"""
    print("正在生成自签名SSL证书...")
    
    try:
        # 创建certs目录
        os.makedirs("certs", exist_ok=True)
        print(f"证书目录: {os.path.abspath('certs')}")
        
        # 生成证书和密钥的路径
        key_path = os.path.join("certs", "server.key")
        cert_path = os.path.join("certs", "server.crt")
        
        # 检查证书是否已存在
        if os.path.exists(key_path) and os.path.exists(cert_path):
            print("证书已存在。如需重新生成，请先删除certs目录中的文件。")
            return True
        
        # 生成私钥
        print("正在生成RSA私钥...")
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            print("私钥生成成功")
        except Exception as e:
            print(f"生成私钥时出错: {str(e)}")
            traceback.print_exc()
            return False
        
        # 生成证书
        print("正在生成自签名证书...")
        try:
            # 设置证书主题和发行者
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, u"CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"State"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Organization"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"Unit"),
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
            ])
            
            # 创建证书
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                # 有效期10年
                datetime.datetime.utcnow() + datetime.timedelta(days=3650)
            ).add_extension(
                x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            print("证书生成成功")
        except Exception as e:
            print(f"生成证书时出错: {str(e)}")
            traceback.print_exc()
            return False
        
        # 将私钥写入文件
        try:
            print("正在保存私钥...")
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            print(f"私钥已保存至: {os.path.abspath(key_path)}")
        except Exception as e:
            print(f"保存私钥时出错: {str(e)}")
            traceback.print_exc()
            return False
        
        # 将证书写入文件
        try:
            print("正在保存证书...")
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            print(f"证书已保存至: {os.path.abspath(cert_path)}")
        except Exception as e:
            print(f"保存证书时出错: {str(e)}")
            traceback.print_exc()
            return False
        
        print("证书和私钥生成完成")
        return True
        
    except Exception as e:
        print(f"生成证书时出错: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = generate_certificates()
        print(f"证书生成{'成功' if success else '失败'}")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"运行脚本时发生错误: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

