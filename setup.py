# -*- coding: utf-8 -*-
import os

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

from setuptools import find_packages, setup

with open("README.md", "r") as fd:
    README = fd.read()

setup(
    name='aio-cryptapi',
    version='1.0.0',
    description="Python Library for CryptAPI payment gateway",
    long_description=README,
    long_description_content_type="text/markdown",
    author='Adam Zhou',
    author_email='adamzhouisnothing@gmail.com',
    url='https://github.com/amazingchow/aio-cryptapi',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiohttp',
        'loguru',
        'ujson'
    ],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    license="MIT",
    zip_safe=False
)
