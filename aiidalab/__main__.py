#!/usr/bin/env python
import click
from textwrap import indent

from . import AiidaLab, show_app_data_files
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
    if apps:
        click.echo("Installed apps:")
        for app in apps:
            click.secho(f"- {app.id[:6]}: {app} [{app.package}]", bold=True)
            missing = list(app.find_missing_dependencies())
            if missing:
                click.secho("  Some app requirements are not met:", fg='red')
            for req in app.find_missing_dependencies():
                click.secho(f"  Requirement '{req}' not met!", fg='yellow')
            if show_data_files:
                data_files = show_app_data_files(app.path)
                formatted = fmt_data_files_for_setup_cfg(data_files)
                click.secho(indent('\n'.join(formatted), '  '))


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
