#!/usr/bin/env python

import sys
from setuptools import setup, find_packages

version = '0.0.1'
description = 'Pattern matching for Python'
url=''
long_description = '''

PyPat provides OCaml-style pattern matching, complete with as-naming,
guards, object decomposition, and piecewise-defined functions.'''.lstrip()

setup(
    name='pypat',
    version=version,
    packages=find_packages(exclude=['tests*']),
    description=description,
    long_description=long_description,
    url=url,
    author='Michael M. Vitousek',
    author_email='mvitouse@indiana.edu',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Indended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='pattern match adt')
