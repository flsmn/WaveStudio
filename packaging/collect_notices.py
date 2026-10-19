"""Copy available dependency notices into a built bundle; not a license audit."""
import argparse
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil


def collect(bundle):
    output = bundle/'Contents/Resources/ThirdPartyNotices'
    output.mkdir(parents=True, exist_ok=True)
    packages = []
    for name in ('numpy', 'torch', 'PySide6', 'PySide6_Essentials',
                 'PySide6_Addons', 'shiboken6', 'pyqtgraph', 'PyInstaller'):
        distribution = metadata.distribution(name)
        documents = []
        for entry in distribution.files or []:
            if not any(word in str(entry).lower() for word in ('license', 'copying', 'notice')):
                continue
            source = distribution.locate_file(entry)
            if not source.is_file():
                continue
            relative = Path(name, *[part for part in Path(entry).parts if part not in ('.', '..', '/')])
            target = output/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            documents.append(str(relative))
        packages.append({
            'name': name, 'version': distribution.version,
            'license_expression': distribution.metadata.get('License-Expression'),
            'license_metadata': distribution.metadata.get('License'),
            'notice_files': documents,
        })
    (output/'inventory.json').write_text(json.dumps(packages, indent=2)+'\n')
    (output/'README.txt').write_text(
        'Available license/NOTICE files copied from the exact build environment.\n'
        'PyInstaller is a build tool; its bootloader is part of the application.\n'
        'Some distributions, including the installed Qt/PySide wheels, expose license\n'
        'metadata without separate notice files. This collection is incomplete and\n'
        'does not replace the outstanding project/third-party license review.\n'
        'No project license or new permission grant is asserted.\n'
    )
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    if not (args.bundle/'Contents/Info.plist').is_file():
        parser.error('Expected an existing macOS application bundle.')
    print(collect(args.bundle))
