# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../../"))

project = 'KG-SaF: Building Complete and Curated Datasets for Machine Learning'
copyright = '2026, Ivan Diliso and Roberto Barile'
author = 'Ivan Diliso and Roberto Barile'
release = '1.6.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',  # Markdown support
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google/NumPy docstrings
    'sphinx.ext.viewcode'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}