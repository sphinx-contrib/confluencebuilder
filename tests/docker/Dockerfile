# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
#
# Container image used for documentation testing (generation, publication,
# etc.). The main reason why this package exists is to have a ready-container
# that includes TeX support for LaTeX/PDF checks. The container includes 
# additional packages for other used components (gettext for locale work),
# tox for testing, etc.

FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install --assume-yes \
    # Sphinx internationalization support
    gettext \
    # Graphviz support
    graphviz \
    # Ensure `python` is available for any support scripts
    python-is-python3 \
    # Install pip support for easy support for installing other dependencies
    python3-pip \
    # Allow preparing a virtual environment
    python3-venv \
    # Full TeX Live suite for LaTeX/PDF support
    texlive-full \
    # Tool used for select tests
    tox \
    && rm -rf /var/lib/apt/lists/*
