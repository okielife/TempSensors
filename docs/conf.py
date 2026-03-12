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
    'sphinx.ext.autodoc',
]
todo_include_todos = environ.get("READTHEDOCS", "") == ""
autodoc_mock_imports = [
    'ds18x20',
    'machine',
    'network',
    'onewire',
    'time',
    'ubinascii',
    'ujson',
    'urequests',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

tried_themes_with_pip_packages = {
    'alabaster': '',
    'cloud': 'cloud-sptheme',
    'groundwork': 'groundwork-sphinx-theme',
    'nameko': 'sphinx-nameko-theme',
    'pdj': 'phinx-pdj-theme',  # something wrong here
    'python_docs_theme': 'python-docs-theme',
    'sphinx_rtd_theme': 'sphinx-rtd-theme'
}
html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']

build_pinout = environ.get("BUILD_PINOUT", "") != ""
if build_pinout:  # build the pinout specially with xelatex
    latex_engine = 'xelatex'
    latex_documents = [
        ('pinout', 'pinout.tex', 'Temperature Sensor Pinout Diagram', 'Edwin Lee', 'manual'),
    ]
    latex_elements = {
        'extraclassoptions': 'openany,landscape'
    }
else:  # normal operation build the main assembly instructions with latex
    latex_engine = 'pdflatex'
    latex_documents = [
        ('assembly', 'assembly.tex', 'Temperature Sensor Assembly Instructions', 'Edwin Lee', 'manual'),
    ]
    latex_elements = {
        'extraclassoptions': 'openany'
    }
