name   ?= thesis

.PHONY: all, clean, reset, $(name).bib

all: $(name).pdf

$(name).pdf: $(name).md ../bib ../figures
	compiler $(name).md

clean:
	rm -f $(name).pdf

reset: clean all
