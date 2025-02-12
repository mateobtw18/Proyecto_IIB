# Configuration file for the Sphinx documentation builder.
# For a full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Agregar la ruta donde está el código fuente para que Sphinx lo encuentre
sys.path.insert(0, os.path.abspath('../../Código'))

# -- Project information -----------------------------------------------------
project = 'Fractales en el plano complejo'
copyright = '2025, Mateo Cumbal, Daniel Flores, Johann Pasquel, Luis Tipán'
author = 'Mateo Cumbal, Daniel Flores, Johann Pasquel, Luis Tipán'
release = '12/02/2025'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',  # Generar documentación a partir de docstrings
    'sphinx.ext.napoleon', # Soporte para docstrings estilo Google y NumPy
    'sphinx.ext.viewcode'  # Agrega enlaces al código fuente en la documentación
]

templates_path = ['_templates']
exclude_patterns = []

# Idioma de la documentación
language = 'es'

# -- Options for HTML output -------------------------------------------------
# Tema más profesional (Read The Docs Theme)
html_theme = 'sphinx_rtd_theme'

# Directorio para archivos estáticos (CSS, imágenes, etc.)
html_static_path = ['_static']
html_show_sphinx = False
