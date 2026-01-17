# Em persistencia.py

import json
import os

def carregar_json(nome_arquivo):
    """
    Carrega um arquivo JSON e retorna seu conteúdo como um dicionário.
    Retorna None se o arquivo não existir ou houver um erro.
    """
    if not os.path.exists(nome_arquivo):
        print(f"Aviso: Arquivo '{nome_arquivo}' não encontrado.")
        return None
    
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados
    except Exception as e:
        print(f"Erro crítico ao carregar '{nome_arquivo}': {e}")
        return None

def salvar_json(nome_arquivo, dados):
    """
    Salva um dicionário 'dados' em um arquivo JSON.
    """
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro crítico ao salvar '{nome_arquivo}': {e}")
        return False