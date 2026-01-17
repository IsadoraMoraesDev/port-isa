# Salve como: main.py (VERSÃO FINAL E CORRIGIDA)

import servicos_sistema as servicos
import ui_menus as menus
import subprocess
import sys

def verificar_e_instalar_bcrypt():
    """Verifica se o bcrypt está instalado e, se não, tenta instalar."""
    try:
        import bcrypt
    except ImportError:
        print("Biblioteca de segurança 'bcrypt' não encontrada.")
        print("Tentando instalar 'bcrypt' automaticamente...")
        try:
            # Tenta usar o pip para instalar
            subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt"])
            print("Dependência 'bcrypt' instalada com sucesso.")
        except Exception as e:
            print("\n" + "="*50)
            print("ERRO CRÍTICO: Falha ao instalar 'bcrypt' automaticamente.")
            print("Por favor, feche o programa e instale manualmente no seu terminal:")
            print("pip install bcrypt")
            print(f"Detalhe do erro: {e}")
            print("="*50)
            return False
    return True

def fazer_login():
    """
    Controla o fluxo de login real, pedindo USERNAME e senha.
    AGORA USA 'input()' em vez de 'getpass.getpass()' para evitar travamentos.
    """
    print("\n--- Login do Sistema Acadêmico ---")
    
    username = input("Digite seu nome de usuário (ou 'sair' para fechar o programa): ")
    if username.lower() == 'sair':
        return None 

    # 🚨 CORREÇÃO CRÍTICA APLICADA: Usando input() para evitar travamento.
    senha = input("Digite sua senha (o texto aparecerá na tela): ") 

    # Chama o "cérebro" para verificar a autenticação (Irá forçar o login do 'admin' no servidor)
    id_usuario_logado = servicos.autenticar_usuario(username, senha)
    
    if id_usuario_logado:
        # SUCESSO
        try:
            # Tenta buscar os dados do usuário para a mensagem de boas-vindas
            dados_usuario = servicos.usuarios[id_usuario_logado]
            nome_usuario = dados_usuario.get('nome', 'Usuário Desconhecido')
            id_funcao = dados_usuario.get('id_funcao')
            nome_funcao = servicos.funcoes.get(id_funcao, "Cargo Desconhecido")
            print(f"\nLogin bem-sucedido! Bem-vindo(a), {nome_usuario} ({nome_funcao}).")
        except Exception:
            print(f"\nLogin bem-sucedido! Bem-vindo(a), ID {id_usuario_logado}.")
        
        return id_usuario_logado
    else:
        # FALHA
        print("ERRO: Nome de usuário ou senha incorretos.")
        return "FALHA"

def main():
    """Ponto de entrada do programa."""
    
    # 1. Inicializa o sistema e CAPTURA a flag 'base_de_dados_nova'
    base_de_dados_nova = servicos.inicializar_sistema()
    
    print("\n--- Bem-vindo ao Sistema Acadêmico ---")
    
    # 2. Se a flag for Verdadeira, exibe as credenciais padrão
    if base_de_dados_nova:
        print("\n" + "="*50)
        print("PRIMEIRA INICIALIZAÇÃO DETECTADA.")
        print("Uma conta 'Admin Mestre' foi criada por padrão.")
        print("Por favor, use estas credenciais para o seu primeiro login:")
        print("\n  Nome de Usuário (Username): admin")
        print("  Senha:                      admin123\n")
        print("RECOMENDAÇÃO: Cadastre o Diretor e demais usuários.")
        print("="*50)

    # --- 3. NOVO LOOP DE APLICAÇÃO (EXTERNO) ---
    while True: 
        
        # 4. Executa a função de login real
        id_usuario_logado = fazer_login()
        
        if id_usuario_logado is None:
            # Usuário digitou 'sair' na tela de login
            print("\nEncerrando o sistema. Adeus!")
            break 
        
        if id_usuario_logado == "FALHA":
            # Usuário errou a senha, volta para a tela de login
            continue 

        # --- 5. LOOP DE SESSÃO (INTERNO) ---
        continuar_sessao = True
        while continuar_sessao:
            continuar_sessao = menus.menu_principal(id_usuario_logado)
        
        print("\n--- Logoff Efetuado ---")

if __name__ == "__main__":
    if verificar_e_instalar_bcrypt():
        main()