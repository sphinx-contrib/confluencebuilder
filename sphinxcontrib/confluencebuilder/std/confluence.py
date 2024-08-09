# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_HIGHLIGHT_STYLE
import os

# prefix for all api path requests to a confluence instance (v1 api)
API_REST_V1 = 'rest/api'

# prefix for all api path requests to a confluence instance (v2 api)
API_REST_V2 = 'api/v2'

# list of supported api modes to operate with
API_MODES = {
    'v1',
    'v2',
}

# default width for a table (v2 editor)
#
# It has been observed that when attempting to fix specific column widths on
# a table in the v2 editor, Confluence applies a default data width of 760 on
# the table.
CONFLUENCE_DEFAULT_V2_TABLE_WIDTH = 760

# maximum length for a confluence page title
#
# The maximum length of a Confluence page is set to 255. This is a Confluence-
# imposed limitation [1].
#
# [1]: confluence-project/confluence-core/confluence/src/
#       java/com/atlassian/confluence/pages/AbstractPage::isValidTitleLength
CONFLUENCE_MAX_TITLE_LEN = 255

# maximum width for a non-full-width page (v1; Server/DC)
#
# It has been observed that some stock macros would default to a fixed width
# of "960" (e.g. when using the Widget Connector macro). We will use this as
# a reference to the max width to ensure no unexpected overflows.
CONFLUENCE_MAX_WIDTH = 960

# list of supported editors
EDITORS = [
    'v1',
    'v2',
]

# confluence default (paragraph) indent offset (in pixels)
INDENT = 30

# confluence restricted filename (attachment) characters
INVALID_CHARS = ['\\', '/', '"', ':', '?', '*', '|', '<', '>']

# confluence default first-child masked margin offset (in pixels)
FCMMO = 10

# confluence font size observed from its default theme
FONT_SIZE = 14

# confluence font x-height size observed from its default theme
FONT_X_HEIGHT = 7

# sphinx literal to confluence language map
#
# Provides a map of Sphinx literal language values to respective and supported*
# Confluence syntax highlight language (*support can vary based on Confluence
# version). Values of the map are driven by supported languages defined by
# Confluence documentation [1][2][3]. Keys of the map are driven by short names
# defined by Pygments [4]. This is due to Sphinx's highlighting which is managed
# by Pygments [5].
#
# [1]: https://confluence.atlassian.com/display/CONF58/Code+Block+Macro
# [2]: https://confluence.atlassian.com/doc/code-block-macro-139390.html
# [3]: https://confluence.atlassian.com/confcloud/code-block-macro-724765175.html
# [4]: http://pygments.org/docs/lexers/
# [5]: http://www.sphinx-doc.org/en/stable/markup/code.html
LITERAL2LANG_MAP_COMMON = {
    # (none)
    'none': 'none',
    'raw': 'none',
    'text': 'none',
    # ActionScript
    'actionscript3': 'actionscript3',
    'as3': 'actionscript3',
    # AppleScript (Confluence >=6.0)
    'applescript': 'applescript',
    # C++
    'c++': 'cpp',
    'cpp': 'cpp',
    # ColdFusion
    'cfc': 'coldfusion',
    'coldfusion': 'coldfusion',
    # Diff
    'diff': 'diff',
    'udiff': 'diff',
    # Groovy
    'groovy': 'groovy',
    # Java
    'java': 'java',
    # Java FX
    'javafx': 'javafx',
    # Perl (Confluence <=5.10)
    'perl': 'perl',
    'pl': 'perl',
    # PHP (Confluence <=5.10)
    'php': 'php',
    'php3': 'php',
    'php4': 'php',
    'php5': 'php',
    # PowerShell
    'posh': 'powershell',
    'powershell': 'powershell',
    'ps1': 'powershell',
    'psm1': 'powershell',
    'pwsh': 'powershell',
    # Python
    'bazel': 'python',
    'py': 'python',
    'py3': 'python',
    'python': 'python',
    'python3': 'python',
    'sage': 'python',
    'starlark': 'python',
    # Ruby
    'duby': 'ruby',
    'rb': 'ruby',
    'ruby': 'ruby',
    # Sass
    'sass': 'sass',
    # Scala
    'scala': 'scala',
    # Shell
    'bash': 'bash',
    'ksh': 'bash',
    'openrc': 'bash',
    'sh': 'bash',
    'shell': 'bash',
    'zsh': 'bash',
    # SQL
    'sql': 'sql',
    # Visual Basic
    'vb': 'vb',
    'vbscript': 'vb',
    'visualbasic': 'vb',
    # YAML (Confluence Server >=6.7)
    'yaml': 'yaml',
}

LITERAL2LANG_MAP_V1 = {
    **LITERAL2LANG_MAP_COMMON,
    # C#
    'c#': 'csharp',
    'csharp': 'csharp',
    # C
    'c': 'cpp',
    # CSS
    'css': 'css',
    # Delphi
    'delphi': 'delphi',
    'pas': 'delphi',
    'pascal': 'delphi',
    'objectpascal': 'delphi',
    # Erlang
    'erlang': 'erlang',
    # HTML and XML
    'html': 'html/xml',
    'html/xml': 'html/xml',
    'xml': 'html/xml',
    'xslt': 'html/xml',
    # JavaScript
    'javascript': 'javascript',
    'js': 'javascript',
    # (special)
    # Sphinx's default highlight language is based off a superset of 'python'.
    # To follow Sphinx's method of highlighting, use Confluence's 'python'
    # highlight type as the target language for the default type.
    #
    # [1]: http://www.sphinx-doc.org/en/stable/config.html#confval-highlight_language
    DEFAULT_HIGHLIGHT_STYLE: 'python',
}

LITERAL2LANG_MAP_V2 = {
    **LITERAL2LANG_MAP_COMMON,
    # ABAP
    'abap': 'abap',
    # Ada
    'ada': 'ada',
    'ada2005': 'ada',
    'ada95': 'ada',
    # Arduino
    'arduino': 'arduino',
    # Autoit
    'autoit': 'autoit',
    # C
    'c': 'c',
    # C#
    'c#': 'c#',
    'csharp': 'c#',
    # Clojure
    'clj': 'clojure',
    'clojure': 'clojure',
    # CoffeeScript
    'coffee': 'coffeescript',
    'coffee-script': 'coffeescript',
    'coffeescript': 'coffeescript',
    # CSS
    'css': 'css',
    # CUDA
    'cu': 'cuda',
    'cuda': 'cuda',
    # D
    'd': 'd',
    # Dart
    'dart': 'dart',
    # Dockerfile
    'docker': 'docker',
    'dockerfile': 'docker',
    # Elixir
    'elixir': 'elixir',
    'ex': 'elixir',
    'exs': 'elixir',
    # Erlang
    'erlang': 'erl',
    # Fortran
    'f90': 'fortran',
    'fortran': 'fortran',
    # FoxPro
    'clipper': 'foxpro',
    'foxpro': 'foxpro',
    'vfp': 'foxpro',
    'xbase': 'foxpro',
    # Go
    'go': 'go',
    'golang': 'go',
    # GraphQL
    'graphql': 'graphql',
    # Haskell
    'haskell': 'haskell',
    'hs': 'haskell',
    # Haxe
    'haxe': 'haxe',
    'hx': 'haxe',
    'hxsl': 'haxe',
    # HCL
    'hcl': 'hcl',
    'terraform': 'hcl',
    'tf': 'hcl',
    # HTML and XML
    'html': 'html',
    # JavaScript
    'javascript': 'js',
    'js': 'js',
    # JSON
    'json': 'json',
    'json-object': 'json',
    # JSX
    'jsx': 'jsx',
    # Julia
    'jl': 'julia',
    'julia': 'julia',
    # Kotlin
    'kotlin': 'kotlin',
    # LiveScript
    'live-script': 'livescript',
    'livescript': 'livescript',
    # Lua
    'lua': 'lua',
    # Mathematica
    'mathematica': 'mathematica',
    'mma': 'mathematica',
    'nb': 'mathematica',
    # MATLAB
    'matlab': 'matlab',
    # NGINX
    'nginx': 'nginx',
    # Objective-C
    'obj-c': 'objective-c',
    'objc': 'objective-c',
    'objective-c': 'objective-c',
    'objectivec': 'objective-c',
    # Objective-J
    'obj-j': 'objective-j',
    'objective-j': 'objective-j',
    'objectivej': 'objective-j',
    'objj': 'objective-j',
    # OCaml
    'ocaml': 'ocaml',
    # Octave
    'octave': 'octave',
    # Pascal
    'delphi': 'pas',
    'pas': 'pas',
    'pascal': 'pas',
    'objectpascal': 'pas',
    # Prolog
    'prolog': 'prolog',
    # Protocol Buffers
    'proto': 'protobuf',
    'protobuf': 'protobuf',
    # Puppet
    'puppet': 'puppet',
    # QML
    'qbs': 'qbs',
    'qml': 'qbs',
    # R
    'r': 'r',
    # Racket
    'racket': 'racket',
    'rkt': 'racket',
    # reStructuredText
    'rest': 'restructuredtext',
    'restructuredtext': 'restructuredtext',
    'rst': 'restructuredtext',
    # Rust
    'rs': 'rust',
    'rust': 'rust',
    # Scheme
    'scm': 'scheme',
    'scheme': 'scheme',
    # Smalltalk
    'smalltalk': 'smalltalk',
    'squeak': 'smalltalk',
    'st': 'smalltalk',
    # SplunkSPL
    'spl': 'splunk-spl',
    'splunkspl': 'splunk-spl',
    # StandardML
    'sml': 'standardml',
    'standardml': 'standardml',
    # Swift
    'swift': 'swift',
    # Tcl
    'tcl': 'tcl',
    # TeX
    'latex': 'tex',
    'tex': 'tex',
    # TSX
    'tsx': 'tsx',
    # TypeScript
    'ts': 'typescript',
    'typescript': 'typescript',
    # Vala
    'vala': 'vala',
    'vapi': 'vala',
    # VbNet
    'lobas': 'vbnet',
    'oobas': 'vbnet',
    'sobas': 'vbnet',
    'vb.net': 'vbnet',
    'vbnet': 'vbnet',
    # Verilog
    'v': 'verilog',
    'verilog': 'verilog',
    # VHDL
    'vhdl': 'vhdl',
    # XML
    'xml': 'xml',
    'xslt': 'xml',
    # XQuery
    'xq': 'xquery',
    'xql': 'xquery',
    'xqm': 'xquery',
    'xquery': 'xquery',
    'xqy': 'xquery',
    # (special)
    # Sphinx's default highlight language is based off a superset of 'python'.
    # To follow Sphinx's method of highlighting, use Confluence's 'python'
    # highlight type as the target language for the default type.
    #
    # [1]: http://www.sphinx-doc.org/en/stable/config.html#confval-highlight_language
    DEFAULT_HIGHLIGHT_STYLE: 'python',
}

# sphinx literal to confluence language map (fallbacks)
#
# Provides an extended map to help provide fallback language types where an
# "unsupported code language" warning is still desired but an alternative
# language type is better than a default/"plain" language type. For example,
# Confluence does not support interactive Python code blocks. A warning should
# be generated to inform users that their documentation cannot render them
# (specifically, the interactive part); however, it will be still nice to
# render the content as Python code instead of plain text.
LITERAL2LANG_FBMAP_COMMON = {
    # C-like languages
    'arduino': 'cpp',
    'charmci': 'cpp',
    'clay': 'cpp',
    'cu': 'cpp',
    'cuda': 'cpp',
    'ec': 'cpp',
    'mq4': 'cpp',
    'mq5': 'cpp',
    'mql': 'cpp',
    'mql4': 'cpp',
    'mql5': 'cpp',
    'nesc': 'cpp',
    'omg-idl': 'cpp',
    'pike': 'cpp',
    'swig': 'cpp',
    'vala': 'cpp',
    'vapi': 'cpp',
    # YAML-like languages
    'salt': 'yaml',
    'sls': 'yaml',
    'yaml+jinja': 'yaml',
}

LITERAL2LANG_FBMAP_V1 = {
    **LITERAL2LANG_FBMAP_COMMON,
    # Interactive Python
    'ipython': 'python',
    'ipython2': 'python',
    'ipython3': 'python',
    # JSON (if JSON is not explicitly supported, Python style slightly works)
    'json': 'python',
    'json-object': 'python',
}

LITERAL2LANG_FBMAP_V2 = {
    **LITERAL2LANG_FBMAP_COMMON,
    # Interactive Python
    'ipython': 'py',
    'ipython2': 'py',
    'ipython3': 'py',
    # JSON (if JSON is not explicitly supported, Python style slightly works)
    'json': 'py',
    'json-object': 'py',
}

# fallback highlight language
#
# When provided a language type that is not supported by Confluence is detected on
# a code block, this fallback style will be applied instead.
FALLBACK_HIGHLIGHT_STYLE = 'none'

# no-check value to inject into a X-Atlassian-Token header
#
# Defines the no-check value to assign to the X-Atlassian-Token to handle
# attachment publishing with XSRF protections. Originally, the no-check value
# was a value of `nocheck`; however, the current promoted value is `no-check`.
# In all supported Confluence instances, the `no-check` value should work. The
# environment variable `CONFLUENCEBUILDER_LEGACY_NOCHECK` can be set for users
# who experience may experience issues with the newer value.
if 'CONFLUENCEBUILDER_LEGACY_NOCHECK' in os.environ:
    NOCHECK = 'nocheck'
else:
    NOCHECK = 'no-check'

# confluence api "retry after" header entry
#
# Confluence may response with a `Retry-After` when rate limiting has been
# imposed on an API request. This entry keeps track of the header key entry
# which reports the recommended duration till next retry.
#
# (see also: https://developer.atlassian.com/cloud/confluence/rate-limiting/)
RSP_HEADER_RETRY_AFTER = 'Retry-After'

# default code block theme
DEFAULT_THEME_STYLE = 'default'

# supported code block themes
#
# (see also: https://confluence.atlassian.com/doc/code-block-macro-139390.html)
SUPPORTED_CODE_BLOCK_THEMES = {
    'confluence': 'Confluence',
    'django': 'DJango',
    'eclipse': 'Eclipse',
    'emacs': 'Emacs',
    'fadetogrey': 'FadeToGrey',
    'midnight': 'Midnight',
    'rdark': 'RDark',
    # 'Default' is also valid and is usually synonymous with 'Confluence',
    # unless changed by a user with Confluence Administrator permissions.
    DEFAULT_THEME_STYLE: 'Default',
}

# supported image types
#
# A list of image types (mostly) supported on a Confluence instance. This
# includes image types observed in the following Confluence implementation and
# image typeswhich also observed to be rendering with Confluence Cloud:
#
#  confluence/webapp/WEB-INF/classes/mime.types
#
SUPPORTED_IMAGE_TYPES = [
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/svg+xml',
    'image/x-ms-bmp',  # image/bmp
]
