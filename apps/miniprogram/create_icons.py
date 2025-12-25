#!/usr/bin/env python3
"""
创建微信小程序TabBar占位图标
使用PIL/Pillow库生成纯色PNG图标
"""

from PIL import Image
import os

def create_icon(filename, color, size=(81, 81)):
    """创建纯色图标"""
    # 将hex颜色转换为RGB
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

    # 创建图像
    img = Image.new('RGB', size, rgb)

    # 保存
    filepath = os.path.join('images', filename)
    img.save(filepath, 'PNG')
    print(f"✅ 创建: {filepath} (颜色: #{color.upper()})")

def main():
    print("🎨 开始创建TabBar图标...\n")

    # 创建images目录
    os.makedirs('images', exist_ok=True)

    # 定义图标配置
    icons = [
        ('home.png', '7A7E83'),           # 灰色
        ('home-active.png', '667eea'),     # 紫色
        ('profile.png', '7A7E83'),         # 灰色
        ('profile-active.png', '667eea'),  # 紫色
    ]

    # 创建所有图标
    for filename, color in icons:
        create_icon(filename, color)

    print("\n🎉 所有图标创建完成！")
    print("\n📋 图标列表:")

    # 列出创建的文件
    for filename, _ in icons:
        filepath = os.path.join('images', filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  - {filename} ({size} bytes)")

    print("\n⚠️  注意: 这些是纯色占位图，仅用于测试")
    print("建议从以下网站下载专业图标:")
    print("  - https://www.iconfont.cn/")
    print("  - https://iconmonstr.com/")
    print("  - https://www.flaticon.com/")
    print("\n✅ 现在可以在微信开发者工具中编译运行了！")

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print("❌ 缺少PIL/Pillow库")
        print("\n请安装: pip install Pillow")
        print("或使用: pip3 install Pillow")
