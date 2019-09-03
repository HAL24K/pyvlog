import os
import sys

sys.path.insert(0, os.path.abspath('../..'))
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.napoleon']

project = 'pyvlog'
copyright = '2019, Samuel Blake'
author = 'Samuel Blake'
version = '0.1'
release = '0.1'
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'sphinx'
html_theme = 'default'
html_static_path = []