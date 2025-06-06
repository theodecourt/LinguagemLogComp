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

## 4. Arquitetura e Implementação Final em Python

*(Nota: Embora o planejamento inicial considerasse Flex e Bison, a implementação final foi feita em Python para maior agilidade, clareza e facilidade na manipulação de dados e geração de arquivos.)*

O compilador foi desenvolvido em **Python**, seguindo um padrão de interpretador de percurso de árvore (*tree-walk interpreter*). A arquitetura do programa é dividida nos seguintes componentes principais:

* **Tokenizer (`Tokenizer`)**: Lê o código-fonte da linguagem `TripScheduler` e o converte em uma sequência de tokens.
* **Parser (`Parser`)**: Consome os tokens e constrói uma **Árvore Sintática Abstrata (AST)**. Cada nó na árvore representa uma declaração da linguagem.
* **Nós da AST (`Node` e suas subclasses)**: Um conjunto de classes que definem a estrutura da árvore. Cada classe (ex: `DestinoDec`, `DiaBlock`) possui um método `evaluate`.
* **Processador (`SymbolTable`)**: Atua como o cérebro da execução. O método `evaluate` de cada nó da AST é chamado para percorrer a árvore, coletar todos os dados da viagem (destino, datas, custos) e armazená-los de forma organizada.

### Geração de Relatório em PDF

O objetivo principal deste compilador não é gerar código de máquina, mas sim processar os dados do roteiro e gerar um relatório final legível para o usuário.

A principal saída do programa é um **relatório de viagem detalhado no formato PDF**. Para isso, o projeto utiliza a biblioteca Python **`fpdf2`**. O PDF gerado inclui:

1.  **Cabeçalho**: Com o nome e país do destino e o período da viagem.
2.  **Cronograma Detalhado**: Uma lista, dia a dia, de todas as atividades e custos planejados.
3.  **Resumo Financeiro**: Uma análise do orçamento total, o custo acumulado e o saldo restante, com um alerta caso o orçamento seja excedido.

---

## 5. Como Executar o Projeto

Para compilar e executar a sua linguagem `TripScheduler` e gerar o relatório em PDF, siga os passos abaixo.

### Requisitos

O projeto depende apenas da biblioteca `fpdf2`. Para instalar, crie um arquivo chamado `requirements.txt` na pasta do projeto com o seguinte conteúdo:

**`requirements.txt`**

```
fpdf2
```

Em seguida, instale a dependência executando o seguinte comando no seu terminal:

```bash
pip install -r requirements.txt
```

### Execução

#### 1.0 Crie um arquivo de roteiro, por exemplo, entrada.txt, com o seu planejamento:

```
// Meu roteiro de viagem dos sonhos

destino "Tóquio", país="Japão"
viagem de 2025-10-08 até 2025-10-20
budget 4000 USD

dia 8 {
    atividade "Chegada em Narita e trem para Shinjuku"
    custo 50 USD
    atividade "Jantar e explorar Shinjuku"
    custo 40 USD
}

dia 9 {
    atividade "Visita ao Templo Senso-ji em Asakusa"
    custo 10 USD
    atividade "Passeio na Tokyo Skytree"
    custo 30 USD
}

para cada dia in 10..12 {
    atividade "Explorar bairros (Shibuya, Harajuku, Akihabara)"
    custo 60 USD
}
```

#### 2.0 Execute o compilador via linha de comando, passando o arquivo de roteiro como argumento:

```bash
python3 trip_compiler.py entrada.txt
```

#### 3.0 Verifique a Saída: Após a execução, além de um resumo impresso no console, um novo arquivo chamado roteiro_da_viagem.pdf será criado na mesma pasta, contendo o seu roteiro completo e formatado.