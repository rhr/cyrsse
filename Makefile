%.c: ./%.pyx
	cython -3 $<

all: python

python: tree.c sse.c
	python ./setup.py build_ext --inplace

