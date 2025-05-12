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
(* TripScheduler EBNF Grammar *)

program        = { statement } ;
(* Um programa consiste em zero ou mais declarações *)

statement      = destino_decl
               | viagem_decl
               | budget_decl
               | dia_block
               | loop_stmt
               ;
(* Tipos de declarações suportadas *)

(* Declaração de destino com opção de país *)
destino_decl   = "destino" string_literal ["," "país" "=" string_literal] ;
(* Ex.: destino "Lisboa", país="Portugal" *)

(* Período da viagem *)
viagem_decl    = "viagem" "de" date "até" date ;
(* Ex.: viagem de 2025-07-10 até 2025-07-20 *)

(* Orçamento em USD (apenas inteiros) *)
budget_decl    = "budget" integer "USD" ;
(* Ex.: budget 1500 USD *)

(* Bloco de dia usando chaves *)
dia_block      = "dia" integer "{" { activity_stmt cost_stmt } "}" ;
(* Ex.: dia 2 { atividade "City tour" custo 30 USD } *)

(* Loop de dias *)
loop_stmt      = "para" "cada" "dia" "in" range "{" { activity_stmt cost_stmt } "}" ;
(* Ex.: para cada dia in 5..7 { atividade "Futebol na praia" custo 0 USD } *)

(* Declaração de atividade *)
activity_stmt  = "atividade" string_literal ;
(* Ex.: atividade "Aula de surf em Ericeira" *)

(* Declaração de custo em USD *)
cost_stmt      = "custo" integer "USD" ;
(* Ex.: custo 60 USD *)

(* Intervalo inclusivo de dias *)
range          = integer ".." integer ;
(* Ex.: 5..7 *)

(* Data no formato YYYY-MM-DD *)
date           = digit digit digit digit "-" digit digit "-" digit digit ;
(* Ex.: 2025-07-10 *)

(* Cadeia de caracteres entre aspas *)
string_literal = '"' { character } '"' ;
(* Ex.: "Praia do Rosa" *)

(* Apenas inteiros (sem parte decimal) *)
integer        = digit { digit } ;
(* Ex.: 100 *)

digit          = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;

(* Qualquer caractere exceto aspa dupla *)
character      = ? any character except '"' ? ;


```

## 03. Utilização de Flex e Bison

### Análise Léxica – Flex (trip.l)

O Flex é responsável por identificar os tokens da linguagem, como palavras-chave (destino, viagem, budget), literais ("Lisboa"), números (1500) e símbolos ({, .., etc). Esses tokens são passados para o analisador sintático.

### Análise Sintática – Bison (trip.y)

O Bison define a gramática da linguagem (baseada em EBNF) e valida se a sequência de tokens está correta. Ele também pode ser estendido para construir uma árvore sintática ou executar ações (como imprimir ou armazenar dados).

### Geração dos arquivos

```
bison -d trip.y      # Gera trip.tab.c e trip.tab.h
flex trip.l          # Gera lex.yy.c
gcc trip.tab.c lex.yy.c -o trip_scheduler -lfl   # Compila o analisador
```

### Execução do programa

```
./trip_scheduler < entrada.txt
```

