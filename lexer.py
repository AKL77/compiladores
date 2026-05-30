import ply.lex as lex

# ------------------------------------------------------------
# 1. Lista de Tokens (Vocabulário da linguagem Homi)
# ------------------------------------------------------------
tokens = (
    'AUTOMACAO', 'QUANDO', 'SE', 'ENTAO', 'FIM',
    'ENTITY_ID', 'TEMPO', 'NUMERO', 'ESTADO', 'STRING',
    'OP_RELACIONAL', 'ATRIBUICAO', 'PALAVRA_TEMPO', 'SERVICO',
    'PONTO', 'ABRE_PAR', 'FECHA_PAR', 'PONTO_VIRGULA'
)

# ------------------------------------------------------------
# 2. Regras de Expressões Regulares (Tokens Simples)
# ------------------------------------------------------------
t_OP_RELACIONAL = r'==|!=|>=|<=|>|<'
t_ATRIBUICAO    = r'='
t_PONTO         = r'\.'
t_ABRE_PAR      = r'\('
t_FECHA_PAR     = r'\)'
t_PONTO_VIRGULA = r';'

# ------------------------------------------------------------
# 3. Regras Complexas (Palavras-chave e Valores)
# A ordem de declaração das funções importa no PLY.
# ------------------------------------------------------------
def t_AUTOMACAO(t):
    r'Automacao'
    return t

def t_QUANDO(t):
    r'Quando'
    return t

def t_SE(t):
    r'Se'
    return t

def t_ENTAO(t):
    r'Entao'
    return t

def t_FIM(t):
    r'Fim'
    return t

def t_ESTADO(t):
    r'\b(on|off)\b'
    return t

def t_TEMPO(t):
    r'\d{2}:\d{2}|\d+(s|min|h)'
    return t

# isso aqui ta omega sus 
def t_PALAVRA_TEMPO(t):
    r'tempo'
    return t

def t_ENTITY_ID(t):
    r'[a-z_]+\.[a-z0-9_]+'
    return t

def t_SERVICO(t):
    r'[a-z_]+'
    return t

def t_NUMERO(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_STRING(t):
    r'\"[^\"]*\"'
    t.value = t.value[1:-1] # Remove as aspas para a AST
    return t

# ------------------------------------------------------------
# 4. Tratamento de Comentários, Espaços e Linhas
# ------------------------------------------------------------
def t_COMENTARIO(t):
    r'\#.*'
    pass # O comando 'pass' diz ao lexer para ignorar este padrão

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value) # Atualiza o contador de linhas

t_ignore = ' \t' # Ignora espaços em branco e tabulações

# ------------------------------------------------------------
# 5. Tratamento de Erros Léxicos
# ------------------------------------------------------------
def t_error(t):
    print(f"[ERRO LÉXICO] Caractere não reconhecido '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1) # Pula o caractere inválido e continua a leitura (Modo Pânico léxico)

# Constrói o analisador léxico
lexer = lex.lex()

# ------------------------------------------------------------
# 6. Bloco de Teste Executável
# ------------------------------------------------------------
if __name__ == '__main__':
    # Script de teste dentro do escopo definido
    codigo_teste = """
    Automacao "Ligar luz da sala"
    # Este é um comentário ignorado pelo lexer
    Quando tempo = 18:00
    Se sensor.luminosidade < 30
    Entao light.sala.turn_on();
    Fim
    @ # Isto deve gerar um erro léxico
    """

    print("--- INICIANDO ANÁLISE LÉXICA ---")
    lexer.input(codigo_teste)
    
    for token in lexer:
        print(f"Linha {token.lineno}: Tipo={token.type}, Valor='{token.value}'")
    print("--- FIM DA ANÁLISE ---")