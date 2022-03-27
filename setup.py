# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from distutils.command.clean import clean
from distutils import dir_util
from setuptools import find_packages
from setuptools import setup
import io
import os

try:
    from babel.messages import frontend as babel
except ImportError:
    babel = None


with io.open('README.rst', 'r', encoding='utf-8') as readme_rst:
    long_desc = readme_rst.read()


# remove extra resources not removed by the default clean operation
class ExtendedClean(clean):
    def run(self):
        clean.run(self)

        if not self.all:
            return

        extras = [
            'dist',
            'sphinxcontrib_confluencebuilder.egg-info',
        ]
        for extra in extras:
            if os.path.exists(extra):
                dir_util.remove_tree(extra, dry_run=self.dry_run)


description = '''\
Sphinx extension to output Atlassian Confluence Storage \
Markup documents and publish to Confluence instances.\
'''

requires = [
    'docutils<0.18;python_version<"3.0"',  # legacy docutils for older sphinx
    'jinja2<=3.0.3;python_version<"3.0"',  # legacy jinja2 for older sphinx
    'requests>=2.14.0',
    'sphinx>=1.8',
]

cmdclass = {
    'clean': ExtendedClean,
}

if babel:
    cmdclass.update(
        {
            'compile_catalog': babel.compile_catalog,
            'extract_messages': babel.extract_messages,
            'init_catalog': babel.init_catalog,
            'update_catalog': babel.update_catalog,
        }
    )

setup(
    name='sphinxcontrib-confluencebuilder',
    version='1.8.0.dev0',
    url='https://github.com/sphinx-contrib/confluencebuilder',
    download_url='https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder',
    license='BSD',  # 2-clause
    author='Anthony Shaw',
    author_email='anthonyshaw@apache.org',
    description=description,
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
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    platforms='any',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
    test_suite='tests',
    cmdclass=cmdclass,
    entry_points={
        'console_scripts': [
            'sphinx-build-confluence = sphinxcontrib.confluencebuilder.__main__:main',
        ],
    },
)
