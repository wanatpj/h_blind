LATEXFLAGS =
DVIPNGFLAGS = -D 150 -bg Transparent

TEXS = $(wildcard *.tex)
OBJS = $(TEXS:.tex=.png)

all: $(OBJS)

%.dvi: %.tex
	latex $(LATEXFLAGS) $<

%.png: %.dvi
	dvipng $(DVIPNGFLAGS) $< -o $@

clean:
	$(RM) *.log *.png *.aux
