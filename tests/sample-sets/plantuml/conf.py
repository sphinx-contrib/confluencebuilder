import os


extensions = [
    'sphinxcontrib.confluencebuilder',
    'sphinxcontrib.plantuml',
]


plantuml_output_format = 'svg'


dir_path = os.path.dirname(os.path.realpath(__file__))
plantuml_jar = os.path.join(dir_path, 'plantuml.jar')
plantuml = 'java -jar ' + plantuml_jar
