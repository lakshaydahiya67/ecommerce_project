"""
Simple setup script for compiling Cython similarity module.

Usage:
    python setup.py build_ext --inplace
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

# Simple extension configuration
extensions = [
    Extension(
        "similarity",
        ["similarity.pyx"],
        include_dirs=[np.get_include()]
    )
]

# Basic setup
setup(
    ext_modules=cythonize(extensions, language_level=3),
    zip_safe=False
)