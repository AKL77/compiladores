# Relatório Técnico: Compilador Homi para Home Assistant

## 1. Descrição da Gramática Livre de Contexto (GLC)
A gramática da linguagem Homi foi projetada para ser simples e focada em usuários leigos. Ela é formalmente definida pela quádrupla G = (V_n, V_t, P, S), onde:

**Símbolo Inicial (S):**
* S = programa

**Conjunto de Símbolos Terminais (V_t):**
Representam os tokens reconhecidos pelo analisador léxico.
* V_t = {AUTOMACAO, QUANDO, SE, ENTAO, FIM, ENTITY_ID, TEMPO, NUMERO, ESTADO, STRING, OP_RELACIONAL, ATRIBUICAO, PALAVRA_TEMPO, SERVICO, PONTO, ABRE_PAR, FECHA_PAR, PONTO_VIRGULA, E, OU}

**Conjunto de Símbolos Não-Terminais (V_n):**
Representam as variáveis sintáticas de abstração.
* V_n = {programa, automacao, quando, gatilho, se, condicoes, condicao, entao, acoes, acao, parametro, empty}

**Regras de Produção (P):**
* programa -> automacao
* automacao -> AUTOMACAO STRING quando se entao FIM
* automacao -> AUTOMACAO STRING quando entao FIM
* quando -> QUANDO gatilho
* gatilho -> ENTITY_ID OP_RELACIONAL ESTADO
* gatilho -> PALAVRA_TEMPO ATRIBUICAO TEMPO
* se -> SE condicoes
* condicoes -> condicao E condicoes
* condicoes -> condicao OU condicoes
* condicoes -> condicao
* condicao -> ENTITY_ID OP_RELACIONAL NUMERO
* condicao -> ENTITY_ID OP_RELACIONAL ESTADO
* condicao -> ENTITY_ID OP_RELACIONAL STRING
* entao -> ENTAO acoes
* acoes -> acao acoes
* acoes -> acao
* acao -> ENTITY_ID PONTO SERVICO ABRE_PAR parametro FECHA_PAR PONTO_VIRGULA
* parametro -> NUMERO | STRING | TEMPO | epsilon (vazio)

---

## 2. Descrição do Analisador Léxico (Scanner)
O Analisador Léxico foi implementado utilizando a ferramenta PLY (Python Lex-Yacc). O seu funcionamento baseia-se na definição prévia de todos os tokens suportados pela linguagem Homi (incluindo palavras reservadas e tipos de dados) e na especificação das suas respectivas Expressões Regulares (ER).

Na biblioteca PLY, os tokens simples — que representam literais diretos sem necessidade de processamento adicional, como operadores de atribuição e pontuação — foram declarados diretamente como variáveis. Por outro lado, tokens complexos e palavras reservadas foram declarados através de funções (ex: `t_AUTOMACAO`), o que permite o retorno exato e exclusivo daquela estrutura.

A ordem de declaração das funções foi estritamente planejada, uma vez que o PLY avalia as ERs sequencialmente. Tokens mais específicos foram colocados no topo do arquivo para evitar que fossem incorretamente absorvidos pelas ERs de tokens mais genéricos (ex: garantir que estados como on/off não caiam na regra genérica de SERVICO). Por fim, o analisador foi configurado para reconhecer os tokens válidos enquanto atua como um filtro, removendo espaços em branco e ignorando comentários do código-fonte.

---

## 3. Descrição do Analisador Sintático (Parser)
A linguagem utiliza um Parser Bottom-Up da família LR(k), construído com o algoritmo LALR(1) através do módulo `yacc` do PLY. A Tabela Preditiva LR não foi escrita à mão no código Python; o PLY compila a gramática descrita nas *docstrings* (ex: `'''automacao : ...'''`) e gera a Tabela de Transição de Estados automaticamente em background.

No PLY, cada função define as regras de produção da nossa gramática. O símbolo não-terminal do lado esquerdo recebe os dados processados dos símbolos do lado direito. O parser agrupa essas informações montando um dicionário em Python, onde a chave `'node'` funciona apenas como uma etiqueta para identificar qual é a estrutura, e as outras chaves guardam os dicionários dos nós filhos, construindo assim a nossa Árvore Sintática Abstrata (AST) de baixo para cima.

**Recuperação de Erros:**
Para garantir a resiliência do compilador, foi implementada a técnica de **Modo Pânico** na função `p_error`. Em caso de erro de sintaxe, o parser não aborta a execução. Em vez disso, ele descarta sucessivamente os tokens de entrada até encontrar um token de sincronização seguro — definidos no nosso projeto como o ponto e vírgula (`;`) ou a palavra reservada `Fim`. Após encontrar a âncora, o parser reseta o seu estado e tenta continuar a compilação a partir daquele ponto.

---

## 4. Descrição do Analisador Semântico
O Analisador Semântico percorre a Árvore Sintática (AST) utilizando o padrão *Visitor*. Ele preenche uma Tabela de Símbolos, armazenando as entidades detectadas e os seus respectivos domínios lógicos e tipos (ex: luz, sensor, switch).

A partir destes dados, o analisador garante a tipagem forte e bloqueia operações inválidas através de duas validações principais:
1. **Verificação de Tipos:** Impede comparações e atribuições incorretas, como comparar numericamente o estado de um interruptor binário (on/off).
2. **Consistência Externa:** Valida se os serviços invocados na AST são compatíveis com o domínio da entidade na Tabela de Símbolos, impedindo ações absurdas como tentar executar um serviço de `turn_on` em um sensor de leitura térmica.

---

## 5. Exemplos Práticos e YAMLs Resultantes
A última fase do compilador é a Geração de Código, que traduz a AST validada para a estrutura declarativa e engessada exigida pelo Home Assistant, respeitando a sua indentação rígida. Seguem os exemplos práticos testados no projeto:

### Exemplo 1: Automação simples (Sem Condições)
**Script Fonte Homi:**
```text
Automacao "Desligar tudo"
Quando tempo = 23:00
Entao light.sala.turn_off();
      switch.ar_condicionado.turn_off();
Fim
```

# Código YAML Gerado:

```- alias: 'Desligar tudo'
  description: 'Gerado pelo Compilador Homi'
  mode: single
  triggers:
  - trigger: time
    at: '23:00'
  conditions: []
  actions:
  - action: light.turn_off
    target:
      entity_id: light.sala
  - action: switch.turn_off
    target:
      entity_id: switch.ar_condicionado
```