# README

## About

Provides the aiidalab Python package, which allows users and administrators to manage an AiiDA lab instance.
Specifically, the management of AiiDA lab appliacations.

## Installation

To install this package, download or clone it, and then execute

    $ python -m pip install .

within the repository root directory.

## Quickstart

You can list the installed apps with:

```python
>>> from aiidalab import AiidaLab
>>> lab = AiidaLab()
>>> for app in lab.find_apps():
...     print(app)
... 
<App I [.../app_i]>
<My App [.../my_app]>
<My App II [.../my_app_ii]>
```

To launch an AiiDA lab instance in a Jupyter notebook, start the notebook and then excute:

```python
from aiidalab import AiidaLab

lab = AiidaLab()
lab  # equivalent to display(lab.home_widget())
```

See also the `home.ipynb` notebook included with this repository.

## Command line interface

The AiiDA lab system application is intended to be executed programatically from within a Jupyter notebook, but you can use the `aiidalab` command application to perform certain operations directly from the command line.
For example:
```bash
~$ aiidalab list
AiidaLab(path=[PosixPath('/home/sadorf/apps'), PosixPath('/home/sadorf/.local/apps'), PosixPath('/home/sadorf/miniconda3/envs/test/apps')])
Installed apps:
- <My Multi App I [.../my_multi_app_i]>
- <My Multi App II [.../my_multi_app_ii]>
```

## Design Philosophy

An AiiDA lab application is considered to be a user-facing frontend appliaction that is to be executed using the Jupyter web framework.
Specifically, it is assumed that an application provides a widget that is used as an entry point to the application.
This widget can either be an `ipywidgets` widget or simply a static text file in Markdown format that is rendered as HTML.
Furthermore, every AiiDA lab application must have a metadata file (`metadata.json`) that describes the name and purpose of the application to make it discoverable, e.g., through an AiiDA lab app registry.

## Architecture

Every AiiDA lab application is stored in one directory and is identified through the presence of

  1. a `metadata.json` file, and
  2. either a `start.py` Python module or a `start.md` markdown-formatted text file
  
in the app root directory.

An AiiDA lab instance finds applications by searching for directories that match the definition above in the following locations:

  1. an `apps/` folder within the current working directory,
  2. an `apps/` folder within the directory provided by `site.USER_SITE`,
  3. an `apps/` folder within the directory provided by `sys.prefix`,

Alternatively, the instance will search for applications in the directories specified by the `AIIDALAB_APPS` environment variable (':'-separated).

## AiiDA lab app installation and distribution

### Manual installation

An AiiDA lab app is installed by simply copying the app directory into one of the locations mentioned above.
For example, assuming that we are launching the AiiDA lab instance from the home directory:
```bash
~/aiidalab$ mkdir ~/apps
~/aiidalab$ cp -r apps/my-app ~/apps/
```

### Installation with pip (recommended)

The process of copying the app can be automated with `pip` in combintaion with a `setup.py` script.
For this, the app data must be declared as `data_files` to be installed in the `apps/` directory, which means that app data is -- by default -- copied to `sys.prefix + '/apps'`.

Any app requirements should be declared with the `requires` key in the `metadata.json` file (following the standard format) to enable the dynamic check of requirements.
If these requirements are to be installed automatically, they must also be declared in the `setup.py` file.

The `aiidalab` package provides convenience functions to simplify this process.
See the example app distributions within the `example-apps/` directory for detailed information.

### Uninstallation / removal

To remove an app from the system, simply delete the directory containing the app, however to remove all files that might have been installed throught he installation, use pip:

```bash
$ python -m pip uninstall my-app
```

### Distribution

Using this format it is possible to build Python distribution packages:

```bash
~/my-app$ python setup.py bdist_wheel
```
will generate a file called similar to `my_app-0.1-py3-none-any.whl` which can be installed with `python -m pip install my_app-0.1-py3-none-any.whl`.
