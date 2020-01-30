from setuptools import setup, find_packages
from aiidalab import find_app_data_files, get_app_requires
#from aiidalab import setup

setup(
    name='my-app',
    version='0.1',
    packages=find_packages(),

    install_requires=[
        'Aiida-lab-core',
        'ipywidgets~=7.0',
    ] + get_app_requires('app/'),

    data_files=find_app_data_files('app/'),
)
