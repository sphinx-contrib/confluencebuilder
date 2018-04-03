# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from .sphinx import DEFAULT_HIGHLIGHT_STYLE

"""
confluence trailing bind path for rest api
"""
API_REST_BIND_PATH = 'rest/api'

"""
confluence trailing bind path for xml-rpc api
"""
API_XMLRPC_BIND_PATH = 'rpc/xmlrpc'

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
    'actionscript3': 'actionscript3',
    'as3': 'actionscript3',
    # AppleScript (Confluence >=6.0)
    'applescript': 'applescript',
    # Bash
    'bash': 'bash',
    'ksh': 'bash',
    'sh': 'bash',
    'shell': 'bash',
    'zsh': 'bash',
    # C#
    'c#': 'csharp',
    'csharp': 'csharp',
    # C++
    'c': 'cpp',
    'c++': 'cpp',
    'cpp': 'cpp',
    # ColdFusion
    'cfc': 'coldfusion',
    'coldfusion': 'coldfusion',
    # CSS
    'css': 'css',
    # Delphi
    'delphi': 'delphi',
    'pas': 'delphi',
    'pascal': 'delphi',
    'objectpascal': 'delphi',
    # Diff
    'diff': 'diff',
    'udiff': 'diff',
    # Erlang
    'erlang': 'erlang',
    # Groovy
    'groovy': 'groovy',
    # HTML and XML
    'html': 'html/xml',
    'html/xml': 'html/xml',
    'xml': 'html/xml',
    'xslt': 'html/xml',
    # Java
    'java': 'java',
    # Java FX
    'javafx': 'javafx',
    # JavaScript
    'javascript': 'javascript',
    'js': 'javascript',
    # Plain Text
    'none': 'none',
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
    # Python
    'py': 'python',
    'python': 'python',
    'sage': 'python',
    # Ruby
    'duby': 'ruby',
    'rb': 'ruby',
    'ruby': 'ruby',
    # Scala
    'scala': 'scala',
    # SQL
    'sql': 'sql',
    # Visual Basic
    'vb': 'vb',
    # (special)
    # Sphinx's default highlight language is based off a superset of 'python'.
    # To follow Sphinx's method of highlighting, use Confluence's 'python'
    # highlight type as the target language for the default type.
    #
    # [1]: http://www.sphinx-doc.org/en/stable/config.html#confval-highlight_language
    DEFAULT_HIGHLIGHT_STYLE: 'python'
}
