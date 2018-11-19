# -*- coding: utf-8 -*-

"""
To upload to PyPI, PyPI test, or a local server:
python setup.py bdist_wheel upload -r <server_identifier>
"""

import setuptools

setuptools.setup(
    name='map_4d',
    version='0.1.0',
    author='Andreas Mittelberger',
    author_email='Brow71189@gmail.com',
    description='Map integral of a square region in a 4d dataset',
    packages=['nionswift_plugin.map_4d'],
    license='MIT',
    include_package_data=True,
    python_requires='~=3.5',
    zip_safe=False
)
