# Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)

DOC_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
BUILDER := $(firstword $(MAKECMDGOALS))

# default html builder
ifeq ($(BUILDER),)
BUILDER := html
endif

.PHONY: all
all:
	@python -m sphinx -M $(BUILDER) $(DOC_DIR) $(DOC_DIR)_build/ -E -a

$(eval $(BUILDER):all)
