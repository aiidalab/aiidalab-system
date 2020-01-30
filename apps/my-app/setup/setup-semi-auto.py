from aiidalab import setup, find_apps

setup(
    name='my-app',
    version='0.1',
    packages=find_packages(),
    apps=['app/'],
)
