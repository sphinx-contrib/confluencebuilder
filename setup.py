# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from setuptools import setup, find_packages

with open('README.rst', 'r') as readme_rst:
    long_desc = readme_rst.read()

requires = [
    'future>=0.16.0',
    'requests>=2.14.0',
    'sphinx>=1.6.3',
    ]

setup(
    name='sphinxcontrib-confluencebuilder',
    version='1.2.0',
    url='https://github.com/sphinx-contrib/confluencebuilder',
    download_url='https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder',
    license='BSD',  # 2-clause
    author='Anthony Shaw',
    author_email='anthonyshaw@apache.org',
    description="""Sphinx extension to output Atlassian Confluence Storage """
                """Markup documents and publish to Confluence instances.""",
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
    test_suite='test',
    tests_require=['sphinx']
)
