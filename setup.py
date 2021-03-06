#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-ansible-docker',
    version='0.5.0',
    author='Alexandre Chaussier',
    author_email='a.chaussier@infopen.pro',
    maintainer='Alexandre Chaussier',
    maintainer_email='a.chaussier@infopen.pro',
    license='MIT',
    url='https://github.com/infOpen/pytest-ansible-docker',
    description='Plugin to manage Ansible roles and plays testing with testinfra, using Docker containers',
    long_description=read('README.rst'),
    py_modules=['pytest_ansible_docker'],
    install_requires=['pytest>=2.9.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'ansible-docker = pytest_ansible_docker',
        ],
    },
)
