# Native onedir application. Build separately on each target operating system.
from pathlib import Path
import tomllib
root = Path(SPECPATH).parent
app_version = tomllib.loads((root/'pyproject.toml').read_text())['project']['version']
analysis = Analysis(
    [str(root/'scripts'/'run_app.py')],
    pathex=[str(root/'build'/'wheel-runtime')],
    binaries=[], datas=[(str(p),'wave_studio/data/examples') for p in (root/'build'/'wheel-runtime'/'wave_studio'/'data'/'examples').glob('*.json')], hiddenimports=[],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['torchvision','torchaudio','matplotlib','scipy','cv2','IPython','tkinter','PySide6.QtWebEngineCore','PySide6.QtWebEngineWidgets','PySide6.QtQml','PySide6.QtQuick'],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(pyz,analysis.scripts,[],exclude_binaries=True,name='WaveStudio',debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False)
collection = COLLECT(exe,analysis.binaries,analysis.datas,strip=False,upx=False,name='WaveStudio')
if __import__('sys').platform == 'darwin':
    app = BUNDLE(
        collection,name='WaveStudio.app',icon=None,bundle_identifier='org.wavestudio.app',
        version=app_version,
        info_plist={'CFBundleShortVersionString':app_version,'CFBundleVersion':app_version,
                    'LSMinimumSystemVersion':'26.0','NSHighResolutionCapable':True},
    )
