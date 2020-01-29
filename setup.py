from setuptools import setup, find_packages


setup(
    name='AiiDA-lab',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'ipywidgets~=7.5',
        'Markdown~=3.1',
        ],
)
