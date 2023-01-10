from setuptools import setup
from Cython.Build import cythonize
setup(
    name='Cheat',
    ext_modules=cythonize('packages/*.py', compiler_directives={'language_level': '3'}),
)