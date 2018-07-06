# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PIKACHU",
    version="0.0.3",
    author="smilefufu",
    author_email="fufu.bluesand@gmail.com",
    description="a PIKA based, Cuter and more Human queue Utility (´_ゝ`)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smilefufu/PIKACHU",
    packages=setuptools.find_packages(),
    classifiers=(
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
)
