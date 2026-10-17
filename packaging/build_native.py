"""Build a native application from an explicitly supplied pair of wheels."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

parser=argparse.ArgumentParser()
parser.add_argument('--engine-wheel',type=Path,required=True)
parser.add_argument('--studio-wheel',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
wheels=[p.resolve(strict=True) for p in (args.engine_wheel,args.studio_wheel)]
if any(p.suffix!='.whl' for p in wheels):parser.error('Both inputs must be wheel files.')
stage=root/'build'/'wheel-runtime'
# This is exclusively a generated staging directory owned by this build script.
if stage.exists():shutil.rmtree(stage)
stage.mkdir(parents=True)
subprocess.run([sys.executable,'-m','pip','install','--no-deps','--target',str(stage),*[str(p) for p in wheels]],check=True)
env={**os.environ,'PYINSTALLER_CONFIG_DIR':str(root/'.pyinstaller')}
subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm',str(root/'packaging'/'wave-studio.spec')],cwd=root,env=env,check=True)
