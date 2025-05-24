#!/usr/bin/env python3
"""
梦境之旅游戏启动脚本
使用 uv 运行的 Flask 应用
"""

import os
import sys
from app import app, socketio

def main():
    """主函数"""
    print("🌙 启动梦境之旅游戏...")
    print("📍 访问地址: http://localhost:5001")
    print("🔄 使用 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0', 
            port=5001,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n🛑 游戏服务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 