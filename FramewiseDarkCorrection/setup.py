# -*- coding: utf-8 -*-

"""
To upload to PyPI, PyPI test, or a local server:
python setup.py bdist_wheel upload -r <server_identifier>
"""

import setuptools

setuptools.setup(
    name='framewise_dark_correction',
    version='0.1.0',
    author='Andreas Mittelberger',
    author_email='Brow71189@gmail.com',
    description='Framewise dark image calculation and subtraction for the Orca camera',
    packages=['nionswift_plugin.framewise_dark_correction'],
    license='MIT',
    include_package_data=True,
    python_requires='~=3.5',
    zip_safe=False
)
