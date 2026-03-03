# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from os import environ, path
from sys import path as syspath
import datetime

project = 'Temperature Sensing'
copyright = f"{datetime.datetime.now().year}, Edwin Lee"
author = 'Edwin Lee'
conf_dir = path.abspath(path.dirname(__file__))
repo_root = path.abspath(path.join(conf_dir, '..'))
# Add the parent directory to sys.path
syspath.insert(0, repo_root)

from firmware.sensing import __version__, __revision__
release = f"{__version__}.{__revision__}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
  "sphinx.ext.todo",
]
todo_include_todos = environ.get("READTHEDOCS", "") == ""

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'python_docs_theme'  # 'alabaster'
html_static_path = ['_static']

latex_documents = [
    ('assembly', 'assembly.tex', 'Temperature Sensor Assembly Instructions', 'Edwin Lee', 'manual'),
]
latex_elements = {
    'extraclassoptions': 'openany'
}
