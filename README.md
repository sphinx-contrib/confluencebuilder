# Atlassian Confluence Builder for Sphinx

[![pip Version](https://badgen.net/pypi/v/sphinxcontrib-confluencebuilder?label=PyPI)](https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder)
[![Build Status](https://github.com/sphinx-contrib/confluencebuilder/actions/workflows/build.yml/badge.svg)](https://github.com/sphinx-contrib/confluencebuilder/actions/workflows/build.yml) 
[![Documentation Status](https://img.shields.io/readthedocs/sphinxcontrib-confluencebuilder?label=Documentation)](https://sphinxcontrib-confluencebuilder.readthedocs.io/) 
[![PyPI download month](https://img.shields.io/pypi/dm/sphinxcontrib-confluencebuilder.svg?label=Downloads)](https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder/) 

[Sphinx][sphinx] extension to build Confluence® compatible markup format
files and optionally publish them to a Confluence instance.

## Requirements

* [Confluence][confluence] Cloud or Data Center 8.1+
* [Python][python] 3.9+
* [Requests][requests] 2.25.0+
* [Sphinx][sphinx] 7.2+

## Installing

The recommended method to installing this extension is using [pip][pip]:

```shell
pip install sphinxcontrib-confluencebuilder
 (or)
python -m pip install sphinxcontrib-confluencebuilder
```

For a more in-depth installation information, see also:

> Atlassian Confluence Builder for Sphinx — Installation \
> https://sphinxcontrib-confluencebuilder.readthedocs.io/install

## Usage

- Register the extension `sphinxcontrib.confluencebuilder` in the project's
  configuration script (`conf.py`):

```python
extensions = [
    'sphinxcontrib.confluencebuilder',
]
```

- Run sphinx-build with the builder `confluence`:

```shell
sphinx-build -M confluence . _build -E -a
 (or)
python -m sphinx -M confluence . _build -E -a
```

For more information on the usage of this extension, see also:

> Atlassian Confluence Builder for Sphinx — Tutorial \
> https://sphinxcontrib-confluencebuilder.readthedocs.io/tutorial

## Configuration

The following is an example of a simple configuration for Confluence generation
and publishing:

```python
extensions = [
    'sphinxcontrib.confluencebuilder',
]
confluence_publish = True
confluence_space_key = 'TEST'
confluence_parent_page = 'Documentation'
confluence_server_url = 'https://intranet-wiki.example.com/'
confluence_ask_user = True
confluence_ask_password = True
```

For a complete list of configuration options, see also:

> Atlassian Confluence Builder for Sphinx — Configuration \
> https://sphinxcontrib-confluencebuilder.readthedocs.io/configuration

## Features

For a complete list of supported markup, extensions, etc.; see:

> Atlassian Confluence Builder for Sphinx — Features \
> https://sphinxcontrib-confluencebuilder.readthedocs.io/features

For a complete list of directives supported by this extension, see:

> Atlassian Confluence Builder for Sphinx — Directives \
> https://sphinxcontrib-confluencebuilder.readthedocs.io/directives

## Demonstration

A demonstration of this extension can be seen by inspecting the published
validation/testing documents found here:

> Atlassian Confluence Builder for Sphinx — Online Demo on Confluence Cloud \
> https://sphinxcontrib-confluencebuilder.atlassian.net/

----

Atlassian Confluence Builder for Sphinx project is unaffiliated with Atlassian.\
Atlassian is a registered trademark of Atlassian Pty Ltd.\
Confluence is a registered trademark of Atlassian Pty Ltd.


[confluence]: https://www.atlassian.com/software/confluence
[pip]: https://pip.pypa.io/
[python]: https://www.python.org/
[requests]: https://pypi.python.org/pypi/requests
[sphinx]: https://www.sphinx-doc.org/
