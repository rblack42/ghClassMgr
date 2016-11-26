# -*- coding: utf-8 -*-
#
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.githubpages',
    'sphinx_exts.pylit',
]

templates_path = ['_templates']
source_suffix = '.rst'
# source_encoding = 'utf-8-sig'
master_doc = 'index'

code_base = '../code'

# General information about the project.
project = u'ghClassMgr'
copyright = u'2016, Roie R. Black'
author = u'Roie R. Black'
version = u'0.3'
release = u'0.3'
language = None
today_fmt = '%B %d, %Y'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

html_theme = 'alabaster'
html_theme_path = []
html_title = u'ghClassMgr v0.3'
html_logo = '_static/images/ACClogo.png'
html_favicon = '_static/images/favicon.ico'
html_static_path = ['_static']
html_last_updated_fmt = None
html_show_sphinx = True
html_show_copyright = True

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
     'papersize': 'letterpaper',
     'pointsize': '11pt',
}

latex_documents = [
    (master_doc, 'ghClassMgr.tex', u'ghClassMgr Documentation',
     u'Roie R. Black', 'manual'),
]

latex_logo = '_static/images/ACClogo.png'
