class GeradorYAML:
    def __init__(self):
        self.yaml_output = ""

    def gerar(self, ast):
        if ast.get('node') == 'programa':
            self._gerar_automacao(ast.get('filho'))
        return self.yaml_output

    def _gerar_automacao(self, nodo):
        self.yaml_output += f"- alias: '{nodo['nome']}'\n"
        self.yaml_output += "  description: 'Gerado pelo Compilador Homi'\n"
        self.yaml_output += "  mode: single\n"
        
        # 1. Gatilhos (Triggers)
        self.yaml_output += "  triggers:\n"
        self._gerar_gatilho(nodo['quando'])
        
        # 2. Condições (Conditions) - Opcional
        if nodo.get('se'):
            self.yaml_output += "  conditions:\n"
            self._gerar_condicao(nodo['se'])
        else:
            self.yaml_output += "  conditions: []\n"
            
        # 3. Ações (Actions)
        self.yaml_output += "  actions:\n"
        for acao in nodo['entao']:
            self._gerar_acao(acao)

    def _gerar_gatilho(self, nodo):
        if nodo['node'] == 'gatilho_tempo':
            self.yaml_output += "  - trigger: time\n"
            self.yaml_output += f"    at: '{nodo['valor']}'\n"
        elif nodo['node'] == 'gatilho_estado':
            self.yaml_output += "  - trigger: state\n"
            self.yaml_output += f"    entity_id: {nodo['entidade']}\n"
            self.yaml_output += f"    to: '{nodo['estado']}'\n"

    def _gerar_condicao(self, nodo):
        if nodo['node'] == 'condicao':
            self.yaml_output += "  - condition: numeric_state\n"
            self.yaml_output += f"    entity_id: {nodo['entidade']}\n"
            # Traduz os operadores para o YAML do Home Assistant
            if nodo['operador'] in ['>', '>=']:
                self.yaml_output += f"    above: {nodo['valor']}\n"
            elif nodo['operador'] in ['<', '<=']:
                self.yaml_output += f"    below: {nodo['valor']}\n"

    def _gerar_acao(self, nodo):
        dominio = nodo['entidade'].split('.')[0]
        # Home Assistant utiliza 'action:' para chamar serviços
        self.yaml_output += f"  - action: {dominio}.{nodo['servico']}\n"
        self.yaml_output += "    target:\n"
        self.yaml_output += f"      entity_id: {nodo['entidade']}\n"

# ------------------------------------------------------------
# Teste de Geração Final
# ------------------------------------------------------------
if __name__ == '__main__':
    from parser import parser, lexer
    from semantico import AnalisadorSemantico

    codigo_teste = """
    Automacao "Ligar luz da sala"
    Quando tempo = 18:00
    Se sensor.luminosidade < 30
    Entao light.sala.turn_on();
    Fim
    """

    print("--- COMPILANDO SCRIPT HOMI ---")
    
    # 1. Análise Sintática (Gera a AST)
    ast = parser.parse(codigo_teste, lexer=lexer)
    
    # 2. Análise Semântica (Valida as regras de negócio)
    analisador = AnalisadorSemantico()
    erros = analisador.analisar(ast)
    
    # 3. Geração de Código
    if erros:
        print("Falha na compilação. Erros encontrados:")
        for erro in erros:
            print(erro)
    else:
        gerador = GeradorYAML()
        yaml_final = gerador.gerar(ast)
        
        print("Compilação concluída com sucesso! Código YAML gerado:\n")
        print(yaml_final)
        
        # Opcional: Salvar em um arquivo
        with open('saida.yaml', 'w', encoding='utf-8') as f:
            f.write(yaml_final)
        print("-> Arquivo 'saida.yaml' criado.")