# -*- mode: python ; coding: utf-8 -*-

static_files = [
    ('config.yaml', '.'), 
    ('../../haiven-tw-knowledge-pack', 'haiven-tw-knowledge-pack'),
    ('resources', 'resources')
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=static_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# Define the executable block, removing `runtime_tmpdir` or other parameters used for single-file bundles
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compresses the executable using UPX, optional
    upx_exclude=[],
    console=True,  # Set to False if you want a windowless app (e.g., GUI apps)
)

# Collate all data into a single directory structure
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dist_folder',  # Folder name for the distribution
)