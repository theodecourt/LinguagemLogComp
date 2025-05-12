%{
#include "trip.tab.h"
#include <string.h>
%}

digit   [0-9]
letter  [a-zA-Z]
quote   \"
ws      [ \t\n\r]+

%%
"destino"              { return DESTINO; }
"país"                 { return PAIS; }
"viagem"               { return VIAGEM; }
"de"                   { return DE; }
"até"                  { return ATE; }
"budget"               { return BUDGET; }
"USD"                  { return USD; }
"dia"                  { return DIA; }
"para"                 { return PARA; }
"cada"                 { return CADA; }
"in"                   { return IN; }
"atividade"            { return ATIVIDADE; }
"custo"                { return CUSTO; }

{digit}+               { yylval.ival = atoi(yytext); return INTEGER; }
{digit}{4}-{digit}{2}-{digit}{2} { yylval.sval = strdup(yytext); return DATE; }
\"([^"]*)\"            { yylval.sval = strdup(yytext + 1); yylval.sval[strlen(yylval.sval)-1] = 0; return STRING; }

"{"                    { return LBRACE; }
"}"                    { return RBRACE; }
","                    { return COMMA; }
"="                    { return EQUAL; }
".."                   { return DOTDOT; }

{ws}                   ;  // ignora espaços em branco
.                      { printf("Caractere desconhecido: %s\n", yytext); return yytext[0]; }

%%
int yywrap() { return 1; }