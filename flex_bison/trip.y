%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void yyerror(const char *s);
int yylex(void);

%}

%union {
    int ival;
    char *sval;
}

%token <sval> STRING DATE
%token <ival> INTEGER

%token DESTINO PAIS VIAGEM DE ATE BUDGET USD
%token DIA PARA CADA IN ATIVIDADE CUSTO
%token LBRACE RBRACE COMMA EQUAL DOTDOT

%start program

%%

program:
    /* vazio */
    | program statement
    ;

statement:
      destino_decl
    | viagem_decl
    | budget_decl
    | dia_block
    | loop_stmt
    ;

destino_decl:
    DESTINO STRING
    | DESTINO STRING COMMA PAIS EQUAL STRING
    ;

viagem_decl:
    VIAGEM DE DATE ATE DATE
    ;

budget_decl:
    BUDGET INTEGER USD
    ;

dia_block:
    DIA INTEGER LBRACE dia_conteudo RBRACE
    ;

loop_stmt:
    PARA CADA DIA IN range LBRACE dia_conteudo RBRACE
    ;

range:
    INTEGER DOTDOT INTEGER
    ;

dia_conteudo:
    /* vazio */
    | dia_conteudo activity_stmt
    | dia_conteudo cost_stmt
    ;

activity_stmt:
    ATIVIDADE STRING
    ;

cost_stmt:
    CUSTO INTEGER USD
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Erro de sintaxe: %s\n", s);
}

int main() {
    return yyparse();
}