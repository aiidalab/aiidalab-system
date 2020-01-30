from setuptools import setup, find_packages

setup(
    name='my-app',
    version='0.1',

    install_requires=[
        'Aiida-lab-core',
        'ipywidgets~=7.0',
        # List app requirements from metadata.json:
        'attrs',
    ],

    data_files=[
        ('apps/my_app', ['app/start.md', 'app/metadata.json', 'app/app.ipynb']),
        ('apps/my_app/my_app', ['app/my_app/__init__.py']),
    ]
)
