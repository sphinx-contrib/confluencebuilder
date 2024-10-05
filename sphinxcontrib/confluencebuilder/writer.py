# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from __future__ import annotations
from docutils import writers
from typing import Any
from typing import ClassVar


class ConfluenceWriter(writers.Writer):
    supported = ('text',)
    settings_spec = ('No options here.', '', ())
    settings_defaults: ClassVar[dict[str, Any]] = {}

    def __init__(self, builder):
        writers.Writer.__init__(self)
        self.builder = builder
        self.output = None

    def translate(self):
        visitor = self.builder.create_translator(self.document, self.builder)
        self.document.walkabout(visitor)
        if hasattr(visitor, 'body_final'):
            self.output = visitor.body_final
