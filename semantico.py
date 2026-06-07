# Tabela de Símbolos
# Armazena as entidades encontradas na AST com seus domínios
# e tipos esperados, permitindo verificação de tipos e escopo.
class TabelaDeSimbolos:
    def __init__(self):
        # Cada entrada: { 'dominio': str, 'tipo': str }
        # tipo pode ser: 'binario' (on/off), 'numerico', 'media', 'atuador'
        self._simbolos = {}

    def registrar(self, entidade: str, dominio: str, tipo: str):
        """Registra uma entidade na tabela."""
        if entidade not in self._simbolos:
            self._simbolos[entidade] = {'dominio': dominio, 'tipo': tipo}

    def buscar(self, entidade: str):
        """Retorna o registro da entidade ou None se não encontrada."""
        return self._simbolos.get(entidade)

    def listar(self):
        return dict(self._simbolos)

    def __str__(self):
        if not self._simbolos:
            return "  (vazia)"
        linhas = []
        for entidade, info in self._simbolos.items():
            linhas.append(f"  {entidade:<35} dominio={info['dominio']:<15} tipo={info['tipo']}")
        return "\n".join(linhas)


# Definições estáticas de domínios conhecidos

# Serviços permitidos por domínio
SERVICOS_PERMITIDOS = {
    'light':        ['turn_on', 'turn_off', 'toggle', 'delay'],
    'switch':       ['turn_on', 'turn_off', 'toggle', 'delay'],
    'media_player': ['volume_set', 'turn_on', 'turn_off', 'play_media', 'delay'],
    'sensor':       [],   # sensores não executam ações
}

# Tipo de cada domínio (usado para verificação de parâmetros)
TIPO_POR_DOMINIO = {
    'light':        'binario',   # aceita on/off; turn_on/turn_off sem parâmetro numérico
    'switch':       'binario',
    'media_player': 'media',     # aceita volume (float 0.0–1.0) e delay (tempo)
    'sensor':       'numerico',  # leitura numérica, não executa ação
}

# Serviços que exigem um parâmetro numérico (float)
SERVICOS_REQUEREM_NUMERO = {'volume_set'}

# Serviços que exigem um parâmetro de tempo (ex: 4min, 10s)
SERVICOS_REQUEREM_TEMPO = {'delay'}

# Serviços que NÃO devem receber nenhum parâmetro
SERVICOS_SEM_PARAMETRO = {'turn_on', 'turn_off', 'toggle', 'play_media'}


# Analisador Semântico
class AnalisadorSemantico:
    def __init__(self):
        self.erros = []
        self.tabela = TabelaDeSimbolos()

    def analisar(self, ast):
        """Ponto de entrada. Retorna a lista de erros encontrados."""
        self.erros = []
        self.tabela = TabelaDeSimbolos()
        self._visitar(ast)
        return self.erros

    def _visitar(self, nodo):
        if isinstance(nodo, dict):
            tipo = nodo.get('node')

            if tipo == 'programa':
                self._visitar(nodo.get('filho'))

            elif tipo == 'automacao':
                self._visitar(nodo.get('quando'))
                if nodo.get('se'):
                    self._visitar(nodo.get('se'))
                self._visitar(nodo.get('entao'))

            elif tipo == 'gatilho_estado':
                self._registrar_entidade(nodo.get('entidade'))

            elif tipo == 'gatilho_tempo':
                pass  # Gatilhos de tempo não envolvem entidades

            elif tipo == 'operacao_logica':
                self._visitar(nodo.get('esq'))
                self._visitar(nodo.get('dir'))

            elif tipo == 'condicao':
                self._verificar_condicao(nodo)

            elif tipo == 'acao':
                self._verificar_acao(nodo)

        elif isinstance(nodo, list):
            for item in nodo:
                self._visitar(item)

    def _registrar_entidade(self, entidade: str):
        if not entidade:
            return
        dominio = entidade.split('.')[0]
        tipo = TIPO_POR_DOMINIO.get(dominio, 'desconhecido')
        self.tabela.registrar(entidade, dominio, tipo)

    def _verificar_condicao(self, nodo):
        entidade = nodo.get('entidade', '')
        operador = nodo.get('operador', '')
        valor    = nodo.get('valor')

        self._registrar_entidade(entidade)
        dominio = entidade.split('.')[0]

        if dominio == 'sensor':
            if isinstance(valor, str) and valor in ('on', 'off'):
                self.erros.append(
                    f"[ERRO SEMÂNTICO] Linha com condição: entidade 'sensor' ({entidade}) "
                    f"não possui estado 'on/off'. Use um operador numérico (ex: < 30)."
                )

        # Luzes e switches: comparação numérica não faz sentido (use on/off)
        elif dominio in ('light', 'switch'):
            if isinstance(valor, (int, float)):
                self.erros.append(
                    f"[ERRO SEMÂNTICO] Condição inválida: '{entidade}' é do tipo binário "
                    f"(on/off) e não pode ser comparado numericamente com '{valor}'."
                )

    def _verificar_acao(self, nodo):
        entidade = nodo.get('entidade', '')
        servico  = nodo.get('servico', '')
        parametro = nodo.get('parametro')

        self._registrar_entidade(entidade)
        dominio = entidade.split('.')[0]

        # 1. Domínio não reconhecido
        if dominio not in SERVICOS_PERMITIDOS:
            self.erros.append(
                f"[ERRO SEMÂNTICO] Domínio '{dominio}' de '{entidade}' não é reconhecido. "
                f"Use: {', '.join(SERVICOS_PERMITIDOS.keys())}."
            )
            return

        # 2. Sensores não executam ações
        if dominio == 'sensor':
            self.erros.append(
                f"[ERRO SEMÂNTICO] '{entidade}' é um sensor e não pode executar ações."
            )
            return

        # 3. Serviço incompatível com o domínio
        if servico not in SERVICOS_PERMITIDOS[dominio]:
            self.erros.append(
                f"[ERRO SEMÂNTICO] Serviço '{servico}' não é permitido para o domínio "
                f"'{dominio}'. Serviços válidos: {SERVICOS_PERMITIDOS[dominio]}."
            )
            return


        # Serviços que NÃO devem ter parâmetro
        if servico in SERVICOS_SEM_PARAMETRO and parametro is not None:
            self.erros.append(
                f"[ERRO SEMÂNTICO] Serviço '{servico}' não aceita parâmetros, "
                f"mas recebeu '{parametro}'."
            )

        # Serviços que exigem número (float/int)
        elif servico in SERVICOS_REQUEREM_NUMERO:
            if parametro is None:
                self.erros.append(
                    f"[ERRO SEMÂNTICO] Serviço '{servico}' requer um parâmetro numérico "
                    f"(ex: 0.5), mas nenhum foi fornecido."
                )
            elif not isinstance(parametro, (int, float)):
                self.erros.append(
                    f"[ERRO SEMÂNTICO] Serviço '{servico}' requer um número, "
                    f"mas recebeu '{parametro}' (tipo: {type(parametro).__name__})."
                )
            # Validação de range para volume_set (deve estar entre 0.0 e 1.0)
            elif servico == 'volume_set' and not (0.0 <= float(parametro) <= 1.0):
                self.erros.append(
                    f"[ERRO SEMÂNTICO] 'volume_set' aceita valores entre 0.0 e 1.0, "
                    f"mas recebeu '{parametro}'."
                )

        # Serviços que exigem tempo (string como '4min', '10s', '1h')
        elif servico in SERVICOS_REQUEREM_TEMPO:
            if parametro is None:
                self.erros.append(
                    f"[ERRO SEMÂNTICO] Serviço '{servico}' requer um parâmetro de tempo "
                    f"(ex: 10s, 5min, 1h), mas nenhum foi fornecido."
                )
            elif not isinstance(parametro, str):
                self.erros.append(
                    f"[ERRO SEMÂNTICO] Serviço '{servico}' requer um valor de tempo "
                    f"(ex: 10s, 5min), mas recebeu '{parametro}' (numérico)."
                )



# if __name__ == '__main__':
#     from parser import parser, lexer

#     casos = {
#         "VÁLIDO — automação completa": """
#             Automacao "Modo Cinema"
#             Quando tempo = 20:00
#             Se sensor.luminosidade < 10 E sensor.tv == on
#             Entao media_player.sala.volume_set(0.8);
#                 light.sanca.turn_off();
#                 media_player.sala.delay(4min);
#             Fim
#         """,
#         "ERRO — sensor como ação": """
#             Automacao "Erro sensor"
#             Quando tempo = 08:00
#             Entao sensor.temperatura.turn_on();
#             Fim
#         """,
#         "ERRO — serviço incompatível": """
#             Automacao "Erro serviço"
#             Quando tempo = 08:00
#             Entao light.sala.volume_set(0.5);
#             Fim
#         """,
#         "ERRO — parâmetro inválido em turn_on": """
#             Automacao "Erro parametro"
#             Quando tempo = 08:00
#             Entao light.sala.turn_on(100);
#             Fim
#         """,
#         "ERRO — volume fora do range": """
#             Automacao "Erro volume"
#             Quando tempo = 08:00
#             Entao media_player.sala.volume_set(1.5);
#             Fim
#         """,
#         "ERRO — delay sem parâmetro de tempo": """
#             Automacao "Erro delay"
#             Quando tempo = 08:00
#             Entao media_player.sala.delay(42);
#             Fim
#         """,
#     }

#     analisador = AnalisadorSemantico()

#     for titulo, codigo in casos.items():
#         print(f"\n{'='*55}")
#         print(f"TESTE: {titulo}")
#         print('='*55)
#         ast = parser.parse(codigo, lexer=lexer)
#         erros = analisador.analisar(ast)

#         print("Tabela de Símbolos registrada:")
#         print(analisador.tabela)

#         if not erros:
#             print("✓ Análise semântica concluída SEM erros.")
#         else:
#             for e in erros:
#                 print(e)    