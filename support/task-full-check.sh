#!/usr/bin/env bash

set -e

cmd_prefix=
if command -v winpty >/dev/null 2>/dev/null; then
    cmd_prefix=winpty
fi

cfg_envs=(
    develop
    doc-html
    doc-latexpdf
    mypy
    py310-sphinx73
    py310-sphinx73-release
    py310-sphinx74
    py310-sphinx74-release
    py310-sphinx80
    py310-sphinx80-release
    py310-sphinx81
    py310-sphinx81-release
    py311-sphinx73
    py311-sphinx73-release
    py311-sphinx74
    py311-sphinx74-release
    py311-sphinx80
    py311-sphinx80-release
    py311-sphinx81
    py311-sphinx81-release
    py311-sphinx82
    py311-sphinx82-release
    py312-sphinx73
    py312-sphinx73-release
    py312-sphinx74
    py312-sphinx74-release
    py312-sphinx80
    py312-sphinx80-release
    py312-sphinx81
    py312-sphinx81-release
    py312-sphinx82
    py312-sphinx82-release
    py313-sphinx73
    py313-sphinx73-release
    py313-sphinx74
    py313-sphinx74-release
    py313-sphinx80
    py313-sphinx80-release
    py313-sphinx81
    py313-sphinx81-release
    py313-sphinx82
    py313-sphinx82-release
    py314-sphinx73
    py314-sphinx73-release
    py314-sphinx74
    py314-sphinx74-release
    py314-sphinx80
    py314-sphinx80-release
    py314-sphinx81
    py314-sphinx81-release
    py314-sphinx82
    py314-sphinx82-release
    pylint
    ruff
)

envs=$(IFS=, ; echo "${cfg_envs[*]}")
$cmd_prefix tox -p -e "$envs" "$@"
