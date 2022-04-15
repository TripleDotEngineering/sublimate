from setuptools import setup

setup(
    name = 'sublimate',
    version = '0.1.0',
    packages = ['sublimate'],
    install_requires = [
        'trivium-cli',
        'networkx'
    ],
    entry_points = {
        'console_scripts': [
            'sublimate = sublimate.__main__:entry'
        ]
    }
)