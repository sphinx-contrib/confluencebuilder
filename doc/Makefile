# Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)

DOC_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
BASE_DIR := $(abspath $(DOC_DIR)/..)
BUILDER := $(firstword $(MAKECMDGOALS))

# default html builder
ifeq ($(BUILDER),)
BUILDER := html
endif

.PHONY: all
all:
	@cd $(BASE_DIR) >/dev/null && \
		python -m sphinx -M $(BUILDER) $(DOC_DIR) $(DOC_DIR)_build/ -E -a -W

$(eval $(BUILDER):all)
