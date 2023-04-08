#!/usr/bin/env bash

git clone https://github.com/sphinx-doc/sphinx.git
cd sphinx
echo "" >>doc/conf.py
echo "extensions.append('sphinxcontrib.confluencebuilder')" >>doc/conf.py
