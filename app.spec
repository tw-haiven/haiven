# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Add all your static files and resources here
static_files = [
    ('app/resources/static/out', 'resources/static/out'),
    ('app/config.yaml', '.'),
    ('app/.env', '.'),
    ('app/embeddings', 'embeddings'),
    ('app/knowledge', 'knowledge'),
    ('app/prompts', 'prompts'),
    ('app/llms', 'llms'),
]

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=static_files,
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.protocols',
        'uvicorn.lifespan',
        'uvicorn.protocols.http',
        'fastapi',
        'gradio',
        'gradio_client',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)