import ply.yacc as yacc

# Importa a lista de tokens e a instância do lexer do ficheiro lexer.py
from lexer import tokens, lexer

# ------------------------------------------------------------
# 1. Regra Inicial (Símbolo S)
# ------------------------------------------------------------
def p_programa(p):
    '''programa : automacao'''
    p[0] = {'node': 'programa', 'filho': p[1]}

# ------------------------------------------------------------
# 2. Estrutura da Automação
# ------------------------------------------------------------
def p_automacao(p):
    '''automacao : AUTOMACAO STRING quando se entao FIM
                 | AUTOMACAO STRING quando entao FIM'''
    if len(p) == 7:
        p[0] = {'node': 'automacao', 'nome': p[2], 'quando': p[3], 'se': p[4], 'entao': p[5]}
    else:
        p[0] = {'node': 'automacao', 'nome': p[2], 'quando': p[3], 'se': None, 'entao': p[4]}

# ------------------------------------------------------------
# 3. Bloco Quando (Gatilhos)
# ------------------------------------------------------------
def p_quando(p):
    '''quando : QUANDO gatilho'''
    p[0] = p[2]

def p_gatilho_estado(p):
    '''gatilho : ENTITY_ID OP_RELACIONAL ESTADO'''
    p[0] = {'node': 'gatilho_estado', 'entidade': p[1], 'operador': p[2], 'estado': p[3]}

def p_gatilho_tempo(p):
    '''gatilho : PALAVRA_TEMPO ATRIBUICAO TEMPO'''
    p[0] = {'node': 'gatilho_tempo', 'valor': p[3]}

# ------------------------------------------------------------
# 4. Bloco Se (Condições Múltiplas)
# ------------------------------------------------------------
def p_se(p):
    '''se : SE condicoes'''
    p[0] = p[2]

# Regra recursiva: permite "condicao E condicao OU condicao"
def p_condicoes(p):
    '''condicoes : condicao E condicoes
                 | condicao OU condicoes
                 | condicao'''
    if len(p) == 4:
        p[0] = {'node': 'operacao_logica', 'esq': p[1], 'operador': p[2], 'dir': p[3]}
    else:
        p[0] = p[1]

def p_condicao(p):
    '''condicao : ENTITY_ID OP_RELACIONAL NUMERO
                | ENTITY_ID OP_RELACIONAL ESTADO
                | ENTITY_ID OP_RELACIONAL STRING'''
    p[0] = {'node': 'condicao', 'entidade': p[1], 'operador': p[2], 'valor': p[3]}

# ------------------------------------------------------------
# 5. Bloco Entao (Ações com Parâmetros)
# ------------------------------------------------------------
def p_entao(p):
    '''entao : ENTAO acoes'''
    p[0] = p[2]

def p_acoes_lista(p):
    '''acoes : acao acoes
             | acao'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_acao(p):
    '''acao : ENTITY_ID PONTO SERVICO ABRE_PAR parametro FECHA_PAR PONTO_VIRGULA'''
    p[0] = {'node': 'acao', 'entidade': p[1], 'servico': p[3], 'parametro': p[5]}

# Define o que pode ser um parâmetro
def p_parametro(p):
    '''parametro : NUMERO
                 | STRING
                 | TEMPO
                 | empty'''
    p[0] = p[1]

# Regra auxiliar para parênteses vazios ()
def p_empty(p):
    'empty :'
    pass

# ------------------------------------------------------------
# 6. Tratamento de Erros e Recuperação (Modo Pânico)
# ------------------------------------------------------------
def p_error(p):
    if p:
        print(f"[ERRO SINTÁTICO] Token inesperado '{p.value}' (tipo: {p.type}) na linha {p.lineno}.")
        print("  >> Modo Pânico ativado: descartando tokens até ';' ou 'Fim'...")

        # Descarta tokens até encontrar um ponto de sincronização seguro
        while True:
            tok = parser.token()
            if not tok or tok.type in ('PONTO_VIRGULA', 'FIM'):
                break

        parser.restart()
    else:
        print("[ERRO SINTÁTICO] Fim de arquivo inesperado. O programa deve terminar com 'Fim'.")

# Constrói o analisador sintático
parser = yacc.yacc()

# ------------------------------------------------------------
# Bloco de Teste
# ------------------------------------------------------------
if __name__ == '__main__':
    import pprint

    # Teste válido com múltiplas ações e condições compostas
    codigo_valido = """
    Automacao "Modo Cinema"
    Quando tempo = 20:00
    Se sensor.luminosidade < 10 E sensor.tv == on
    Entao media_player.sala.volume_set(0.11);
        light.sanca.turn_off();
        media_player.sala.delay(4min);
    Fim
    """

    # Teste com erro sintático (falta o ponto e vírgula)
    codigo_com_erro = """
    Automacao "Teste Erro"
    Quando tempo = 08:00
    Entao light.sala.turn_on()
        light.quarto.turn_off();
    Fim
    """

    print("--- TESTE 1: CÓDIGO VÁLIDO ---")
    ast = parser.parse(codigo_valido, lexer=lexer)
    pprint.pprint(ast, sort_dicts=False)

    print("\n--- TESTE 2: CÓDIGO COM ERRO SINTÁTICO ---")
    ast2 = parser.parse(codigo_com_erro, lexer=lexer)
    pprint.pprint(ast2, sort_dicts=False)

    print("--- FIM DA ANÁLISE ---")