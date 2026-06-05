import ply.lex as lex

# 1. Lista de Tokens (Vocabulário da linguagem Homi)
tokens = (
    'AUTOMACAO', 'QUANDO', 'SE', 'ENTAO', 'FIM',
    'ENTITY_ID', 'TEMPO', 'NUMERO', 'ESTADO', 'STRING',
    'OP_RELACIONAL', 'ATRIBUICAO', 'PALAVRA_TEMPO', 'SERVICO',
    'PONTO', 'ABRE_PAR', 'FECHA_PAR', 'PONTO_VIRGULA',
    'E', 'OU'
)

# 2. Regras de Expressões Regulares (Tokens Simples)
t_OP_RELACIONAL = r'==|!=|>=|<=|>|<'
t_ATRIBUICAO    = r'='
t_PONTO         = r'\.'
t_ABRE_PAR      = r'\('
t_FECHA_PAR     = r'\)'
t_PONTO_VIRGULA = r';'

# ------------------------------------------------------------
# 3. Regras Complexas (Palavras-chave e Valores)
#
# ATENÇÃO — ORDEM IMPORTA NO PLY:
#   O PLY ordena funções pelo tamanho do padrão regex (maior = maior prioridade).
#   Tokens mais específicos (palavras-chave, ENTITY_ID, TEMPO) devem vir
#   ANTES dos tokens genéricos (SERVICO, NUMERO) para não serem engolidos.
# ------------------------------------------------------------

# --- Palavras-chave da linguagem (maiúsculas iniciais) ---
def t_AUTOMACAO(t):
    r'Automacao'
    return t

def t_QUANDO(t):
    r'Quando'
    return t

def t_ENTAO(t):
    r'Entao'
    return t

def t_SE(t):
    r'Se'
    return t

def t_FIM(t):
    r'Fim'
    return t

# --- Operadores lógicos (palavras isoladas minúsculas) ---
def t_E(t):
    r'(?<![.\w])[Ee](?![.\w])'
    return t

def t_OU(t):
    r'(?<![.\w])[Oo][Uu](?![.\w])'
    return t

# --- Tokens de valor com padrões específicos ---
# TEMPO antes de NUMERO (r'\d+' seria match parcial em '10min')
def t_TEMPO(t):
    r'\d{2}:\d{2}|\d+(?:s|min|h)'
    return t

# ESTADO antes de SERVICO (on/off são [a-z]+ e seriam capturados como SERVICO)
def t_ESTADO(t):
    r'\b(?:on|off)\b'
    return t

# PALAVRA_TEMPO antes de SERVICO (mesmo motivo acima — 'tempo' = [a-z]+)
def t_PALAVRA_TEMPO(t):
    r'tempo'
    return t

# prioridade, o lexer tokenizaria 'light' como SERVICO e '.sala' como PONTO + SERVICO)
def t_ENTITY_ID(t):
    r'[a-z_][a-z0-9_]*\.[a-z0-9_]+'
    return t

# SERVICO: padrão genérico — deve ser o ÚLTIMO token alfabético
def t_SERVICO(t):
    r'[a-z_][a-z0-9_]*'
    return t


def t_NUMERO(t):
    r'\d+(?:\.\d+)?'
    t.value = float(t.value) if '.' in str(t.value) else int(t.value)
    return t

def t_STRING(t):
    r'\"[^\"]*\"'
    t.value = t.value[1:-1] 
    return t


#Um analisador léxico ignora espaços e linhas.
# Tratamento de Comentários, Espaços e Linhas
def t_COMENTARIO(t):
    r'\#.*'
    pass  # Ignora comentários de linha

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)  # Atualiza o contador de linhas

t_ignore = ' \t'  # Ignora espaços em branco e tabulações


# Tratamento de Erros Léxicos, token não reconhecido.
def t_error(t):
    print(f"[ERRO LÉXICO] Caractere não reconhecido '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)  # Modo pânico léxico: pula o caractere e continua

# Constrói o analisador léxico
lexer = lex.lex()

# ------------------------------------------------------------
# 6. Bloco de Teste Executável
# ------------------------------------------------------------
if __name__ == '__main__':
    codigo_teste = """
    Automacao "Ligar luz da sala"
    # Este é um comentário ignorado pelo lexer
    Quando tempo = 18:00
    Se sensor.luminosidade < 30 E switch.corredor == on
    Entao light.sala.turn_on();
        media_player.sala.volume_set(0.5);
    Fim
    @ # Isto deve gerar um erro léxico
    """

    print("--- INICIANDO ANÁLISE LÉXICA ---")
    lexer.input(codigo_teste)

    for token in lexer:
        print(f"Linha {token.lineno}: Tipo={token.type:<15} Valor='{token.value}'")
    print("--- FIM DA ANÁLISE ---")