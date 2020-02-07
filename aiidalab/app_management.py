import json
import subprocess
from pathlib import Path
from dataclasses import dataclass

from cached_property import cached_property

from .util import is_app_path


class PipAppManager:

    @dataclass
    class PipPackageRecord:
        name: str
        version: str

        @property
        def files(self):
            proc = subprocess.run(['python', '-m', 'pip', 'show',
                                   '-f', self.name], capture_output=True)
            out = proc.stdout.decode()
            lines = out.splitlines()
            location = None
            for i, line in enumerate(lines):
                if line.startswith('Location:'):
                    location = Path(line.split(':')[1].strip())

                if line.startswith('Files:'):
                    assert location is not None
                    files = [location / l.strip() for l in lines[i+1:]]
                    return files
            return []

    @classmethod
    def list_packages(cls, outdated=False):
        args = ['python', '-m', 'pip', 'list', '--format', 'json']
        if outdated:
            args.append('--outdated')
        proc = subprocess.run(args, capture_output=True)
        records = json.loads(proc.stdout.decode())
        return [cls.PipPackageRecord(**record) for record in records]

    def find_app_paths(self, package):
        dirs = {Path(f).parent.resolve() for f in package.files}
        app_paths = [d for d in dirs if is_app_path(d)]
        yield from app_paths


class CondaAppManager:

    def __init__(self, prefix=None):
        if prefix is None:
            from conda.base.context import context
            self.prefix = Path(context.target_prefix)
        else:
            self.prefix = Path(prefix)

    def list_packages(self):
        from conda.core.prefix_data import PrefixData
        from conda.gateways import logging  # noqa monkey-patched
        prefix_data = PrefixData(self.prefix, pip_interop_enabled=True)
        yield from prefix_data.iter_records()

    def find_app_paths(self, package):
        dirs = {(self.prefix / f).parent.resolve() for f in package.files}
        app_paths = [d for d in dirs if is_app_path(d)]
        yield from app_paths

    @cached_property
    def package_map(self):
        return {app_path: package
                for package in self.list_packages()
                for app_path in self.find_app_paths(package)}
