"""
Word 引用插入 - 独立桌面版入口
通过 PyInstaller 打包为单一 EXE 运行
"""

import sys
import os

# 确保在打包后也能找到模块
if getattr(sys, 'frozen', False):
    # PyInstaller 打包环境
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前目录加入模块搜索路径
sys.path.insert(0, base_dir)

from app import main

if __name__ == "__main__":
    main()
