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

        self.yaml_output += "  triggers:\n"
        self._gerar_gatilho(nodo['quando'])

        if nodo.get('se'):
            self.yaml_output += "  conditions:\n"
            self._gerar_condicao(nodo['se'], indent="  ")
        else:
            self.yaml_output += "  conditions: []\n"

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
