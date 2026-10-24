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
    py311-sphinx81
    py311-sphinx81-release
    py311-sphinx82
    py311-sphinx82-release
    py311-sphinx90
    py311-sphinx90-release
    py312-sphinx81
    py312-sphinx81-release
    py312-sphinx82
    py312-sphinx82-release
    py312-sphinx90
    py312-sphinx90-release
    py312-sphinx91
    py312-sphinx91-release
    py313-sphinx81
    py313-sphinx81-release
    py313-sphinx82
    py313-sphinx82-release
    py313-sphinx90
    py313-sphinx90-release
    py313-sphinx91
    py313-sphinx91-release
    py313-sphinx92
    py313-sphinx92-release
    py314-sphinx81
    py314-sphinx81-release
    py314-sphinx82
    py314-sphinx82-release
    py314-sphinx90
    py314-sphinx90-release
    py314-sphinx91
    py314-sphinx91-release
    py314-sphinx92
    py314-sphinx92-release
    py315-sphinx81
    py315-sphinx81-release
    py315-sphinx82
    py315-sphinx82-release
    py315-sphinx90
    py315-sphinx90-release
    py315-sphinx91
    py315-sphinx91-release
    py315-sphinx92
    py315-sphinx92-release
    pylint
    ruff
)

envs=$(IFS=, ; echo "${cfg_envs[*]}")
$cmd_prefix tox -p -e "$envs" "$@"
