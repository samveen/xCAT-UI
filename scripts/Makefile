ALL_PY=${wildcard *.py}
.PHONY: all clean run $(ALL_PY)

all: $(ALL_PY)

clean:
	rm -f *.pyc

$(ALL_PY):
	python -m py_compile $@

run:
	python cgiwrapper.py
