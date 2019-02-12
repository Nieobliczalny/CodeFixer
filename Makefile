all: lexer

lexer: CxxLexer

CxxLexer: CxxLexer.c
	g++ -Wall -Wextra CxxLexer.c -o CxxLexer

CxxLexer.c: CxxLexer.l CxxLexing.hxx CxxLexing.cxx
	flex --outfile=CxxLexer.c CxxLexer.l

clean:
	-rm -f CxxLexer CxxLexer.c