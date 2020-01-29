import os
from pathlib import Path
from itertools import chain


def _find_files(directory, include, exclude):
    for root, dirs, files in os.walk(directory):
        for dir_ in dirs:
            if dir_.startswith('.'):
                dirs.remove(dir_)
        for file in files:
            file_path = (Path(root) / file).relative_to(directory)
            included = include and any(file_path.match(i) for i in include)
            excluded = exclude and any(file_path.match(e) for e in exclude)
            if included and not excluded:
                yield file_path


def find_apps(
        include=['*.ipynb', '*.md', '*.py', '*.json'],
        exclude=['.*']):
    cwd = Path.cwd()
    for directory in chain([cwd], cwd.iterdir()):
        metadata_file = directory / 'metadata.json'
        start_py = directory / 'start.py'
        start_md = directory / 'start.md'

        if metadata_file.is_file() and \
                (start_py.is_file() or start_md.is_file()):
            files = _find_files(directory, include, exclude)
            yield directory.relative_to(cwd), files
