# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('backend', 'backend'), ('constants', 'constants'), ('database', 'database'), ('frontend', 'frontend'), ('env', 'env')],
    hiddenimports=['PyQt6.uic', 'uuid', 'dateutil', 'dateutil.parser', 'sortedcontainers', 'cassandra', 'sqlite3', 'cryptography', 'cryptography.hazmat.primitives.padding', 'PyQt6.QtSql'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CassTl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CassTl',
)
