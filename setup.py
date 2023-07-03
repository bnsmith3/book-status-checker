# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 13:30:37 2018
@author: bnsmith3
"""

from setuptools import setup

setup(
    name='status_checker',
    packages=['status_checker'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)