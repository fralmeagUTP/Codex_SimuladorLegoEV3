# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('simulador_ev3')


def _collect_tk_binaries():
    """Incluye las DLL de Tcl/Tk cuando Python procede de Conda o venv."""
    base = Path(sys.base_prefix)
    candidates = (base / 'Library' / 'bin', base / 'DLLs', base)
    binaries = []
    for name in ('tcl86t.dll', 'tk86t.dll'):
        source = next((directory / name for directory in candidates if (directory / name).is_file()), None)
        if source is not None:
            binaries.append((str(source), '.'))
    return binaries


def _collect_conda_runtime_binaries():
    """Incluye DLL transitivas que Conda instala fuera de ``DLLs``."""
    library_bin = Path(sys.base_prefix) / 'Library' / 'bin'
    if not library_bin.is_dir():
        return []
    return [(str(path), '.') for path in library_bin.glob('*.dll')]


runtime_binaries = _collect_tk_binaries() + _collect_conda_runtime_binaries()


a = Analysis(
    ['simulador_ev3\\ui\\main_window.py'],
    pathex=[],
    binaries=runtime_binaries,
    datas=[('simulador_ev3\\assets', 'simulador_ev3\\assets')],
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='SimuladorEV3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=True,
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
    name='SimuladorEV3',
)
