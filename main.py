import sys
import os

# Importar os módulos desenvolvidos nas etapas anteriores
from parser import parser, lexer
from semantico import AnalisadorSemantico
from gerador import GeradorYAML

def compilar(caminho_arquivo):
    print(f"--- Iniciando compilação: {caminho_arquivo} ---")
    
    # Verifica se o ficheiro existe
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O ficheiro '{caminho_arquivo}' não foi encontrado.")
        return

    # Lê o código-fonte
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        codigo_fonte = f.read()

    # Análise Sintática (Gera a AST e já embute a Análise Léxica)
    ast = parser.parse(codigo_fonte, lexer=lexer)
    
    if not ast:
        print("Compilação abortada devido a erros sintáticos.")
        return

    # Análise Semântica
    analisador = AnalisadorSemantico()
    erros = analisador.analisar(ast)
    
    if erros:
        print("Falha na compilação. Foram encontrados erros semânticos:")
        for erro in erros:
            print(erro)
        return
        
    # Geração de Código
    gerador = GeradorYAML()
    yaml_final = gerador.gerar(ast)
    
    # Salvar o ficheiro de saída
    nome_saida = caminho_arquivo.replace('.homi', '.yaml')
    with open(nome_saida, 'w', encoding='utf-8') as f:
        f.write(yaml_final)
        
    print(f"Compilação concluída com sucesso! Ficheiro gerado: {nome_saida}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso correto: python main.py <ficheiro.homi>")
    else:
        compilar(sys.argv[1])