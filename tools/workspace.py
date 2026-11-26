#!/usr/bin/env python3
"""Small GitHub-backed working copy. Standard library + Git only; no application changes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / 'workspace.lock.json'
CACHE = Path.home() / '.cache' / 'keepit-workspace'
GITDIR = CACHE / 'repository.git'
BASE_PATTERNS = ['/*', '!/*/', '/Keepit-OCR/', '!/Keepit-OCR/vendor/', '/Plan/', '/tools/']
GROUP_PATHS = {'ocr-assets': '/Keepit-OCR/vendor/', 'original': '/Keep-it/'}


def lock():
    data = json.loads(LOCK_PATH.read_text())
    if data.get('schema') != 1 or not re.fullmatch(r'[0-9a-f]{40}', data['sourceCommit']):
        raise RuntimeError('Invalid workspace lock')
    for entry in data['files']:
        path = Path(entry['path'])
        if path.is_absolute() or '..' in path.parts or '.git' in path.parts:
            raise RuntimeError('Unsafe locked path')
    return data


def git(*args, capture=True):
    command = ['git', '--git-dir=' + str(GITDIR), '--work-tree=' + str(ROOT), *args]
    return subprocess.check_output(command, text=True).strip() if capture else subprocess.check_call(command)


def blob_hash(path):
    digest = hashlib.sha1()
    digest.update(('blob ' + str(path.stat().st_size) + '\0').encode())
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verify(group, missing_ok=False):
    entries = [e for e in lock()['files'] if group == 'all' or e['group'] == group]
    missing, modified = [], []
    for e in entries:
        p = ROOT / e['path']
        if not p.is_file():
            missing.append(e['path'])
        elif p.is_symlink() or blob_hash(p) != e['blob']:
            modified.append(e['path'])
    if modified or (missing and not missing_ok):
        raise RuntimeError('Verification stopped. Modified: ' + ', '.join(modified[:12]) +
                           '; missing: ' + ', '.join(missing[:12]))
    return len(entries) - len(missing), len(missing)


def ensure_repo():
    data = lock()
    if not (GITDIR / 'HEAD').exists():
        if (ROOT / '.git').is_dir():
            raise RuntimeError('Existing root Git directory: refusing to replace it')
        CACHE.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(['git', 'init', '--bare', '-q', str(GITDIR)])
        git('config', 'core.bare', 'false')
        git('config', 'core.worktree', str(ROOT))
        git('config', 'remote.origin.url', data['repository'])
        git('config', 'remote.origin.promisor', 'true')
        git('config', 'remote.origin.partialclonefilter', 'blob:none')
        git('fetch', '--filter=blob:none', '--depth=1', 'origin', 'main', capture=False)
        git('update-ref', 'refs/heads/main', 'FETCH_HEAD')
        git('symbolic-ref', 'HEAD', 'refs/heads/main')
        git('read-tree', 'HEAD')
        # These flags prepare sparse checkout without initially materializing all blobs.
        git('config', 'core.sparseCheckout', 'true')
        git('config', 'core.sparseCheckoutCone', 'false')
        git('config', 'index.sparse', 'false')
        git('config', 'user.name', 'Arena')
        git('config', 'user.email', 'arena@local.invalid')
    (ROOT / '.git').write_text('gitdir: ' + str(GITDIR) + '\n')


def selected_groups():
    if (GITDIR / 'info' / 'sparse-checkout').exists():
        patterns = (GITDIR / 'info' / 'sparse-checkout').read_text().splitlines()
        return {g for g, pattern in GROUP_PATHS.items() if pattern in patterns}
    return {g for g, pattern in GROUP_PATHS.items() if (ROOT / pattern.strip('/')).exists()}


def select(groups):
    patterns = BASE_PATTERNS + [GROUP_PATHS[g] for g in sorted(groups)]
    subprocess.run(['git', '--git-dir=' + str(GITDIR), '--work-tree=' + str(ROOT),
                    'sparse-checkout', 'set', '--no-cone', '--stdin'],
                   input='\n'.join(patterns) + '\n', text=True, check=True)


def hydrate(group):
    ensure_repo()
    groups = set(GROUP_PATHS) if group == 'all' else {group}
    # Sparse checkout obtains files via Git. Require the exact locked blobs, not mutable URLs.
    for g in groups:
        for e in lock()['files']:
            if e['group'] == g and git('rev-parse', 'HEAD:' + e['path']) != e['blob']:
                raise RuntimeError('HEAD differs from the asset lock: ' + e['path'] +
                                   '. Review/update the lock before downloading.')
        verify(g, missing_ok=True)  # Never overwrite locally edited materialized assets.
    select(selected_groups() | groups)
    for g in groups:
        count, _ = verify(g)
        print('Hydrated and hash-verified:', g, count, 'files')


def evict(group):
    ensure_repo()
    groups = set(GROUP_PATHS) if group == 'all' else {group}
    tracked = {e['path'] for e in lock()['files']}
    for g in groups:
        verify(g, missing_ok=True)
        folder = ROOT / GROUP_PATHS[g].strip('/')
        if (folder / '.git').exists():
            raise RuntimeError('Nested Git history must be archived before evicting ' + str(folder))
        if folder.exists():
            for p in folder.rglob('*'):
                if p.is_file() and p.relative_to(ROOT).as_posix() not in tracked:
                    raise RuntimeError('Untracked file would be lost; refusing eviction: ' + str(p))
    select(selected_groups() - groups)
    for g in groups:
        folder = ROOT / GROUP_PATHS[g].strip('/')
        if folder.exists() and any(p.is_file() for p in folder.rglob('*')):
            raise RuntimeError('Git retained files; inspect instead of deleting forcibly: ' + str(folder))
        print('Evicted verified local copy; GitHub copy retained:', g)


def status():
    data = lock()
    print('Repository:', data['repository'])
    print('Locked source:', data['sourceCommit'], '| app', data['appVersion'])
    print('Local Git metadata:', GITDIR, '(rebuildable cache, excluded from Arena snapshots)')
    total = 0
    for g in ['working', 'ocr-assets', 'original']:
        entries = [e for e in data['files'] if e['group'] == g]
        present = [e for e in entries if (ROOT / e['path']).is_file()]
        size = sum((ROOT / e['path']).stat().st_size for e in present)
        total += size
        print(f'{g}: {len(present)}/{len(entries)} files present, {size / 1048576:.2f} MiB')
    print(f'Locked files currently materialized: {total / 1048576:.2f} MiB')
    print('Thin checkout is NOT a runnable/packagable extension until ocr-assets are hydrated.')


def pack(output, evict_after):
    hydrate('ocr-assets')
    # Code may intentionally differ while developing, but all locked app paths must exist.
    paths = sorted({e['path'] for e in lock()['files'] if e['path'].startswith('Keepit-OCR/')} |
                   set(git('ls-files', '--', 'Keepit-OCR/').splitlines()))
    for name in paths:
        p = ROOT / name
        if not p.is_file() or p.is_symlink():
            raise RuntimeError('Missing or unsafe app file: ' + name)
    version = json.loads((ROOT / 'Keepit-OCR/manifest.json').read_text())['version']
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}', version):
        raise RuntimeError('Unsafe app version')
    destination = Path(output).resolve() if output else CACHE / 'packages' / f'Keepit - Optimize Test-v{version}.zip'
    if destination.exists():
        raise RuntimeError('Refusing to overwrite existing package: ' + str(destination))
    if destination.is_relative_to(ROOT):
        raise RuntimeError('Keep packages outside Workspace: use a cache path')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix('.zip.part')
    try:
        with zipfile.ZipFile(temporary, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in paths:
                rel = Path(name).relative_to('Keepit-OCR').as_posix()
                if '.git' in Path(rel).parts or Path(rel).suffix.lower() in {'.pem', '.key', '.zip', '.log', '.pyc'}:
                    raise RuntimeError('Disallowed packaging path: ' + rel)
                archive.write(ROOT / name, rel)
        with zipfile.ZipFile(temporary) as archive:
            assert archive.testzip() is None
            assert {'manifest.json', 'AGENTS.md', 'PROJECT.md'} <= set(archive.namelist())
            assert len(archive.namelist()) == len(paths)
        temporary.rename(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    print('Created full offline package:', destination)
    print('SHA256:', hashlib.sha256(destination.read_bytes()).hexdigest())
    if evict_after:
        evict('ocr-assets')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('status')
    for cmd in ['hydrate', 'evict', 'verify']:
        p = subs.add_parser(cmd)
        p.add_argument('group', choices=['ocr-assets', 'original', 'all'] if cmd != 'verify' else ['working', 'ocr-assets', 'original', 'all'])
    subs.add_parser('bootstrap')
    p = subs.add_parser('pack')
    p.add_argument('--output')
    p.add_argument('--evict', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'status':
            status()
        elif args.command == 'bootstrap':
            ensure_repo()
            select(selected_groups())
            print('Sparse partial-clone metadata is ready.')
        elif args.command == 'hydrate':
            hydrate(args.group)
        elif args.command == 'evict':
            evict(args.group)
        elif args.command == 'verify':
            print('Verified:', verify(args.group))
        else:
            pack(args.output, args.evict)
    except (RuntimeError, subprocess.CalledProcessError, OSError, AssertionError) as error:
        print('STOP:', error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
