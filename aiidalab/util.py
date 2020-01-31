import json
import subprocess
from pathlib import Path


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


def list_packages():
    proc = subprocess.run(['python', '-m', 'pip', 'list',
                           '--format', 'json'], capture_output=True)
    return json.loads(proc.stdout.decode())


def fmt_data_files_for_setup_cfg(data_files):
    yield "[options.data_files]"
    for root, files in data_files:
        if len(files) == 1:
            yield f"{root} = {files[0]}"
        else:
            yield f"{root} ="
            for fn in files:
                yield f"  {fn}"
