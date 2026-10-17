# Native onedir application. Build separately on each target operating system.
from pathlib import Path
root = Path(SPECPATH).parent
analysis = Analysis(
    [str(root/'scripts'/'run_app.py')],
    pathex=[str(root/'build'/'wheel-runtime')],
    binaries=[], datas=[], hiddenimports=[],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['matplotlib','cv2','IPython','tkinter','PySide6.QtWebEngineCore','PySide6.QtWebEngineWidgets','PySide6.QtQml','PySide6.QtQuick'],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(pyz,analysis.scripts,[],exclude_binaries=True,name='WaveStudio',debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False)
collection = COLLECT(exe,analysis.binaries,analysis.datas,strip=False,upx=False,name='WaveStudio')
if __import__('sys').platform == 'darwin':
    app = BUNDLE(collection,name='WaveStudio.app',icon=None,bundle_identifier='org.wavestudio.app')
