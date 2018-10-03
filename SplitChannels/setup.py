# -*- coding: utf-8 -*-

"""
To upload to PyPI, PyPI test, or a local server:
python setup.py bdist_wheel upload -r <server_identifier>
"""

import setuptools

setuptools.setup(
    name='split_channels',
    version='0.1.0',
    author='Andreas Mittelberger',
    author_email='Brow71189@gmail.com',
    description='Splits the channels of an RGB image',
    packages=['nionswift_plugin.split_channels'],
    license='MIT',
    include_package_data=True,
    python_requires='~=3.5',
    zip_safe=False
)
