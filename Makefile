FC	= gfortran
FFLAGS	= -O3

%.c: ./%.pyx
	cython -3 $<

all: python

python: tree.c
	python ./setup.py build_ext --inplace

