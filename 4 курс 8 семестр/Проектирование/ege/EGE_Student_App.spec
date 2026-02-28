# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ege_students_app.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('database', 'database'), ('ui', 'ui'), ('services', 'services'), ('utils', 'utils')],
    hiddenimports=[],
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
    name='EGE_Student_App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\Swifty\\AppData\\Local\\Temp\\c877cbb3-b08c-4924-9b5c-69ca92e7d334',
)
