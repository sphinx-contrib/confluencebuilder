# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
Sphinx_ extension to build Confluence Wiki markup files.

This extension is in particular useful to use in combination with an automated publisher to confluence
'''

requires = [
    'future',
    'requests',
    'Sphinx>=1.0',
    ]

setup(
    name='sphinxcontrib-confluencebuilder',
    version='0.7',
    url='https://github.com/tonybaloney/sphinxcontrib-confluencebuilder',
    download_url='https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder',
    license='BSD', # 2-clause
    author='Anthony Shaw',
    author_email='anthonyshaw@apache.org',
    description="""Sphinx extension to output Atlassian Confluence Wiki """
                """files and publish to Confluence Servers.""",
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
    test_suite='test',
    tests_require=['sphinx']
)
