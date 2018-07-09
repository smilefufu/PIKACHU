# -*- coding: utf-8 -*-

import sys
import setuptools
from distutils.core import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

def get_info():
    init_file = 'PIKACHU/__init__.py'
    with open(init_file, 'r') as f:
        for line in f.readlines():
            if "=" in line:
                exec(compile(line, "", 'exec'))
    return locals()['name'], locals()['author'], locals()['version']

NAME, AUTHOR, VERSION = get_info()

sys.dont_write_bytecode = True
setuptools.setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email="fufu.bluesand@gmail.com",
    description="a PIKA based, Cuter and more Human rabbitmq queue Utility (´_ゝ`)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smilefufu/PIKACHU",
    data_files = [("", ["LICENSE"])],
    packages=setuptools.find_packages(),
    install_requires=[
        "pika",
    ],
    classifiers=(
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent'
    ),
)
