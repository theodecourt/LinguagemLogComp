# TripScheduler – Gramática EBNF

Este documento apresenta a gramática EBNF completa da DSL **TripScheduler**, para descrever roteiros de viagem, atividades diárias e orçamento em dólares (USD).
---

## 1. Visão Geral

- **program**: sequência de declarações (`statement`)
- **destino_decl**: define destino (e opcionalmente país)
- **viagem_decl**: período da viagem (data de início e fim)
- **budget_decl**: orçamento total em USD
- **dia_block**: bloco de atividades e custos para um dia específico
- **loop_stmt**: iterações automáticas de atividades em um intervalo de dias

---

## 2. Gramática EBNF

```ebnf
(* TripLang EBNF Grammar *)

program        = { statement } ;

statement      = destino_decl
               | viagem_decl
               | budget_decl
               | dia_block
               | loop_stmt
               ;

// Declaração de destino com opção de país

destino_decl   = "destino" string_literal [ "," "país" "=" string_literal ] ;

// Período da viagem

viagem_decl    = "viagem" "de" date "até" date ;

// Orçamento em dólares (apenas inteiros)

budget_decl    = "budget" integer "USD" ;

// Bloco de dia usando chaves

dia_block      = "dia" integer "{" { activity_stmt cost_stmt } "}" ;

// Loop para dias, com chaves

loop_stmt      = "para" "cada" "dia" "in" range "{" { activity_stmt cost_stmt } "}" ;

// Declarações de atividade e custo (apenas inteiros)

activity_stmt  = "atividade" string_literal ;
cost_stmt      = "custo" integer "USD" ;

// Intervalo inclusivo

range          = integer ".." integer ;

// Data no formato YYYY-MM-DD

date           = digit digit digit digit "-" digit digit "-" digit digit ;

// Cadeia de caracteres entre aspas

string_literal = '"' { character } '"' ;

// Apenas inteiros (sem pontos decimais)

integer        = digit { digit } ;

digit          = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;

// Qualquer caractere exceto aspa dupla

character      = ? any character except '"' ? ;

```
