#!/usr/bin/env python
import click

from . import AiidaLab, find_app_data_files
from aiidalab.app_management import CondaAppManager
from .util import fmt_data_files_for_setup_cfg


@click.group()
def cli():
    pass


@cli.command(name='list',
             help="List all installed applications.")
@click.option('--show-data-files', is_flag=True)
def list_(show_data_files):
    lab = AiidaLab()
    click.echo(lab)

    apps = list(lab.find_apps())
    app_manager = CondaAppManager()
    for app in apps:
        package = app_manager.package_map.get(app.path)
        print(app, package)
        if show_data_files:
            files = find_app_data_files(app.path)
            files_formatted = fmt_data_files_for_setup_cfg(files)
            print('\n'.join(files_formatted))


@cli.command()
@click.argument('name')
def install(name):
    lab = AiidaLab()
    lab.install_app(name)


@cli.command()
@click.argument('identifier')
def uninstall(identifier):
    lab = AiidaLab()
    app = lab.get_app(identifier)
    if app.package is None:
        print("rm", app.path)
    else:
        print("python -m pip uninstall", app.package)


if __name__ == '__main__':
    cli()
