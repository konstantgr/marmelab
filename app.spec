# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

data_files = [
    ('.\\pyqt_app\\assets\\*.png', '.\\pyqt\\assets'),
    ('.\\pyqt_app\\assets\\*.svg', '.\\pyqt\\assets'),
    ('.\\src\\icons\\*.png', '.\\src\\icons'),
    ('.\\src\\views\\description\\*.html', '.\\src\\views\\description'),
    ('.\\src\\icons\\*.svg', '.\\src\\icons'),
    ('.\\src\\views\\PScannerVisualizers\\assets\\*.stl', '.\\src\\views\\PScannerVisualizers\\assets\\'),
    ('.\\src\\project\\PObjects\\assets\\*.stl', '.\\src\\project\\PObjects\\assets\\') 

]

a = Analysis(
    ['pyqt_app\\app.py'],
    pathex=['.', 'src', 'pyqt_app'],
    binaries=[],
    datas=data_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
