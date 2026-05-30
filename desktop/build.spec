"""
Word 引用插入 - PyInstaller 打包配置
生成单一 EXE 文件
"""

import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))

a = Analysis(
    ['main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'win32com',
        'win32com.client',
        'pythoncom',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Word引用插入',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
