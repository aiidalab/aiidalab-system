from setuptools import find_packages
from aiidalab import setup, find_apps

setup(
    name='my-nested-app',
    version='0.1',
    packages=find_packages(),
    apps=find_apps(),
)
