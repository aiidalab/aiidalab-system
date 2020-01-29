#!/usr/bin/env python
import sys
import os
import json
import logging
from pathlib import Path
from importlib import import_module

from IPython.display import display
import ipywidgets as ipw
from markdown import markdown

logger = logging.getLogger(__name__)


__all__ = ['AiidaLab']


class AiidaLabApp:

    class InvalidAppDirectory(TypeError):
        pass

    def __init__(self, path):
        self.path = Path(path).resolve()
        if not self.path.is_dir():
            raise self.InvalidAppDirectory(
                f"App path is not a directory: {self.path}")
        self.metadata  # check existance and validity
        start_file = self.path / 'start'
        if not start_file.with_suffix('.md').exists() or \
                start_file.with_suffix('.py').exists():
            raise self.InvalidAppDirectory(
                f"Start file missing: {start_file}[.py|.md]")

    @property
    def metadata(self):
        metadata_file = self.path / 'metadata.json'
        try:
            return json.loads(metadata_file.read_bytes())
        except FileNotFoundError:
            raise self.InvalidAppDirectory(
                f"Metadata file missing: '{metadata_file}'")
        except json.decoder.JSONDecodeError:
            raise self.InvalidAppDirectory(
                f"Ill-formed metadata file: '{metadata_file}'")
        except Exception as error:
            raise self.InvalidAppDirectory(
                f"Unknown error accessing metadata file: {error}") from error

    @property
    def name(self):
        return self.metadata['name']

    def __repr__(self):
        return f"AiidaLabApp(path={self.path})"

    def __str__(self):
        return f"<{self.name} [{self.path}]>"

    def check_dependencies(self):
        import pkg_resources
        requires = pkg_resources.parse_requirements(
            self.metadata.get('requires', []))
        ws = pkg_resources.working_set
        for req in requires:
            match = ws.find(req)
            if match is None:
                logger.warning(f"Requirement '{req}' for {self} not met!")

    def _start_widget_py(self, app_base):
        start_py = self.path / 'start.py'
        mod = import_module(start_py)
        start = mod.get_start_widget()
        return start.get_start_widget(app_base=app_base)

    def _start_widget_md(self, app_base):
        start_md = self.path / 'start.md'
        html = markdown(start_md.read_text())
        html = html.replace('<a ', '<a target="_blank" ')
        return ipw.HTML(html.format(app_base=app_base))

    def start_widget(self, base):
        self.check_dependencies()

        app_base = Path(os.path.relpath(self.path, base))
        if (self.path / 'start.py').exists():
            return self._start_widget_py(app_base=app_base)
        else:
            return self._start_widget_md(app_base=app_base)


class AiidaLab:

    def __init__(self, path=None):
        if path is None:
            path = [Path(p) for p in os.getenv(
                'AIIDALAB_APPS',
                f'{os.getcwd()}/apps:{sys.prefix}/apps').split(':')]
        self.path = path

    def __repr__(self):
        return f"{type(self).__name__}(path='{self.path}')"

    def find_apps(self):
        for apps_path in self.path:
            if apps_path.is_dir():
                for app_path in apps_path.iterdir():
                    try:
                        yield AiidaLabApp(app_path)
                    except TypeError as error:
                        logger.warning(error)

    def home_widget(self, base=None):
        if base is None:
            base = os.getcwd()
        widgets = [app.start_widget(base=base) for app in self.find_apps()]
        return ipw.VBox(children=widgets)

    def _ipython_display_(self):
        display(self.home_widget())


if __name__ == '__main__':
    aiidalab = AiidaLab()
    apps = list(aiidalab.find_apps())
    if apps:
        print("Installed apps:")
        for app in apps:
            print(f" - {app}")
