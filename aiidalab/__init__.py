#!/usr/bin/env python
import os
import sys
import site
import json
import logging
import pkg_resources
from pathlib import Path
from importlib import import_module
from collections import defaultdict

from IPython.display import display
import ipywidgets as ipw
from markdown import markdown

logger = logging.getLogger(__name__)


__all__ = ['AiidaLab', 'setup']


class AiidaLabApp:

    class InvalidAppDirectory(TypeError):
        pass

    def __init__(self, path):
        self._path = Path(path).resolve()
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
    def path(self):
        return self._path

    def __fspath__(self):
        return str(self.path)

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

        app_base = self.path.relative_to(base)
        if (self.path / 'start.py').exists():
            return self._start_widget_py(app_base=app_base)
        else:
            return self._start_widget_md(app_base=app_base)


class AiidaLab:

    DEFAULT_PATHS = [
        Path.cwd() / 'apps',
        Path(site.USER_BASE, 'apps'),
        Path(sys.prefix, 'apps'),
    ]

    def __init__(self, path=None):
        if path is None:
            env_path = os.getenv('AIIDALAB_APPS')
            if env_path is None:
                self.path = self.DEFAULT_PATHS
            else:
                self.path = [Path(p).expanduser().resolve() for p in env_path.split(':')]
        elif isinstance(path, str):
            self.path = [Path(p).expanduser().resolve() for p in path.split(':')]
        else:
            self.path = [Path(p).expanduser().resolve() for p in path]

    def __repr__(self):
        return f"{type(self).__name__}(path={self.path})"

    def find_apps(self):
        for apps_path in self.path:
            if apps_path.is_dir():
                for app_path in find_app_paths(apps_path):
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


TEXT_FILES = ['*.json', '*.md', '*.html']
PY_FILES = ['*.py', '*.ipynb']
IMG_FILES = ['*.gif', '*.jpg', '*jpeg', '*png']
MOV_FILES = ['*.mpg', '*.mpeg', '*.mp4']


DEFAULT_INCLUDE = TEXT_FILES + PY_FILES + IMG_FILES + MOV_FILES
DEFAULT_EXCLUDE = ['.*']


def _find_app_data_files(app_path, include, exclude, include_hidden):
    for root, dirs, files in os.walk(app_path):
        if not include_hidden:
            for child_dir in dirs:
                if child_dir.startswith('.'):
                    dirs.remove(child_dir)

        for file in files:
            if not include_hidden and file.startswith('.'):
                continue
            file_path = Path(root, file)
            included = include and any(file_path.match(i) for i in include)
            excluded = exclude and any(file_path.match(e) for e in exclude)
            if included and not excluded:
                yield file_path


def find_app_data_files(app_path,  # maybe in the future add:', /'
                        install_path=None,
                        base=None,
                        include=DEFAULT_INCLUDE, exclude=DEFAULT_EXCLUDE,
                        include_hidden=False):
    base = Path.cwd() if base is None else base
    if install_path is None:
        install_path = Path('apps', to_filename(AiidaLabApp(app_path).name))

    # Collect all app-related data files:
    data_files = defaultdict(list)
    for file_path in _find_app_data_files(app_path, include, exclude,
                                          include_hidden):
        dst_directory = file_path.parent.relative_to(app_path)
        data_files[dst_directory].append(file_path)

    # Collate data files by their parent directory
    ret = []
    for parent, files in data_files.items():
        ret.append(
            (str((install_path / parent)),
            [str(p.resolve().relative_to(base)) for p in files]))

    return ret


def show_app_data_files(app_path, **kwargs):
    return find_app_data_files(app_path, '.', app_path, **kwargs)


def find_app_paths(root=None):
    if root is None:
        root = Path.cwd()
    else:
        root = Path(root).resolve()

    metadata_file = root / 'metadata.json'
    start_py = root / 'start.py'
    start_md = root / 'start.md'

    if metadata_file.is_file() and \
            (start_py.is_file() or start_md.is_file()):
        yield root
    else:
        for child in root.iterdir():
            if child.is_dir():
                yield from find_app_paths(child)


def find_apps(root=None):
    for app_path in find_app_paths(root):
        yield AiidaLabApp(app_path)


def get_app_requires(app_path):
    return AiidaLabApp(app_path).metadata.get('requires', [])


def to_filename(name):
    from pkg_resources import to_filename
    return to_filename(name.replace(' ', '_').lower())


def setup(**kwargs):
    """Custom setup function for AiiDA lab distributions."""
    import setuptools

    app_paths = [Path(p) for p in kwargs.pop('apps', [])]
    if app_paths:
        install_requires = kwargs.pop('install_requires', [])
        data_files = kwargs.pop('data_files', [])
        for app_path in app_paths:
            app = AiidaLabApp(app_path)
            install_path = os.path.join('apps', to_filename(app.name))

            install_requires.extend(app.metadata.get('requires', []))
            data_files.extend(find_app_data_files(app.path, install_path))

        kwargs['install_requires'] = list(set(install_requires))
        kwargs['data_files'] = data_files

    return setuptools.setup(**kwargs)
