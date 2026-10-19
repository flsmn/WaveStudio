"""Read-only build-target and license-evidence inventory; no release certification."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import struct
import sys


def version_string(value):
    return f'{value >> 16}.{(value >> 8) & 255}.{value & 255}'


def macho_headers(path):
    """Read load commands directly; distinguish minimum target from SDK version."""
    with path.open('rb') as stream:
        magic = stream.read(4)
        if magic in (b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe'):
            slices = [(0, '<', magic == b'\xcf\xfa\xed\xfe')]
        elif magic in (b'\xfe\xed\xfa\xcf', b'\xfe\xed\xfa\xce'):
            slices = [(0, '>', magic == b'\xfe\xed\xfa\xcf')]
        elif magic in (b'\xca\xfe\xba\xbe', b'\xca\xfe\xba\xbf'):
            count = struct.unpack('>I', stream.read(4))[0]
            if count > 64:
                return []
            wide = magic == b'\xca\xfe\xba\xbf'
            slices = []
            for _ in range(count):
                fields = struct.unpack('>IIQQII' if wide else '>IIIII', stream.read(32 if wide else 20))
                slices.append((fields[2], '<', True))
        else:
            return []
        result = []
        for offset, endian, wide in slices:
            stream.seek(offset)
            header = stream.read(32 if wide else 28)
            fields = struct.unpack(endian+('8I' if wide else '7I'), header)
            cpu, commands = fields[1], fields[4]
            target = {'architecture': {0x100000C: 'arm64', 0x1000007: 'x86_64', 12: 'arm', 7: 'x86'}.get(cpu, hex(cpu))}
            for _ in range(commands):
                command, size = struct.unpack(endian+'II', stream.read(8))
                if size < 8 or size > 1024*1024:
                    raise ValueError('Invalid Mach-O load-command length.')
                data = stream.read(size-8)
                if command == 0x32:  # LC_BUILD_VERSION
                    system, minimum, sdk = struct.unpack(endian+'III', data[:12])
                    target.update(platform=system, minimum_os=version_string(minimum), sdk=version_string(sdk))
                elif command == 0x24:  # LC_VERSION_MIN_MACOSX
                    minimum, sdk = struct.unpack(endian+'II', data[:8])
                    target.update(platform=1, minimum_os=version_string(minimum), sdk=version_string(sdk))
            result.append(target)
        return result


def package_evidence(name, role):
    distribution = metadata.distribution(name)
    documents = []
    for entry in distribution.files or []:
        if not any(word in str(entry).lower() for word in ('license', 'copying', 'notice')):
            continue
        path = distribution.locate_file(entry)
        if path.is_file():
            documents.append({'path': str(entry), 'bytes': path.stat().st_size,
                              'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return {'name': name, 'version': distribution.version, 'role': role,
            'metadata_license_expression': distribution.metadata.get('License-Expression'),
            'metadata_license_heading': (distribution.metadata.get('License') or '').splitlines()[:1],
            'local_license_documents': documents}


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=root/'dist/WaveStudio.app')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.bundle.is_dir():
        raise ValueError('The actual Mac application bundle must exist.')
    report = {'platform': platform.platform(), 'python': sys.version.split()[0],
              'bundle': str(args.bundle.resolve()), 'binary_targets': [], 'packages': [],
              'release_accepted': False,
              'scope': 'Static targets in the existing bundle and selected installed distribution license evidence. Not a clean-Mac run, complete transitive license audit, or a legal conclusion.'}
    seen = set()
    for path in sorted(args.bundle.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        inode = (path.stat().st_dev, path.stat().st_ino)
        if inode in seen:
            continue
        seen.add(inode)
        headers = macho_headers(path)
        if headers:
            report['binary_targets'].append({'path': str(path.relative_to(args.bundle)), 'slices': headers})
    minimums = [tuple(map(int, header['minimum_os'].split('.')))
                for binary in report['binary_targets'] for header in binary['slices']
                if header.get('platform') == 1 and header['architecture'] == 'arm64' and 'minimum_os' in header]
    report['highest_declared_arm64_macos_target'] = '.'.join(map(str, max(minimums))) if minimums else None
    report['architectures'] = sorted({h['architecture'] for binary in report['binary_targets'] for h in binary['slices']})
    for name in ['numpy', 'torch', 'PySide6', 'PySide6_Essentials', 'PySide6_Addons', 'shiboken6', 'pyqtgraph']:
        report['packages'].append(package_evidence(name, 'runtime environment; exact bundled content must be matched at final build'))
    report['packages'].append(package_evidence('pyinstaller', 'build only'))
    try:
        report['packages'].append(package_evidence('scipy', 'validation only; not a production dependency'))
    except metadata.PackageNotFoundError:
        pass
    report['repository_license_files'] = {}
    for name, repo in [('Studio', root), ('Engine', root.parent/'WaveSimulator2D')]:
        report['repository_license_files'][name] = [str(p.relative_to(repo)) for p in repo.iterdir()
            if p.is_file() and p.name.lower().startswith(('license', 'licence', 'copying', 'notice'))]
    report['open_items'] = [
        'Confirm project/fork redistribution license or permission; no top-level license file found in the current repositories.',
        'Complete Qt and transitive bundled-library license/notice collection and required distribution material.',
        'Choose supported minimum macOS from static targets plus a real clean-machine test; static headers alone do not establish compatibility.',
        'Decide public signing/notarization, distribution and update procedure before public delivery.',
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'mach_o_files': len(report['binary_targets']),
                      'architectures': report['architectures'],
                      'highest_declared_arm64_macos_target': report['highest_declared_arm64_macos_target'],
                      'repository_license_files': report['repository_license_files'],
                      'release_accepted': False}, indent=2))


if __name__ == '__main__':
    main()
