# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os

from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_HIGHLIGHT_STYLE

"""
confluence trailing bind path for rest api
"""
API_REST_BIND_PATH = "rest/api"

"""
confluence default (paragraph) indent offset (in pixels)
"""
INDENT = 30

"""
confluence restricted filename (attachment) characters
"""
INVALID_CHARS = ["\\", "/", '"', ":", "?", "*", "|", "<", ">"]

"""
confluence default first-child masked margin offset (in pixels)
"""
FCMMO = 10

"""
sphinx literal to confluence language map

Provides a map of Sphinx literal language values to respective and supported*
Confluence syntax highlight language (*support can vary based on Confluence
version). Values of the map are driven by supported languages defined by
Confluence documentation [1][2][3]. Keys of the map are driven by short names
defined by Pygments [4]. This is due to Sphinx's highlighting which is managed
by Pygments [5].

[1]: https://confluence.atlassian.com/display/CONF58/Code+Block+Macro
[2]: https://confluence.atlassian.com/doc/code-block-macro-139390.html
[3]: https://confluence.atlassian.com/confcloud/code-block-macro-724765175.html
[4]: http://pygments.org/docs/lexers/
[5]: http://www.sphinx-doc.org/en/stable/markup/code.html
"""
LITERAL2LANG_MAP = {
    # ActionScript
    "actionscript3": "actionscript3",
    "as3": "actionscript3",
    # AppleScript (Confluence >=6.0)
    "applescript": "applescript",
    # Bash
    "bash": "bash",
    "ksh": "bash",
    "sh": "bash",
    "shell": "bash",
    "zsh": "bash",
    # C#
    "c#": "csharp",
    "csharp": "csharp",
    # C++
    "c": "cpp",
    "c++": "cpp",
    "cpp": "cpp",
    # ColdFusion
    "cfc": "coldfusion",
    "coldfusion": "coldfusion",
    # CSS
    "css": "css",
    # Delphi
    "delphi": "delphi",
    "pas": "delphi",
    "pascal": "delphi",
    "objectpascal": "delphi",
    # Diff
    "diff": "diff",
    "udiff": "diff",
    # Erlang
    "erlang": "erlang",
    # Groovy
    "groovy": "groovy",
    # HTML and XML
    "html": "html/xml",
    "html/xml": "html/xml",
    "xml": "html/xml",
    "xslt": "html/xml",
    # Java
    "java": "java",
    # Java FX
    "javafx": "javafx",
    # JavaScript
    "javascript": "javascript",
    "js": "javascript",
    # Plain Text
    "none": "none",
    "raw": "none",
    "text": "none",
    # Perl (Confluence <=5.10)
    "perl": "perl",
    "pl": "perl",
    # PHP (Confluence <=5.10)
    "php": "php",
    "php3": "php",
    "php4": "php",
    "php5": "php",
    # PowerShell
    "posh": "powershell",
    "powershell": "powershell",
    "ps1": "powershell",
    "psm1": "powershell",
    # Python
    "py": "python",
    "py3": "python",
    "python": "python",
    "python3": "python",
    "sage": "python",
    # Ruby
    "duby": "ruby",
    "rb": "ruby",
    "ruby": "ruby",
    # Sass
    "sass": "sass",
    # Scala
    "scala": "scala",
    # SQL
    "sql": "sql",
    # Visual Basic
    "vb": "vb",
    "vbscript": "vb",
    # YAML (Confluence Server >=6.7)
    "yaml": "yaml",
    # (special)
    # Sphinx's default highlight language is based off a superset of 'python'.
    # To follow Sphinx's method of highlighting, use Confluence's 'python'
    # highlight type as the target language for the default type.
    #
    # [1]: http://www.sphinx-doc.org/en/stable/config.html#confval-highlight_language
    DEFAULT_HIGHLIGHT_STYLE: "python",
}

"""
fallback highlight language

When provided a language type that is not supported by Confluence is detected on
a code block, this fallback style will be applied instead.
"""
FALLBACK_HIGHLIGHT_STYLE = "none"

"""
no-check value to inject into a X-Atlassian-Token header

Defines the no-check value to assign to the X-Atlassian-Token to handle
attachment publishing with XSRF protections. Originally, the no-check value was
a value of `nocheck`; however, the current promoted value is `no-check`. In all
supported Confluence instances, the `no-check` value should work. The
environment variable `CONFLUENCEBUILDER_LEGACY_NOCHECK` can be set for users who
experience may experience issues with the newer value.
"""
if "CONFLUENCEBUILDER_LEGACY_NOCHECK" in os.environ:
    NOCHECK = "nocheck"
else:
    NOCHECK = "no-check"

"""
supported image types

A list of image types (mostly) supported on a Confluence instance. This includes
image types observed in the following Confluence implementation and image types
which also observed to be rendering with Confluence Cloud:

    confluence/webapp/WEB-INF/classes/mime.types
"""
SUPPORTED_IMAGE_TYPES = [
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/svg+xml",
    "image/x-ms-bmp",  # image/bmp
]
