#!/usr/bin/env python
import sys
import os
import json
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


__all__ = ['AiidaLab']


class AiidaLabApp:

    class InvalidAppDirectory(TypeError):
        pass

    def __init__(self, path):
        self.path = Path(path).resolve()
        self.metadata  # check existance and validity
        start_file = self.path / 'start'
        if not start_file.with_suffix('.md').exists() or \
                start_file.with_suffix('.py').exists():
            raise self.InvalidAppDirectory(f"Start file missing: {start_file}[.py|.md]")

    @property
    def metadata(self):
        metadata_file = self.path / 'metadata.json'
        try:
            return json.loads(metadata_file.read_bytes())
        except FileNotFoundError:
            raise self.InvalidAppDirectory(f"Metadata file missing: '{metadata_file}'")
        except json.decoder.JSONDecodeError:
            raise self.InvalidAppDirectory(f"Ill-formed metadata file: '{metadata_file}'")
        except Exception as error:
            raise self.InvalidAppDirectory(
                f"Unknown error accessing metadata file: {error}") from error

    @property
    def name(self):
        return self.metadata['name']

    def __repr__(self):
        return f"AiidaLabApp(path={self.path})"

    def __str__(self):
        return f"{self.name} [{self.path}]"


class AiidaLab:

    def __init__(self):
        self.path = [Path(p) for p in os.getenv(
            'AIIDALAB_APPS',
            f'{os.getcwd()}/apps:{sys.prefix}/apps').split(':')]

    def find_apps(self):
        for apps_path in self.path:
            for app_path in apps_path.iterdir():
                try:
                    yield AiidaLabApp(app_path)
                except TypeError as error:
                    logger.warning(error)


if __name__ == '__main__':
    aiidalab = AiidaLab()
    apps = list(aiidalab.find_apps())
    if apps:
        print("Installed apps:")
        for app in apps:
            print(f" - {app}")
