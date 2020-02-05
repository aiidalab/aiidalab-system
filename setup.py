from setuptools import setup, find_packages


setup(
    name='AiiDA lab system',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'ipywidgets~=7.5',
        'Markdown~=3.1',
        'Click~=7.0',
        ],
    entry_points={
        'console_scripts': [
            'aiidalab = aiidalab.__main__:cli',
        ],
    },
)
