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
sitemap_filename = "sitemap.xml"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.mathjax',
    'sphinx_sitemap',
    'myst_parser',  # Markdown support
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google/NumPy docstrings
    'sphinx.ext.viewcode'
]

templates_path = ['_templates']
exclude_patterns = []




# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_baseurl = "https://ivandiliso.github.io/kg-saf/"
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = 'KG-SaF: Official Documentation'
html_context = {
    "description": "Documentation for the KG-SaF-Data and KG-SaF-JDeX Workflow: Building Complete and Curated Datasets for Machine Learning"
}

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}