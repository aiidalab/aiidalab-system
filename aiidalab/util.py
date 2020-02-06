import sys
import json
import subprocess
from pathlib import Path
from functools import lru_cache
from contextlib import contextmanager

from tqdm import tqdm
from watchdog.observers import Observer


__all__ = ['fmt_data_files_for_setup_cfg']


def is_app_path(path):
    metadata_file = path / 'metadata.json'
    start_py = path / 'start.py'
    start_md = path / 'start.md'
    return metadata_file.is_file() and \
        (start_py.is_file() or start_md.is_file())


def find_app_paths_for_package(name):
    proc = subprocess.run(['python', '-m', 'pip', 'show',
                           '-f', name], capture_output=True)
    out = proc.stdout.decode()
    lines = out.splitlines()
    location = None
    for i, line in enumerate(lines):
        if line.startswith('Location:'):
            location = Path(line.split(':')[1].strip())

        if line.startswith('Files:'):
            assert location is not None
            files = [location / l.strip() for l in lines[i+1:]]
            dirs = {f.parent.resolve() for f in files}
            return [d for d in dirs if is_app_path(d)]
    return []


def list_packages(outdated=False):
    args = ['python', '-m', 'pip', 'list', '--format', 'json']
    if outdated:
        args.append('--outdated')
    proc = subprocess.run(args, capture_output=True)
    return json.loads(proc.stdout.decode())


def _read_package_cache():
    try:
        with open(Path.home() / 'aiidalab_package_cache.json') as file:
            return json.load(file)
    except FileNotFoundError:
        return dict()


def _read_and_update_package_cache():
    cache = _read_package_cache()

    # Generate requirements-style package names.
    packages = [p['name'] + '==' + p['version'] for p in list_packages()]

    # Remove packages from cache that are no longer installed.
    to_delete_from_cache = {pkg for pkg in cache if pkg not in packages}
    for pkg in to_delete_from_cache:
        del cache[pkg]

    # Update the app paths for each installed package.
    to_update = [pkg for pkg in packages if pkg not in cache]
    if len(to_update) > 10:
        to_update = tqdm(to_update, 'update-package-cache')
    for package in to_update:
        if package not in cache:
            paths = find_app_paths_for_package(package.split('==')[0])
            cache[package] = [str(p) for p in paths]

    # Write the updated cache file to disk.
    serialized_cache = json.dumps(cache)
    with open(Path.home() / 'aiidalab_package_cache.json', 'w') as file:
        file.write(serialized_cache)

    return cache


@contextmanager
def package_cache():

    @lru_cache
    def mem_cached_package_cache():
        return _read_and_update_package_cache()

    def event_handler(*args, **kwargs):
        print(args, kwargs)
        mem_cached_package_cache.cache_clear()

    # setup file system observer
    observer = Observer()
    for path in sys.path:
        if Path(path).is_dir():
            observer.schedule(event_handler, path)

    class Cache:
        
        @staticmethod
        def find_package(app):
            cache = mem_cached_package_cache()
            pkg_table = {Path(p): pkg
                         for pkg, paths in cache.items() for p in paths}
            return pkg_table.get(app.path)

    observer.start()
    try:
        yield Cache
    finally:
        observer.stop()
        observer.join()


def fmt_data_files_for_setup_cfg(data_files):
    yield "[options.data_files]"
    for root, files in data_files:
        if len(files) == 1:
            yield f"{root} = {files[0]}"
        else:
            yield f"{root} ="
            for fn in files:
                yield f"  {fn}"
