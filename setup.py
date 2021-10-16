# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
from distutils import dir_util
from distutils.command.clean import clean

from setuptools import find_packages, setup

with open("README.rst", "r") as readme_rst:
    long_desc = readme_rst.read()

# remove extra resources not removed by the default clean operation
class ExtendedClean(clean):
    def run(self):
        clean.run(self)

        if not self.all:
            return

        extras = [
            "dist",
            "sphinxcontrib_confluencebuilder.egg-info",
        ]
        for extra in extras:
            if os.path.exists(extra):
                dir_util.remove_tree(extra, dry_run=self.dry_run)


requires = [
    "future>=0.16.0",
    "requests>=2.14.0",
    "sphinx>=1.8",
]

setup(
    name="sphinxcontrib-confluencebuilder",
    version="1.7.0.dev0",
    url="https://github.com/sphinx-contrib/confluencebuilder",
    download_url="https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder",
    license="BSD",  # 2-clause
    author="Anthony Shaw",
    author_email="anthonyshaw@apache.org",
    description="""Sphinx extension to output Atlassian Confluence Storage """
    """Markup documents and publish to Confluence instances.""",
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    platforms="any",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=["sphinxcontrib"],
    test_suite="tests",
    tests_require=["sphinx"],
    cmdclass={
        "clean": ExtendedClean,
    },
    entry_points={
        "console_scripts": [
            "sphinx-build-confluence = sphinxcontrib.confluencebuilder.__main__:main",
        ],
    },
)
