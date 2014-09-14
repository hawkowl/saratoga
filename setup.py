#!/usr/bin/env python

from setuptools import find_packages, setup
from saratoga import __version__


setup(
    name='saratoga',
    description='Framework for making APIs.',
    version=__version__,
    author='HawkOwl',
    author_email='hawkowl@atleastfornow.net',
    url='https://github.com/hawkowl/saratoga',
    packages=find_packages(),
    package_data={
        'saratoga': [
            'test/*.json',
            'static/*.html',
            'static/content/*.css'
        ]
        },
    scripts=[
        ],
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7"
        ],
    keywords=[
        "twisted", "http", "api"
        ],
    install_requires=[
        "twisted",
        "jsonschema",
        "negotiator"
        ],
    long_description=file('README.rst').read()
)
