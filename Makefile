# ============================================================
# Makefile — Compilador Homi
# Linguagem: Python 3 + PLY (Python Lex-Yacc)
# ============================================================

PYTHON     = python3
PIP        = pip3
MAIN       = gerador.py
LEXER      = lexer.py
PARSER     = parser.py
SEMANTICO  = semantico.py

# Arquivos gerados automaticamente pelo PLY
PLY_FILES  = parser.out parsetab.py __pycache__
YAML_OUT   = saida.yaml

# ============================================================
# Alvo padrão: instala dependências e executa o compilador
# ============================================================
.PHONY: all
all: install run

# ============================================================
# Instala a dependência PLY
# ============================================================
.PHONY: install
install:
	@echo ">>> Instalando dependências..."
	$(PIP) install ply --quiet
	@echo ">>> PLY instalado com sucesso."

# ============================================================
# Executa o compilador completo (lexer → parser → semântico → gerador)
# ============================================================
.PHONY: run
run:
	@echo ">>> Executando compilador Homi..."
	$(PYTHON) $(MAIN)

# ============================================================
# Testa cada fase individualmente
# ============================================================
.PHONY: test-lexico
test-lexico:
	@echo ">>> Testando Análise Léxica..."
	$(PYTHON) $(LEXER)

.PHONY: test-sintatico
test-sintatico:
	@echo ">>> Testando Análise Sintática..."
	$(PYTHON) $(PARSER)

.PHONY: test-semantico
test-semantico:
	@echo ">>> Testando Análise Semântica..."
	$(PYTHON) $(SEMANTICO)

.PHONY: test-gerador
test-gerador:
	@echo ">>> Testando Geração de Código YAML..."
	$(PYTHON) $(MAIN)

# Roda todos os testes em sequência
.PHONY: test
test: test-lexico test-sintatico test-semantico test-gerador
	@echo ">>> Todos os testes concluídos."

# ============================================================
# Compila um arquivo .homi passado pelo usuário
# Uso: make compile FILE=meu_script.homi
# ============================================================
.PHONY: compile
compile:
ifndef FILE
	@echo "[ERRO] Especifique o arquivo: make compile FILE=meu_script.homi"
else
	@echo ">>> Compilando '$(FILE)'..."
	$(PYTHON) -c "\
from lexer import lexer; \
from parser import parser; \
from semantico import AnalisadorSemantico; \
from gerador import GeradorYAML; \
import sys; \
codigo = open('$(FILE)', encoding='utf-8').read(); \
ast = parser.parse(codigo, lexer=lexer); \
erros = AnalisadorSemantico().analisar(ast); \
[print(e) for e in erros] if erros else print(GeradorYAML().gerar(ast)); \
"
endif

# ============================================================
# Remove arquivos gerados pelo PLY e pelo compilador
# ============================================================
.PHONY: clean
clean:
	@echo ">>> Limpando arquivos gerados..."
	rm -rf $(PLY_FILES) $(YAML_OUT)
	@echo ">>> Limpeza concluída."

# ============================================================
# Exibe ajuda
# ============================================================
.PHONY: help
help:
	@echo ""
	@echo "  Compilador Homi — comandos disponíveis:"
	@echo ""
	@echo "  make install        Instala a dependência PLY"
	@echo "  make run            Executa o compilador com os exemplos embutidos"
	@echo "  make test           Roda os testes de todas as fases"
	@echo "  make test-lexico    Testa somente o analisador léxico"
	@echo "  make test-sintatico Testa somente o analisador sintático"
	@echo "  make test-semantico Testa somente o analisador semântico"
	@echo "  make test-gerador   Testa somente o gerador de YAML"
	@echo "  make compile FILE=x Compila um arquivo .homi externo"
	@echo "  make clean          Remove arquivos temporários gerados pelo PLY"
	@echo ""
