from setuptools import find_packages
from aiidalab import setup, find_apps

setup(
    name='aiidalab-my-app',
    version='0.2',
    packages=find_packages(),
    apps=find_apps(),
)
