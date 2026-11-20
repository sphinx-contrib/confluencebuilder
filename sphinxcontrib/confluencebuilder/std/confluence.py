# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_HIGHLIGHT_STYLE
import os

# modern cloud api endpoint (scoped tokens)
API_CLOUD_ENDPOINT = 'https://api.atlassian.com/ex/confluence'

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

# default "maximum" width for a table (v2 editor)
#
# It has been observed that when attempting to maximum the width of a table in
# the v2 editor, Confluence applies a limit of 1800 on the table.
CONFLUENCE_DEFAULT_V2_TABLE_WIDTH_MAX = 1800

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
    # ABAP (Confluence Data Center >=9.1)
    'abap': 'abap',
    # ActionScript
    'actionscript3': 'actionscript3',
    'as3': 'actionscript3',
    # AppleScript (Confluence >=6.0)
    'applescript': 'applescript',
    # Ada (Confluence Data Center >=9.1)
    'ada': 'ada',
    'ada2005': 'ada',
    'ada95': 'ada',
    # Arduino (Confluence Data Center >=9.1)
    'arduino': 'arduino',
    # Autoit (Confluence Data Center >=9.1)
    'autoit': 'autoit',
    # C (Confluence Data Center >=9.1; "cpp -> c")
    'c': 'c',
    # C++
    'c++': 'cpp',
    'cpp': 'cpp',
    # Clojure (Confluence Data Center >=9.1)
    'clj': 'clojure',
    'clojure': 'clojure',
    # CoffeeScript (Confluence Data Center >=9.1)
    'coffee': 'coffeescript',
    'coffee-script': 'coffeescript',
    'coffeescript': 'coffeescript',
    # ColdFusion
    'cfc': 'coldfusion',
    'coldfusion': 'coldfusion',
    # CSS
    'css': 'css',
    # CUDA (Confluence Data Center >=9.1)
    'cu': 'cuda',
    'cuda': 'cuda',
    # D (Confluence Data Center >=9.1)
    'd': 'd',
    # Dart (Confluence Data Center >=9.1)
    'dart': 'dart',
    # Diff
    'diff': 'diff',
    'udiff': 'diff',
    # Dockerfile (Confluence Data Center >=9.1)
    'docker': 'docker',
    'dockerfile': 'docker',
    # Elixir (Confluence Data Center >=9.1)
    'elixir': 'elixir',
    'ex': 'elixir',
    'exs': 'elixir',
    # Fortran (Confluence Data Center >=9.1)
    'f90': 'fortran',
    'fortran': 'fortran',
    # FoxPro (Confluence Data Center >=9.1)
    'clipper': 'foxpro',
    'foxpro': 'foxpro',
    'vfp': 'foxpro',
    'xbase': 'foxpro',
    # Gherkin (Confluence Data Center >=9.1)
    'cucumber': 'gherkin',
    'gherkin': 'gherkin',
    # Go (Confluence Data Center >=9.1)
    'go': 'go',
    'golang': 'go',
    # GraphQL (Confluence Data Center >=9.1)
    'graphql': 'graphql',
    # Groovy
    'groovy': 'groovy',
    # Handlebars (Confluence Data Center >=9.1)
    'handlebars': 'handlebars',
    'hbs': 'handlebars',
    'html+handlebars': 'handlebars',
    # Haskell (Confluence Data Center >=9.1)
    'haskell': 'haskell',
    'hs': 'haskell',
    # Haxe (Confluence Data Center >=9.1)
    'haxe': 'haxe',
    'hx': 'haxe',
    'hxsl': 'haxe',
    # HCL (Confluence Data Center >=9.1)
    'hcl': 'hcl',
    'terraform': 'hcl',
    'tf': 'hcl',
    # HTML (Confluence Data Center >=9.1; "html/xml -> html")
    'html': 'html/xml',
    'html/xml': 'html/xml',
    # Java
    'java': 'java',
    # Java FX
    'javafx': 'javafx',
    # JSON (Confluence Data Center >=9.1)
    'json': 'json',
    'json-object': 'json',
    # JSX (Confluence Data Center >=9.1)
    'jsx': 'jsx',
    # Julia (Confluence Data Center >=9.1)
    'jl': 'julia',
    'julia': 'julia',
    # Kotlin (Confluence Data Center >=9.1)
    'kotlin': 'kotlin',
    # LiveScript (Confluence Data Center >=9.1)
    'live-script': 'livescript',
    'livescript': 'livescript',
    # Lua (Confluence Data Center >=9.1)
    'lua': 'lua',
    # Markdown
    'markdown': 'markdown',
    'md': 'markdown',
    # Mathematica (Confluence Data Center >=9.1)
    'mathematica': 'mathematica',
    'mma': 'mathematica',
    'nb': 'mathematica',
    # MATLAB (Confluence Data Center >=9.1)
    'matlab': 'matlab',
    # NGINX (Confluence Data Center >=9.1)
    'nginx': 'nginx',
    # Objective-C (Confluence Data Center >=9.1)
    'obj-c': 'objective-c',
    'objc': 'objective-c',
    'objective-c': 'objective-c',
    'objectivec': 'objective-c',
    # Objective-J (Confluence Data Center >=9.1)
    'obj-j': 'objective-j',
    'objective-j': 'objective-j',
    'objectivej': 'objective-j',
    'objj': 'objective-j',
    # OCaml (Confluence Data Center >=9.1)
    'ocaml': 'ocaml',
    # Octave (Confluence Data Center >=9.1)
    'octave': 'octave',
    # Pascal (Confluence Data Center >=9.1; "delphi -> pas")
    'delphi': 'pas',
    'pas': 'pas',
    'pascal': 'pas',
    'objectpascal': 'pas',
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
    # Prolog (Confluence Data Center >=9.1)
    'prolog': 'prolog',
    # Protocol Buffers (Confluence Data Center >=9.1)
    'proto': 'protobuf',
    'protobuf': 'protobuf',
    # Puppet (Confluence Data Center >=9.1)
    'puppet': 'puppet',
    # Python
    'bazel': 'python',
    'py': 'python',
    'py3': 'python',
    'python': 'python',
    'python3': 'python',
    'sage': 'python',
    'starlark': 'python',
    # QML (Confluence Data Center >=9.1)
    'qbs': 'qbs',
    'qml': 'qbs',
    # R (Confluence Data Center >=9.1)
    'r': 'r',
    # Racket (Confluence Data Center >=9.1)
    'racket': 'racket',
    'rkt': 'racket',
    # reStructuredText (Confluence Data Center >=9.1)
    'rest': 'restructuredtext',
    'restructuredtext': 'restructuredtext',
    'rst': 'restructuredtext',
    # Ruby
    'duby': 'ruby',
    'rb': 'ruby',
    'ruby': 'ruby',
    # Rust (Confluence Data Center >=9.1)
    'rs': 'rust',
    'rust': 'rust',
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
    # Scheme (Confluence Data Center >=9.1)
    'scm': 'scheme',
    'scheme': 'scheme',
    # Smalltalk (Confluence Data Center >=9.1)
    'smalltalk': 'smalltalk',
    'squeak': 'smalltalk',
    'st': 'smalltalk',
    # SplunkSPL (Confluence Data Center >=9.1)
    'spl': 'splunk-spl',
    'splunkspl': 'splunk-spl',
    # SQL
    'sql': 'sql',
    # StandardML (Confluence Data Center >=9.1)
    'sml': 'standardml',
    'standardml': 'standardml',
    # Swift (Confluence Data Center >=9.1)
    'swift': 'swift',
    # Tcl (Confluence Data Center >=9.1)
    'tcl': 'tcl',
    # TeX (Confluence Data Center >=9.1)
    'latex': 'tex',
    'tex': 'tex',
    # TSX (Confluence Data Center >=9.1)
    'tsx': 'tsx',
    # TypeScript (Confluence Data Center >=9.1)
    'ts': 'typescript',
    'typescript': 'typescript',
    # Vala (Confluence Data Center >=9.1)
    'vala': 'vala',
    'vapi': 'vala',
    # VbNet (Confluence Data Center >=9.1)
    'lobas': 'vbnet',
    'oobas': 'vbnet',
    'sobas': 'vbnet',
    'vb.net': 'vbnet',
    'vbnet': 'vbnet',
    # Verilog (Confluence Data Center >=9.1)
    'v': 'verilog',
    'verilog': 'verilog',
    # Visual Basic
    'vb': 'vb',
    'vbscript': 'vb',
    'visualbasic': 'vb',
    # VHDL (Confluence Data Center >=9.1)
    'vhdl': 'vhdl',
    # XML (Confluence Data Center >=9.1; "html/xml -> xml")
    'xml': 'xml',
    'xslt': 'xml',
    # XQuery (Confluence Data Center >=9.1)
    'xq': 'xquery',
    'xql': 'xquery',
    'xqm': 'xquery',
    'xquery': 'xquery',
    'xqy': 'xquery',
    # YAML (Confluence Server >=6.7)
    'yaml': 'yaml',
    # (special)
    # Sphinx's default highlight language is based off a superset of 'python'.
    # To follow Sphinx's method of highlighting, use Confluence's 'python'
    # highlight type as the target language for the default type.
    #
    # [1]: http://www.sphinx-doc.org/en/stable/config.html#confval-highlight_language
    DEFAULT_HIGHLIGHT_STYLE: 'python',
}

LITERAL2LANG_MAP_V1 = {
    **LITERAL2LANG_MAP_COMMON,
    # C#
    'c#': 'csharp',
    'csharp': 'csharp',
    # Erlang
    'erlang': 'erlang',
    # JavaScript
    'javascript': 'javascript',
    'js': 'javascript',
}

LITERAL2LANG_MAP_V2 = {
    **LITERAL2LANG_MAP_COMMON,
    # C#
    'c#': 'c#',
    'csharp': 'c#',
    # Erlang
    'erlang': 'erl',
    # JavaScript
    'javascript': 'js',
    'js': 'js',
    # Mermaid
    'mermaid': 'mermaid',
    # TOML
    'toml': 'toml',
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
    # C-like languages (Confluence Data Center >=9.1; "cpp -> c")
    'clay': 'c',
    'ec': 'c',
    'nesc': 'c',
    'pike': 'c',
    'vala': 'c',
    'vapi': 'c',
    # C++-like languages
    'arduino': 'cpp',
    'charmci': 'cpp',
    'cu': 'cpp',
    'cuda': 'cpp',
    'mq4': 'cpp',
    'mq5': 'cpp',
    'mql': 'cpp',
    'mql4': 'cpp',
    'mql5': 'cpp',
    'omg-idl': 'cpp',
    'swig': 'cpp',
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
}

LITERAL2LANG_FBMAP_V2 = {
    **LITERAL2LANG_FBMAP_COMMON,
    # Interactive Python
    'ipython': 'py',
    'ipython2': 'py',
    'ipython3': 'py',
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
