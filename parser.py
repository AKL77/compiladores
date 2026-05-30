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
# 4. Bloco Se (Condições)
# ------------------------------------------------------------
def p_se(p):
    '''se : SE condicao'''
    p[0] = p[2]

def p_condicao(p):
    '''condicao : ENTITY_ID OP_RELACIONAL NUMERO'''
    p[0] = {'node': 'condicao', 'entidade': p[1], 'operador': p[2], 'valor': p[3]}

# ------------------------------------------------------------
# 5. Bloco Entao (Ações)
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
    '''acao : ENTITY_ID PONTO SERVICO ABRE_PAR FECHA_PAR PONTO_VIRGULA'''
    p[0] = {'node': 'acao', 'entidade': p[1], 'servico': p[3]}

# ------------------------------------------------------------
# 6. Tratamento de Erros e Recuperação (Modo Pânico)
# ------------------------------------------------------------
def p_error(p):
    if p:
        print(f"[ERRO SINTÁTICO] Token inesperado '{p.value}' na linha {p.lineno}.")
        print("A iniciar Modo Pânico: a ignorar tokens até encontrar um ponto de sincronização...")
        
        # O parser descarta tokens até encontrar um delimitador seguro (como ; ou FIM)
        while True:
            tok = parser.token()
            if not tok or tok.type in ['PONTO_VIRGULA', 'FIM']:
                break
        parser.restart()
    else:
        print("[ERRO SINTÁTICO] Fim de ficheiro inesperado. Esqueceu-se de fechar com 'Fim'?")

# Constrói o analisador sintático
parser = yacc.yacc()

# ------------------------------------------------------------
# Bloco de Teste
# ------------------------------------------------------------
if __name__ == '__main__':
    codigo_teste = """
    Automacao "Ligar luz da sala"
    Quando tempo = 18:00
    Se sensor.luminosidade < 30
    Entao light.sala.turn_on();
    Fim
    """
    
    print("--- INICIANDO ANÁLISE SINTÁTICA ---")
    
    # Chama o parser passando a string e o lexer
    ast = parser.parse(codigo_teste, lexer=lexer)
    
    # Imprime a árvore formatada
    import pprint
    pprint.pprint(ast, sort_dicts=False)
    
    print("--- FIM DA ANÁLISE ---")