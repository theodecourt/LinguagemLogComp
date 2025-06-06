import sys
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos


class SymbolTable:
    def __init__(self):
        self.table = {}
    def getValue(self, key):
        if key in self.table:
            return self.table[key]
        raise ValueError(f"'{key}' não foi definido no roteiro.")
    def setValue(self, key, value):
        self.table[key] = value
    def create_keys(self):
        self.setValue('destino', None)
        self.setValue('pais', None)
        self.setValue('data_inicio', None)
        self.setValue('data_fim', None)
        self.setValue('budget', 0)
        self.setValue('total_custo', 0)
        self.setValue('itinerario', {})
        self.setValue('current_day', 0)

    def generate_pdf(self, filename="roteiro_viagem.pdf"):
        """Cria um PDF com o cronograma e o resumo da viagem."""
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, "Roteiro de Viagem", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(5)

        pdf.set_font("Helvetica", "", 12)
        destino = self.getValue('destino')
        pais = self.getValue('pais')
        inicio = self.getValue('data_inicio')
        fim = self.getValue('data_fim')
        
        destino_str = destino if destino else "N/A"
        if pais:
            destino_str += f", {pais}"

        periodo_str = f"De {inicio if inicio else 'N/A'} até {fim if fim else 'N/A'}"

        pdf.cell(0, 6, destino_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.cell(0, 6, periodo_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10) 

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Cronograma Detalhado", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        itinerario = self.getValue('itinerario')
        
        for dia in sorted(itinerario.keys()):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, f"Dia {dia}:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", 11)
            for item in itinerario[dia]:
                pdf.multi_cell(0, 6, f"  - {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

        pdf.ln(10)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Resumo Financeiro", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 11)
        
        budget = self.getValue('budget')
        custo = self.getValue('total_custo')
        saldo = budget - custo
        
        pdf.cell(0, 6, f"Orçamento Total: ${budget} USD", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 6, f"Custo Total Planejado: ${custo} USD", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_font("Helvetica", "B", 11)
        if saldo >= 0:
            pdf.cell(0, 8, f"Saldo Restante: ${saldo} USD", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 8, f"ATENÇÃO: Orçamento excedido em ${-saldo} USD!", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.output(filename)
        print(f"\nPDF '{filename}' gerado com sucesso!")


class Token:
    def __init__(self, token_type: str, value): self.token_type = token_type; self.value = value
    def __repr__(self): return f"Token({self.token_type!r}, {self.value!r})"

class Node:
    def __init__(self, value, children: list): self.value = value; self.children = children
    def evaluate(self, st): pass

class Program(Node):
    def evaluate(self, st: SymbolTable):
        for child in self.children: child.evaluate(st)

class DestinoDec(Node):
    def __init__(self, value, children: list): super().__init__(value, children)
    def evaluate(self, st: SymbolTable):
        st.setValue('destino', self.value)
        if self.children: st.setValue('pais', self.children[0])

class ViagemDec(Node):
    def evaluate(self, st: SymbolTable): st.setValue('data_inicio', self.children[0]); st.setValue('data_fim', self.children[1])

class BudgetDec(Node):
    def evaluate(self, st: SymbolTable): st.setValue('budget', self.value)

class DiaBlock(Node):
    def evaluate(self, st: SymbolTable):
        st.setValue('current_day', self.value)
        for child in self.children: child.evaluate(st)

class LoopStmt(Node):
    def evaluate(self, st: SymbolTable):
        start_day, end_day = self.value
        for dia in range(start_day, end_day + 1):
            st.setValue('current_day', dia)
            for child in self.children: child.evaluate(st)

class Atividade(Node):
    def evaluate(self, st: SymbolTable):
        dia = st.getValue('current_day'); itinerario = st.getValue('itinerario')
        if dia not in itinerario: itinerario[dia] = []
        itinerario[dia].append(f"Atividade: {self.value}")

class Custo(Node):
    def evaluate(self, st: SymbolTable):
        custo_atual = st.getValue('total_custo'); novo_custo = custo_atual + self.value
        st.setValue('total_custo', novo_custo)
        dia = st.getValue('current_day'); itinerario = st.getValue('itinerario')
        if dia not in itinerario: itinerario[dia] = []
        itinerario[dia].append(f"Custo: ${self.value} USD")

class NoOp(Node):
    def evaluate(self, st: SymbolTable): pass


class PrePro:
    @staticmethod
    def filter(s: str) -> str: return re.sub(r'//.*$', '', s, flags=re.MULTILINE)

class Tokenizer:
    def __init__(self, source: str): self.source = source; self.position = 0; self.next = self._select_next()

    def _select_next(self):
        while self.position < len(self.source) and self.source[self.position].isspace(): self.position += 1
        if self.position >= len(self.source): return Token("EOF", "")

        current_char = self.source[self.position]

        if current_char.isalpha():
            identifier = ""
            while self.position < len(self.source) and self.source[self.position].isalpha(): identifier += self.source[self.position]; self.position += 1
            keywords = {"destino": "DESTINO", "país": "PAIS", "viagem": "VIAGEM", "de": "DE", "até": "ATE", "budget": "BUDGET", "USD": "USD", "dia": "DIA", "para": "PARA", "cada": "CADA", "in": "IN", "atividade": "ATIVIDADE", "custo": "CUSTO"}
            return Token(keywords.get(identifier, "IDENTIFIER"), identifier)
        
        if current_char.isdigit():
            if re.match(r'\d{4}-\d{2}-\d{2}', self.source[self.position:]):
                date_str = self.source[self.position:self.position+10]; self.position += 10
                return Token("DATE", date_str)
            num_str = ""

            while self.position < len(self.source) and self.source[self.position].isdigit(): num_str += self.source[self.position]; self.position += 1

            return Token("INTEGER", int(num_str))
        
        if current_char == '"':
            self.position += 1; string = ""

            while self.position < len(self.source) and self.source[self.position] != '"': string += self.source[self.position]; self.position += 1

            self.position += 1

            return Token("STRING", string)
        
        if self.source[self.position:self.position+2] == '..': self.position += 2; return Token("RANGE", "..")

        symbols = {"{": "LBRACE", "}": "RBRACE", ",": "COMMA", "=": "ASSIGN"}

        if current_char in symbols: self.position += 1; return Token(symbols[current_char], current_char)

        raise ValueError(f"Caractere inesperado: {current_char}")


class Parser:
    @staticmethod
    def eat(token_type):
        if Parser.t.next.token_type == token_type:
            token_value = Parser.t.next.value; Parser.t.next = Parser.t._select_next()
            return token_value
        else: raise ValueError(f"Erro de Sintaxe: esperava {token_type}, encontrou {Parser.t.next.token_type}")

    @staticmethod
    def parse_dia_conteudo():
        conteudo = []; Parser.eat("LBRACE")
        while Parser.t.next.token_type != "RBRACE":
            if Parser.t.next.token_type == "ATIVIDADE":
                Parser.eat("ATIVIDADE"); descricao = Parser.eat("STRING")
                conteudo.append(Atividade(descricao, []))
            elif Parser.t.next.token_type == "CUSTO":
                Parser.eat("CUSTO"); valor = Parser.eat("INTEGER"); Parser.eat("USD")
                conteudo.append(Custo(valor, []))
            else: raise ValueError(f"Comando inesperado dentro de bloco de dia: {Parser.t.next.token_type}")
        Parser.eat("RBRACE")
        return conteudo
    
    @staticmethod
    def parse_statement():
        token_type = Parser.t.next.token_type

        if token_type == "DESTINO":
            Parser.eat("DESTINO"); nome = Parser.eat("STRING"); pais = None
            if Parser.t.next.token_type == "COMMA": Parser.eat("COMMA"); Parser.eat("PAIS"); Parser.eat("ASSIGN"); pais = Parser.eat("STRING")
            return DestinoDec(nome, [pais] if pais else [])
        
        elif token_type == "VIAGEM":
            Parser.eat("VIAGEM"); Parser.eat("DE"); inicio = Parser.eat("DATE"); Parser.eat("ATE"); fim = Parser.eat("DATE")
            return ViagemDec(None, [inicio, fim])
        
        elif token_type == "BUDGET":
            Parser.eat("BUDGET"); valor = Parser.eat("INTEGER"); Parser.eat("USD")
            return BudgetDec(valor, [])
        
        elif token_type == "DIA":
            Parser.eat("DIA"); dia_num = Parser.eat("INTEGER"); conteudo = Parser.parse_dia_conteudo()
            return DiaBlock(dia_num, conteudo)
        
        elif token_type == "PARA":
            Parser.eat("PARA"); Parser.eat("CADA"); Parser.eat("DIA"); Parser.eat("IN")
            start_day = Parser.eat("INTEGER"); Parser.eat("RANGE"); end_day = Parser.eat("INTEGER")
            conteudo = Parser.parse_dia_conteudo()
            return LoopStmt((start_day, end_day), conteudo)
        return NoOp(None, [])
    
    @staticmethod
    def run(source: str):
        if not source.strip(): return NoOp(None, [])
        Parser.t = Tokenizer(source); statements = []
        while Parser.t.next.token_type != "EOF": statements.append(Parser.parse_statement())
        return Program(None, statements)


if __name__ == "__main__":
    if len(sys.argv) < 2: print("Uso: python seu_arquivo.py <arquivo_de_roteiro>"); sys.exit(1)
    arquivo = sys.argv[1]
    try:
        with open(arquivo, "r", encoding="utf-8") as f: source = PrePro.filter(f.read())
    except FileNotFoundError: print(f"Erro: Arquivo '{arquivo}' não encontrado."); sys.exit(1)
    ast = Parser.run(source)
    st = SymbolTable()
    st.create_keys()
    ast.evaluate(st)
    st.generate_pdf("roteiro_da_viagem.pdf")