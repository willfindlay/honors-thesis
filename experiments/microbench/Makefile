.PHONY: all clean

all: null simple

clean:
	@rm -f null simple

null: null.c
	gcc -O2 -o null null.c

simple: simple.c
	gcc -O2 -o simple simple.c
