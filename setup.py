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
    entry_points = {
        'downfile.dumpers': [
            'json=downfile.formats.format_json:to_json',
            'datetime.datetime=downfile.formats.format_datetime:datetime_to_json',
            'datetime.date=downfile.formats.format_datetime:date_to_json',
            'pandas.core.frame.DataFrame=downfile.formats.format_pandas:to_feather',
        ],
        'downfile.parsers': [
            'json=downfile.formats.format_json:from_json',
            'datetime.datetime=downfile.formats.format_datetime:datetime_from_json',
            'datetime.date=downfile.formats.format_datetime:date_from_json',
            'feather=downfile.formats.format_pandas:from_feather',
        ],
    }
    
)
