#!/usr/bin/env python

import setuptools
import distutils.command.build
import distutils.command.sdist
import os

setuptools.setup(
    name='downfile',
    version='0.0.1',
    description='Serialize data as a zip file of json and other formats',
    long_description='Serialize data as a zip file of json and other formats',
    long_description_content_type="text/markdown",
    author='Egil Moeller',
    author_email='em@emrld.no',
    url='https://github.com/emerald-geomodelling/downfile',
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas",
    ],
#    entry_points = {
#        'serializers': ['pandas.DataFrame=downfile.formats.pandas:to_feather'],
#        'deserializers': ['feather=downfile.formats.pandas:from_feather'],
#    }
    
)
