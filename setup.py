#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

setup(
    name='expeditious',
    version='1.0.0',
    author='Tarjei Husøy',
    author_email='telemark-webmaster@ntnui.no',
    url='https://github.com/TelemarkAlpint/expeditious',
    description='Helpers for working with trimmed audio',
    py_modules=['monsen'],
    install_requires=[
        'pyyaml',
        'requests',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'monsen = monsen:main',
            'nansen = nansen:main'
        ]
    }
)
