from pathlib import Path


extensions = [
    'sphinxcontrib.confluencebuilder',
    'sphinxcontrib.plantuml',
]


plantuml_output_format = 'svg'


dir_path = Path(__file__).parent.resolve()
plantuml_jar = dir_path / 'plantuml.jar'
plantuml = 'java -jar ' + str(plantuml_jar)
