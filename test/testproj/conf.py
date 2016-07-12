import sys
import os


sys.path.append(os.path.abspath(__file__ + "/../../../"))
extensions = ['sphinxcontrib.confluencebuilder']
confluence_publish = False
confluence_space_name = 'TEST'
confluence_parent_page = 'Documentation'
