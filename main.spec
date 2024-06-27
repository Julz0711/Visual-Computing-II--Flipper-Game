# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py', 'endgame.py', 'config.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('data/gameover_bg.png', 'data'),
        ('data/gui_bg_v2.png', 'data'),
        ('data/pause_bg_v2.png', 'data'),
        ('data/pinbolchill.mp3', 'data'),
        ('data/PressStart2P-Regular.ttf', 'data'),
        ('data/theme.json', 'data'),
        ('highscore.txt', '.'),  # Include highscore.txt in the root directory
        ('icon.ico', '.')  # Include icon.ico in the root directory
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon='icon.ico'  # Specify the icon file for the executable
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
