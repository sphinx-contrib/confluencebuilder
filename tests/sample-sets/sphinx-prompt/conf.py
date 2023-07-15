from docutils import nodes
import importlib


extensions = [
    'sphinxcontrib.confluencebuilder',
    'sphinx-prompt',
]


sphinx_prompt = importlib.import_module('sphinx-prompt')


class PromptDirectiveOverride(sphinx_prompt.PromptDirective):
    def run(self):
        text = '\n'.join(self.content)
        lang = self.options.get('language') or 'text'

        new_node = nodes.literal_block(text, text)
        new_node['language'] = lang
        return [ new_node ]


def setup(app):
    app.connect('builder-inited', builder_inited)


def builder_inited(app):
    if app.builder.name in ('html', 'latex'):
        return

    app.add_directive('prompt', PromptDirectiveOverride, override=True)
