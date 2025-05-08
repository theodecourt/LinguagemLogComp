# TripScheduler – Gramática EBNF

Este documento apresenta a gramática EBNF completa da DSL **TripScheduler**, para descrever roteiros de viagem, atividades diárias e orçamento em dólares (USD). Você pode copiar e colar este texto em qualquer plataforma que suporte Markdown.

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
(* TripScheduler EBNF *)

program        = { statement } ;

statement      = destino_decl
               | viagem_decl
               | budget_decl
               | dia_block
               | loop_stmt
               ;

destino_decl   = "destino" string_literal
                   [ "," "país" "=" string_literal ]
               ;
               (* Ex.: destino "Lisboa", país="Portugal" *)

viagem_decl    = "viagem" "de" date "até" date ;
               (* Ex.: viagem de 2025-07-10 até 2025-07-20 *)

budget_decl    = "budget" number "USD" ;
               (* Ex.: budget 1500 USD *)

dia_block      = "dia" integer "{"
                    { activity_stmt cost_stmt }
                 "}"
               ;
               (* Ex.:
                  dia 2 {
                    atividade "City tour"
                    custo 30.0 USD
                    atividade "Jantar típico"
                    custo 25.0 USD
                  }
               *)

loop_stmt      = "para" "cada" "dia" "in" range "{"
                    { activity_stmt cost_stmt }
                 "}"
               ;
               (* Ex.:
                  para cada dia in 5..7 {
                    atividade "Partida de futebol na praia"
                    custo 0.0 USD
                  }
               *)

activity_stmt  = "atividade" string_literal ;
               (* Ex.: atividade "Aula de surf em Ericeira" *)

cost_stmt      = "custo" number "USD" ;
               (* Ex.: custo 60.0 USD *)

range          = integer ".." integer ;
               (* Ex.: 5..7 — dias 5, 6 e 7 *)
               
date           = digit digit digit digit "-" digit digit "-" digit digit ;
               (* Ex.: 2025-07-10 *)

string_literal = '"' { character } '"' ;
               (* Ex.: "Praia do Rosa" *)

number         = integer [ "." integer ] ;
               (* Ex.: 100, 45.5 *)

integer        = digit { digit } ;
digit          = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;

character      = ? any character except '"' ? ;

(* Comentários opcionais no nível do lexer
   Ex.: linhas iniciando com ‘#’ são ignoradas. *)
```
