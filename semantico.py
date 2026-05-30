class AnalisadorSemantico:
    def __init__(self):
        self.erros = []

    def analisar(self, ast):
        self._visitar(ast)
        return self.erros

    def _visitar(self, nodo):
        if isinstance(nodo, dict):
            tipo_nodo = nodo.get('node')
            
            if tipo_nodo == 'programa':
                self._visitar(nodo.get('filho'))
            
            elif tipo_nodo == 'automacao':
                self._visitar(nodo.get('quando'))
                if nodo.get('se'):
                    self._visitar(nodo.get('se'))
                self._visitar(nodo.get('entao'))
            
            elif tipo_nodo == 'acao':
                self._verificar_acao(nodo)
                
        elif isinstance(nodo, list):
            for item in nodo:
                self._visitar(item)

    def _verificar_acao(self, nodo):
        entidade = nodo.get('entidade')
        servico = nodo.get('servico')
        
        # O domínio é tudo que vem antes do ponto (ex: light.sala -> light)
        dominio = entidade.split('.')[0]

        # Tabela de Símbolos / Domínios Permitidos
        servicos_permitidos = {
            'light': ['turn_on', 'turn_off', 'toggle'],
            'switch': ['turn_on', 'turn_off', 'toggle'],
            'sensor': [] # Sensores não executam ações
        }

        if dominio == 'sensor':
            self.erros.append(f"[ERRO SEMÂNTICO] Entidades do tipo 'sensor' ({entidade}) não executam ações. Falha ao tentar chamar '{servico}'.")
        elif dominio in servicos_permitidos:
            if servico not in servicos_permitidos[dominio]:
                self.erros.append(f"[ERRO SEMÂNTICO] Serviço '{servico}' incompatível com o domínio '{dominio}'.")
        else:
            self.erros.append(f"[ERRO SEMÂNTICO] Domínio '{dominio}' não reconhecido pelo compilador.")

# ------------------------------------------------------------
# Bloco de Teste Integrado
# ------------------------------------------------------------
if __name__ == '__main__':
    from parser import parser, lexer

    # Teste 1: Automação Válida
    codigo_valido = """
    Automacao "Ligar luz da sala"
    Quando tempo = 18:00
    Se sensor.luminosidade < 30
    Entao light.sala.turn_on();
    Fim
    """

    # Teste 2: Automação com Erro Semântico (Tentando ligar um sensor)
    codigo_invalido = """
    Automacao "Erro semantico"
    Quando tempo = 18:00
    Entao sensor.temperatura.turn_on();
    Fim
    """

    analisador = AnalisadorSemantico()

    print("--- TESTE 1: CÓDIGO VÁLIDO ---")
    ast_valida = parser.parse(codigo_valido, lexer=lexer)
    erros1 = analisador.analisar(ast_valida)
    if not erros1:
        print("Análise Semântica concluída sem erros.")
    
    print("\n--- TESTE 2: CÓDIGO INVÁLIDO ---")
    ast_invalida = parser.parse(codigo_invalido, lexer=lexer)
    analisador.erros.clear() # Limpa os erros do teste anterior
    erros2 = analisador.analisar(ast_invalida)
    for erro in erros2:
        print(erro)