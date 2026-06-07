# Compilador Homi ➔ Home Assistant

Este repositório contém o código-fonte de um compilador desenvolvido como trabalho final para a disciplina de Compiladores. 

O objetivo do projeto é abstrair a complexidade na criação de automações residenciais, permitindo que usuários escrevam regras em uma linguagem declarativa e simplificada chamada **Homi**. O compilador traduz essas regras de negócio, passando por análises léxica, sintática e semântica, gerando como saída arquivos de configuração **YAML** nativos e prontos para uso no [Home Assistant](https://www.home-assistant.io/).

---

## 🛠️ Pré-requisitos e Instalação

O projeto foi construído em **Python 3** e utiliza a biblioteca **PLY (Python Lex-Yacc)** para a geração dos autômatos léxicos e sintáticos.

Para rodar o compilador, certifique-se de ter o Python instalado e instale as dependências:

```bash
# Utilizando o Makefile fornecido:
make install

# Ou instalando manualmente via pip:
pip install ply