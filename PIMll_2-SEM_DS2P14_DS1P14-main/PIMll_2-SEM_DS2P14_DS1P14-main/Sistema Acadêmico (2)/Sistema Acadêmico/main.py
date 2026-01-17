# Em main.py

import servicos_sistema as servicos
import ui_menus as menus
import getpass  # Para esconder a senha
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
    Retorna o ID do usuário logado se for bem-sucedido.
    Retorna "FALHA" se o login falhar.
    Retorna None se o usuário quiser SAIR do programa.
    """
    print("\n--- Login do Sistema Acadêmico ---")
    
    username = input("Digite seu nome de usuário (ou 'sair' para fechar o programa): ")
    if username.lower() == 'sair':
        return None # Sinaliza para o loop principal encerrar

    try:
        senha = getpass.getpass("Digite sua senha: ") 
    except Exception as e:
        print(f"\nAviso: getpass não suportado neste terminal. A senha ficará visível. {e}")
        senha = input("Digite sua senha (visível): ") # Fallback

    # Chama o "cérebro" para verificar a autenticação
    id_usuario_logado = servicos.autenticar_usuario(username, senha)
    
    if id_usuario_logado:
        # SUCESSO
        
        # --- (INÍCIO DA CORREÇÃO) ---
        
        # 1. Pega o dicionário completo do usuário
        dados_usuario = servicos.usuarios[id_usuario_logado]
        
        # 2. Pega o nome de exibição (ex: "Diretor Marcos")
        nome_usuario = dados_usuario.get('nome', 'Usuário Desconhecido')
        
        # 3. Pega o ID da função (ex: "f5")
        id_funcao = dados_usuario.get('id_funcao')
        
        # 4. Busca o NOME da função (ex: "Diretor") no dicionário 'funcoes'
        # Usamos .get() para evitar erros se a função não for encontrada
        nome_funcao = servicos.funcoes.get(id_funcao, "Cargo Desconhecido")
        
        # 5. Imprime a nova mensagem formatada
        print(f"\nLogin bem-sucedido! Bem-vindo(a), {nome_usuario} ({nome_funcao}).")
        
        # --- (FIM DA CORREÇÃO) ---
        
        return id_usuario_logado # Retorna o ID
    else:
        # FALHA
        print("ERRO: Nome de usuário ou senha incorretos.")
        return "FALHA" # Sinaliza para o loop principal repetir o login

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
            break # Quebra o loop EXTERNO e encerra o programa
        
        if id_usuario_logado == "FALHA":
            # Usuário errou a senha, volta para a tela de login
            continue # Volta para o início do loop EXTERNO

        # --- 5. LOOP DE SESSÃO (INTERNO) ---
        continuar_sessao = True
        while continuar_sessao:
            continuar_sessao = menus.menu_principal(id_usuario_logado)
        
        print("\n--- Logoff Efetuado ---")

if __name__ == "__main__":
    # Verifica a dependência 'bcrypt' antes de rodar o main()
    if verificar_e_instalar_bcrypt():
        main()