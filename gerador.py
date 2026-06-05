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

        # 2. Condições (Conditions) — opcional
        if nodo.get('se'):
            # CORREÇÃO: o cabeçalho "conditions:" é gerado AQUI apenas uma vez.
            # O método _gerar_condicao não deve mais gerá-lo — só gera os itens.
            self.yaml_output += "  conditions:\n"
            self._gerar_condicao(nodo['se'], indent="  ")
        else:
            self.yaml_output += "  conditions: []\n"

        # 3. Ações (Actions)
        self.yaml_output += "  actions:\n"
        for acao in nodo['entao']:
            self._gerar_acao(acao)

    # ----------------------------------------------------------
    def _gerar_gatilho(self, nodo):
        if nodo['node'] == 'gatilho_tempo':
            self.yaml_output += "  - trigger: time\n"
            self.yaml_output += f"    at: '{nodo['valor']}'\n"
        elif nodo['node'] == 'gatilho_estado':
            self.yaml_output += "  - trigger: state\n"
            self.yaml_output += f"    entity_id: {nodo['entidade']}\n"
            self.yaml_output += f"    to: '{nodo['estado']}'\n"

    # ----------------------------------------------------------
    # CORREÇÃO: método reescrito sem o flag 'primeira_condicao'.
    # Recebe apenas o nodo e o nível de indentação atual.
    # O cabeçalho "conditions:" já foi emitido pelo chamador.
    # ----------------------------------------------------------
    def _gerar_condicao(self, nodo, indent="  "):
        if nodo['node'] == 'operacao_logica':
            # Home Assistant usa 'and' ou 'or' como condition composta
            operador_yaml = 'and' if nodo['operador'].upper() == 'E' else 'or'
            self.yaml_output += f"{indent}- condition: {operador_yaml}\n"
            self.yaml_output += f"{indent}  conditions:\n"
            # As sub-condições recebem recuo adicional de 4 espaços
            self._gerar_condicao(nodo['esq'], indent + "    ")
            self._gerar_condicao(nodo['dir'], indent + "    ")

        elif nodo['node'] == 'condicao':
            if nodo['operador'] in ('==', '!='):
                # Comparação de estado (on/off ou string)
                self.yaml_output += f"{indent}- condition: state\n"
                self.yaml_output += f"{indent}  entity_id: {nodo['entidade']}\n"
                self.yaml_output += f"{indent}  state: '{nodo['valor']}'\n"
            else:
                # Comparação numérica
                self.yaml_output += f"{indent}- condition: numeric_state\n"
                self.yaml_output += f"{indent}  entity_id: {nodo['entidade']}\n"
                if nodo['operador'] in ('>', '>='):
                    self.yaml_output += f"{indent}  above: {nodo['valor']}\n"
                elif nodo['operador'] in ('<', '<='):
                    self.yaml_output += f"{indent}  below: {nodo['valor']}\n"

    # ----------------------------------------------------------
    def _gerar_acao(self, nodo):
        dominio   = nodo['entidade'].split('.')[0]
        servico   = nodo['servico']
        parametro = nodo.get('parametro')

        # 'delay' é uma ação nativa do HA, não um serviço de entidade
        if servico == 'delay':
            self.yaml_output += f"  - delay: '{parametro}'\n"
        else:
            self.yaml_output += f"  - action: {dominio}.{servico}\n"
            self.yaml_output += "    target:\n"
            self.yaml_output += f"      entity_id: {nodo['entidade']}\n"

            if parametro is not None:
                self.yaml_output += "    data:\n"
                if servico == 'volume_set':
                    self.yaml_output += f"      volume_level: {parametro}\n"
                else:
                    self.yaml_output += f"      value: {parametro}\n"


# ------------------------------------------------------------
# Teste de Geração Final
# ------------------------------------------------------------
if __name__ == '__main__':
    from parser import parser, lexer
    from semantico import AnalisadorSemantico

    casos = {
        "Ligar luz da sala": """
            Automacao "Ligar luz da sala"
            Quando tempo = 18:00
            Se sensor.luminosidade < 30
            Entao light.sala.turn_on();
            Fim
        """,
        "Modo Cinema (condição composta)": """
            Automacao "Modo Cinema"
            Quando tempo = 20:00
            Se sensor.luminosidade < 10 E sensor.tv == on
            Entao media_player.sala.volume_set(0.8);
                light.sanca.turn_off();
                media_player.sala.delay(4min);
            Fim
        """,
        "Sem condição": """
            Automacao "Desligar tudo"
            Quando tempo = 23:00
            Entao light.sala.turn_off();
                switch.ar_condicionado.turn_off();
            Fim
        """,
    }

    for titulo, codigo in casos.items():
        print(f"\n{'='*55}")
        print(f"COMPILANDO: {titulo}")
        print('='*55)

        ast = parser.parse(codigo, lexer=lexer)
        analisador = AnalisadorSemantico()
        erros = analisador.analisar(ast)

        if erros:
            print("Falha na compilação. Erros semânticos:")
            for e in erros:
                print(" ", e)
        else:
            gerador = GeradorYAML()
            yaml_final = gerador.gerar(ast)
            print("YAML gerado:\n")
            print(yaml_final)

    # Salva o último YAML num arquivo de exemplo
    with open('saida.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_final)
    print("-> Arquivo 'saida.yaml' criado.")