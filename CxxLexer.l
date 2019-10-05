%{
//**************************** RACAL Confidential ****************************
//
//	  Title:			Miniature lexer for C++ parser.
//
//	  File Name:		CxxLexer.l
//
//	  Author:			E.D.Willink
//
//	  SCCS:				%W% %G%
//
//	  Latest Modification:
// EDW	1.1		Date:	26-Aug-1999		Original - trimmed back from FogLexer.l
//
//	This is a complete lexer for C++, intended for use with CxxParser.y.
//	All actions are done by macros, so that there is some chance that customisation
//	can be performed within the bounds of the CxxLexer.inc.h and CxxLexer.inc.c
//	include files.
//END
//
#include "CxxLexing.hxx"
%}
%option noyywrap
%a 5000
%e 1500
%n 1000
%o 10000
%p 10000
ws								[ \f\v\t]

digit							[0-9]
hex								[0-9A-Fa-f]
letter							[A-Z_a-z]
simple_escape_sequence			(\\\'|\\\"|\\\?|\\\\|\\a|\\b|\\f|\\n|\\r|\\t|\\v)
octal_escape_sequence			(\\[0-7]|\\[0-7][0-7]|\\[0-7][0-7][0-7])
hexadecimal_escape_sequence		(\\x{hex}+)
escape_sequence					({simple_escape_sequence}|{octal_escape_sequence}|{hexadecimal_escape_sequence})
universal_character_name		(\\u{hex}{hex}{hex}{hex}|\\U{hex}{hex}{hex}{hex}{hex}{hex}{hex}{hex})
non_digit						({letter}|{universal_character_name})
identifier						({non_digit}({non_digit}|{digit})*)

character_lit					(L?\'([^\'\\\n]|\\.)*)
character_literal				({character_lit}\')

string_lit						(L?\"([^\"\\\n]|\\.)*)
string_literal					({string_lit}\")

pp_number						(\.?{digit}({digit}|{non_digit}|[eE][-+]|\.)*)
%%
^{ws}*"#".*						{ /* Throw away preprocessor lines - hopefully only #line and equivalent. */ }

{character_lit}\'				{ yylval = addSymbol(yytext, yyleng); return T_CHARACTER_LITERAL; };
{character_lit}\\				{ yylval = addSymbol(yytext, yyleng - 1); return T_CHARACTER_LITERAL; };
{character_lit}					{ yylval = addSymbol(yytext, yyleng); return T_CHARACTER_LITERAL; };

{string_lit}\"					{ yylval = addSymbol(yytext, yyleng - 1); return T_STRING_LITERAL; };
{string_lit}\\					{ yylval = addSymbol(yytext, yyleng - 1); return T_STRING_LITERAL; };
{string_lit}					{ yylval = addSymbol(yytext, yyleng); return T_STRING_LITERAL; };

"asm"							{ return (T_ASM); }
"auto"							{ return (T_AUTO); }
"bool"							{ return (T_BOOL); }
"break"							{ return (T_BREAK); }
"case"							{ return (T_CASE); }
"catch"							{ return (T_CATCH); }
"char"							{ return (T_CHAR); }
"class"							{ return (T_CLASS); }
"const"							{ return (T_CONST); }
"const_cast"					{ return (T_CONST_CAST); }
"continue"						{ return (T_CONTINUE); }
"default"						{ return (T_DEFAULT); }
"delete"						{ return (T_DELETE); }
"do"							{ return (T_DO); }
"double"						{ return (T_DOUBLE); }
"dynamic_cast"					{ return (T_DYNAMIC_CAST); }
"else"							{ return (T_ELSE); }
"enum"							{ return (T_ENUM); }
"explicit"						{ return (T_EXPLICIT); }
"export"						{ return (T_EXPORT); }
"extern"						{ return (T_EXTERN); }
"false"							{ return (T_FALSE); }
"float"							{ return (T_FLOAT); }
"for"							{ return (T_FOR); }
"friend"						{ return (T_FRIEND); }
"goto"							{ return (T_GOTO); }
"if"							{ return (T_IF); }
"inline"						{ return (T_INLINE); }
"int"							{ return (T_INT); }
"long"							{ return (T_LONG); }
"mutable"						{ return (T_MUTABLE); }
"namespace"						{ return (T_NAMESPACE); }
"new"							{ return (T_NEW); }
"operator"						{ return (T_OPERATOR); }
"private"						{ return (T_PRIVATE); }
"protected"						{ return (T_PROTECTED); }
"public"						{ return (T_PUBLIC); }
"register"						{ return (T_REGISTER); }
"reinterpret_cast"				{ return (T_REINTERPRET_CAST); }
"return"						{ return (T_RETURN); }
"short"							{ return (T_SHORT); }
"signed"						{ return (T_SIGNED); }
"sizeof"						{ return (T_SIZEOF); }
"static"						{ return (T_STATIC); }
"static_cast"					{ return (T_STATIC_CAST); }
"struct"						{ return (T_STRUCT); }
"switch"						{ return (T_SWITCH); }
"template"						{ return (T_TEMPLATE); }
"this"							{ return (T_THIS); }
"throw"							{ return (T_THROW); }
"true"							{ return (T_TRUE); }
"try"							{ return (T_TRY); }
"typedef"						{ return (T_TYPEDEF); }
"typeid"						{ return (T_TYPEID); }
"typename"						{ return (T_TYPENAME); }
"union"							{ return (T_UNION); }
"unsigned"						{ return (T_UNSIGNED); }
"using"							{ return (T_USING); }
"virtual"						{ return (T_VIRTUAL); }
"void"							{ return (T_VOID); }
"volatile"						{ return (T_VOLATILE); }
"wchar_t"						{ return (T_WCHAR_T); }
"while"							{ return (T_WHILE); }

"::"							{ return (T_SCOPE); }
"..."							{ return (T_ELLIPSIS); }
"<<"							{ return (T_SHL); }
">>"							{ return (T_SHR); }
"=="							{ return (T_EQ); }
"!="							{ return (T_NE); }
"<="							{ return (T_LE); }
">="							{ return (T_GE); }
"&&"							{ return (T_LOG_AND); }
"||"							{ return (T_LOG_OR); }
"++"							{ return (T_INC); }
"--"							{ return (T_DEC); }
"->*"							{ return (T_ARROW_STAR); }
"->"							{ return (T_ARROW); }
".*"							{ return (T_DOT_STAR); }
"+="							{ return (T_ASS_ADD); }
"-="							{ return (T_ASS_SUB); }
"*="							{ return (T_ASS_MUL); }
"/="							{ return (T_ASS_DIV); }
"%="							{ return (T_ASS_MOD); }
"^="							{ return (T_ASS_XOR); }
"&="							{ return (T_ASS_AND); }
"|="							{ return (T_ASS_OR); }
">>="							{ return (T_ASS_SHR); }
"<<="							{ return (T_ASS_SHL); }

{pp_number}						{ yylval = addSymbol(yytext, yyleng); return T_NUMBER; }

{identifier}					{ yylval = addSymbol(yytext, yyleng); return T_ID; }

{escape_sequence}				|
{universal_character_name}		{ yylval = addSymbol(yytext, yyleng); return T_ESCAPED; }

\n								|
\r                              |
{ws}							{ return (yytext[0]); }
.								{ return (yytext[0]); }

%%
#include "CxxLexing.cxx"
