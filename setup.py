from setuptools import setup
from setuptools.extension import Extension

extensions = [
    Extension(
        'tree',
        ['tree.c'],
        define_macros=[('CYTHON_TRACE', '1')]
    ),
    Extension(
        'sse',
        ['sse.c'],
        libraries = ['gsl', 'blas', 'nlopt'],
        define_macros=[('CYTHON_TRACE', '1')]
    ),
    ## Extension(
    ##     'odeiv',
    ##     ['odeiv.c'],
    ##     libraries = ['gsl', 'blas']
    ## ),
]

setup(
  name = 'cyrsse',
  ext_modules = extensions
)
