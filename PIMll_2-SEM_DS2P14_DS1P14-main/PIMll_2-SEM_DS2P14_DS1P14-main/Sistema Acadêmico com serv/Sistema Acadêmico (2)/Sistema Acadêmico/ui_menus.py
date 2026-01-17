# Salve como: ui_menus.py (VERSÃO CORRIGIDA)

# IMPORTANTE: Agora importa 'cliente' e não mais 'servicos_sistema' e 'servicos_ia'
import cliente as servicos      # <--- NOVO
import cliente as servicos_ia   # <--- NOVO

import getpass # Para esconder a senha durante o cadastro

# --- 1. FUNÇÃO HELPER DE MENU (Sem alterações) ---

def _obter_escolha_numerada(prompt: str, opcoes_mapa: dict) -> str:
    """
    Exibe um menu de opções numeradas e retorna o VALOR (string) da opção escolhida.
    """
    print(f"\n{prompt}")
    
    opcoes_para_escolha = list(opcoes_mapa.items())
    
    for i, (descricao, valor) in enumerate(opcoes_para_escolha):
        print(f"  {i+1}: {descricao}")
    
    while True:
        try:
            escolha_num = int(input(f"Escolha o número (1-{len(opcoes_para_escolha)}): "))
            if 1 <= escolha_num <= len(opcoes_para_escolha):
                indice = escolha_num - 1
                return opcoes_para_escolha[indice][1]
            else:
                print(f"ERRO: Número fora do intervalo (1-{len(opcoes_para_escolha)}). Tente novamente.")
        except ValueError:
            print("ERRO: Por favor, digite apenas um número.")

# --- 2. MENU PRINCIPAL (Sem alterações no corpo, usa 'cliente.py') ---
def menu_principal(id_usuario_logado):
    """
    Exibe o menu principal com base nas permissões do usuário.
    Retorna True para continuar na sessão (ex: voltar ao menu).
    Retorna False para fazer logout (voltar para a tela de login).
    """
    
    # Busca permissões (agora via socket através do stub)
    permissoes = servicos.obter_permissoes_usuario(id_usuario_logado)
    nome_usuario = servicos.obter_nome_usuario(id_usuario_logado)
    
    print("\n" + "="*50)
    print(f"Bem-vindo(a), {nome_usuario}!")
    print("Menu Principal")
    print("="*50)

    # Constrói o menu dinâmico
    opcoes_menu = {}
    if "cadastrar_usuario" in permissoes:
        opcoes_menu["Cadastrar Novo Usuário"] = _menu_cadastrar_usuario
    if "ver_boletim" in permissoes:
        opcoes_menu["Ver Boletim (Aluno)"] = _menu_ver_boletim_aluno
    if "lancar_nota" in permissoes:
        opcoes_menu["Lançar Notas (Professor)"] = _menu_lancar_notas_professor
    if "analisar_risco" in permissoes:
        opcoes_menu["Analisar Risco de Aluno (IA)"] = _menu_analise_risco_ia

    # Adiciona opção de Logout
    opcoes_menu["Fazer Logout (Sair)"] = None

    while True:
        print("\nEscolha uma opção:")
        opcoes_lista = list(opcoes_menu.keys())
        for i, desc in enumerate(opcoes_lista):
            print(f"  {i+1}: {desc}")
        
        try:
            escolha = int(input("Opção: "))
            if not 1 <= escolha <= len(opcoes_lista):
                print("ERRO: Opção inválida.")
                continue

            descricao_escolhida = opcoes_lista[escolha-1]
            
            if descricao_escolhida == "Fazer Logout (Sair)":
                print("\nFazendo logout...")
                return False  # Sinaliza para o main.py que a sessão terminou

            funcao_menu = opcoes_menu[descricao_escolhida]
            funcao_menu(id_usuario_logado) 
            
        except ValueError:
            print("ERRO: Por favor, digite um número.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação interrompida. Fazendo logout por segurança...")
            return False

# --- 3. SUBMENUS (Usam 'cliente.py' indiretamente) ---

def _menu_cadastrar_usuario(id_usuario_logado):
    """Submenu para cadastrar um novo usuário."""
    print("\n--- Cadastro de Novo Usuário ---")
    
    dados_novo_usuario = {}
    
    # --- Coleta de Dados Pessoais ---
    print("\n--- 1. Dados Pessoais ---")
    dados_novo_usuario['nome'] = input("Nome Completo: ")
    dados_novo_usuario['email'] = input("E-mail: ")
    
    while True:
        cpf = input("CPF (apenas números ou formatado): ")
        # Validação (agora via socket)
        if servicos.validar_cpf(cpf): 
            dados_novo_usuario['cpf'] = cpf
            break
        else:
            print("ERRO: CPF inválido ou em formato incorreto. Tente novamente.")

    # --- Coleta de Dados de Acesso ---
    print("\n--- 2. Dados de Acesso ---")
    dados_novo_usuario['username'] = input("Nome de Usuário (para login): ")
    
    while True:
        senha1 = getpass.getpass("Senha (mín. 6 caracteres): ")
        if len(senha1) < 6:
            print("ERRO: A senha deve ter no mínimo 6 caracteres.")
            continue
        senha2 = getpass.getpass("Confirme a Senha: ")
        if senha1 == senha2:
            dados_novo_usuario['senha'] = senha1
            break
        else:
            print("ERRO: As senhas não coincidem. Tente novamente.")

    # --- Definição da Função/Cargo ---
    mapa_funcoes = {
        "Aluno": "f4",
        "Professor": "f3",
        "Coordenador": "f2",
        "Vice-Diretor": "f6",
        "Diretor": "f5",
        "Admin": "f1" 
    }
    dados_novo_usuario['id_funcao'] = _obter_escolha_numerada("3. Função/Cargo do Usuário:", mapa_funcoes)

    # --- Dados Específicos (Perfil do Aluno) ---
    if dados_novo_usuario['id_funcao'] == 'f4': # Se for Aluno
        print("\n--- 4. Perfil Estático do Aluno (IA) ---")
        
        perfil_aluno = {}
        perfil_aluno['school'] = input("Escola (Sigla, ex: GP ou MS): ").upper()
        perfil_aluno['age'] = int(input("Idade: "))
        perfil_aluno['sex'] = _obter_escolha_numerada("Sexo:", {"Masculino": "M", "Feminino": "F"})
        perfil_aluno['address_type'] = _obter_escolha_numerada("Tipo de Endereço:", {"Urbano": "Urban", "Rural": "Rural"})
        perfil_aluno['family_size'] = _obter_escolha_numerada("Tamanho da Família:", {"Menor ou igual a 3": "Less than or equal to 3", "Maior que 3": "Greater than 3"})
        perfil_aluno['parent_status'] = _obter_escolha_numerada("Status dos Pais:", {"Morando juntos": "Living together", "Separados": "Apart"})
        
        mapa_educ = {
            "Nenhuma": "none",
            "Até 4ª série": "primary education (4th grade)",
            "5ª a 9ª série": "5th to 9th grade",
            "Ensino Médio": "secondary education",
            "Superior": "higher education"
        }
        perfil_aluno['mother_education'] = _obter_escolha_numerada("Educação da Mãe:", mapa_educ)
        perfil_aluno['father_education'] = _obter_escolha_numerada("Educação do Pai:", mapa_educ)

        mapa_job = { "Professor": "teacher", "Saúde": "health", "Serviços": "services", "Em casa": "at_home", "Outro": "other" }
        perfil_aluno['mother_job'] = _obter_escolha_numerada("Trabalho da Mãe:", mapa_job)
        perfil_aluno['father_job'] = _obter_escolha_numerada("Trabalho do Pai:", mapa_job)
        
        mapa_reason = {"Perto de casa": "home", "Reputação": "reputation", "Qualidade": "course", "Outro": "other"}
        perfil_aluno['school_choice_reason'] = _obter_escolha_numerada("Razão da escolha da escola:", mapa_reason)

        mapa_guardian = {"Mãe": "mother", "Pai": "father", "Outro": "other"}
        perfil_aluno['guardian'] = _obter_escolha_numerada("Responsável principal:", mapa_guardian)

        mapa_time = {"< 15 min": "<15 min.", "15 a 30 min": "15 to 30 min.", "30 min a 1h": "30 min. to 1 hour", "> 1h": ">1 hour"}
        perfil_aluno['travel_time'] = _obter_escolha_numerada("Tempo de viagem (casa-escola):", mapa_time)

        perfil_aluno['class_failures'] = int(input("Nº de reprovações anteriores: "))

        mapa_sim_nao = {"Sim": "yes", "Não": "no"}
        perfil_aluno['school_support'] = _obter_escolha_numerada("Suporte educacional extra (escola):", mapa_sim_nao)
        perfil_aluno['family_support'] = _obter_escolha_numerada("Suporte educacional (família):", mapa_sim_nao)
        perfil_aluno['extra_paid_classes'] = _obter_escolha_numerada("Aulas particulares pagas (fora da escola):", mapa_sim_nao)
        perfil_aluno['activities'] = _obter_escolha_numerada("Participa de atividades extra-curriculares:", mapa_sim_nao)
        perfil_aluno['nursery_school'] = _obter_escolha_numerada("Frequentou creche/pré-escola:", mapa_sim_nao)
        perfil_aluno['higher_ed'] = _obter_escolha_numerada("Pretende cursar Ensino Superior:", mapa_sim_nao)
        perfil_aluno['internet_access'] = _obter_escolha_numerada("Possui acesso à Internet em casa:", mapa_sim_nao)
        perfil_aluno['romantic_relationship'] = _obter_escolha_numerada("Está em um relacionamento amoroso:", mapa_sim_nao)
        
        print("\n(Responda de 1=Muito Ruim a 5=Muito Bom)")
        perfil_aluno['family_relationship'] = int(input("Qualidade da relação familiar (1-5): "))
        perfil_aluno['free_time'] = int(input("Tempo livre após a escola (1-5): "))
        perfil_aluno['go_out'] = int(input("Frequência que sai com amigos (1-5): "))
        perfil_aluno['health_status'] = int(input("Estado de saúde atual (1-5): "))
        
        dados_novo_usuario['perfil_aluno'] = perfil_aluno

    # --- Envio para o Servidor ---
    print("\nEnviando dados para cadastro...")
    # Chama o stub 'cadastrar_novo_usuario' do cliente.py
    sucesso, mensagem = servicos.cadastrar_novo_usuario(dados_novo_usuario)
    
    if sucesso:
        print("\n[SUCESSO] Usuário cadastrado com sucesso!")
    else:
        print(f"\n[ERRO] Falha ao cadastrar usuário: {mensagem}")
    
    input("Pressione ENTER para voltar ao menu...")


def _menu_ver_boletim_aluno(id_usuario_logado):
    """Submenu para o aluno ver o próprio boletim."""
    print("\n--- Meu Boletim ---")
    
    # ID do aluno é o ID do usuário logado
    boletim = servicos.obter_boletim_aluno(id_usuario_logado)
    
    if not boletim:
        print("Boletim não encontrado ou ainda não lançado.")
    else:
        print(f"Matemática (G1): {boletim.get('grade_1_mat', 'N/L')}")
        print(f"Matemática (G2): {boletim.get('grade_2_mat', 'N/L')}")
        print(f"Faltas (Mat):   {boletim.get('absences_mat', 'N/L')}")
        print("---")
        print(f"Português (G1):  {boletim.get('grade_1_por', 'N/L')}")
        print(f"Português (G2):  {boletim.get('grade_2_por', 'N/L')}")
        print(f"Faltas (Por):    {boletim.get('absences_por', 'N/L')}")
        
    input("\nPressione ENTER para voltar ao menu...")


def _menu_lancar_notas_professor(id_usuario_logado):
    """Submenu para o professor lançar notas para um aluno."""
    print("\n--- Lançamento de Notas (Professor) ---")
    
    try:
        id_aluno_alvo = int(input("Digite o ID do Aluno: "))
        
        perfil = servicos.obter_perfil_aluno(id_aluno_alvo)
        if not perfil:
            print(f"ERRO: Aluno com ID {id_aluno_alvo} não encontrado.")
            input("Pressione ENTER para voltar...")
            return

        print(f"Aluno selecionado: {servicos.obter_nome_usuario(id_aluno_alvo)}")
        
        print("\nDigite as notas (G1 e G2) e faltas:")
        # Professor lança notas de matemática
        nota_g1_mat = int(input("Nota G1 (Matemática): "))
        nota_g2_mat = int(input("Nota G2 (Matemática): "))
        
        # Professor lança notas de português
        nota_g1_por = int(input("Nota G1 (Português): "))
        nota_g2_por = int(input("Nota G2 (Português): "))

        # Os dados de notas serão formatados no servidor
        sucesso, msg = servicos.lancar_notas_professor(
            id_usuario_logado, 
            id_aluno_alvo, 
            (nota_g1_mat, nota_g2_mat), 
            (nota_g1_por, nota_g2_por)
        )

        if sucesso:
            print(f"\n[SUCESSO] Notas do aluno {id_aluno_alvo} atualizadas.")
        else:
            print(f"\n[ERRO] {msg}")

    except ValueError:
        print("ERRO: ID e notas devem ser números inteiros.")
    
    input("Pressione ENTER para voltar ao menu...")


def _menu_analise_risco_ia(id_usuario_logado):
    """Submenu para Coordenador/Diretor rodar a IA."""
    print("\n--- Análise de Risco (IA) ---")
    
    try:
        id_aluno_alvo = int(input("Digite o ID do Aluno para análise: "))
        
        # 1. Puxa o perfil estático (via socket)
        perfil_estatico = servicos.obter_perfil_aluno(id_aluno_alvo)
        
        if not perfil_estatico:
            print(f"ERRO: Aluno com ID {id_aluno_alvo} não encontrado.")
            input("Pressione ENTER para voltar...")
            return

        print(f"Aluno selecionado: {servicos.obter_nome_usuario(id_aluno_alvo)}")
        print("Perfil estático carregado.")
        
        # 2. Coleta os dados dinâmicos (atuais)
        print("\n--- Coleta de Dados Dinâmicos (Atuais) ---")
        dados_dinamicos = {}
        
        dados_dinamicos['grade_1_mat'] = int(input("Nota G1 (Matemática): "))
        dados_dinamicos['grade_2_mat'] = int(input("Nota G2 (Matemática): "))
        dados_dinamicos['absences_mat'] = int(input("Faltas em Matemática: "))
        
        dados_dinamicos['grade_1_por'] = int(input("Nota G1 (Português): "))
        dados_dinamicos['grade_2_por'] = int(input("Nota G2 (Português): "))
        dados_dinamicos['absences_por'] = int(input("Faltas em Português: "))
        
        mapa_study_ui = {
            "Menos de 2 horas": "<2 hours",
            "2 a 5 horas": "2 to 5 hours",
            "5 a 10 horas": "5 to 10 hours",
            "Mais de 10 horas": ">10 hours"
        }
        dados_dinamicos['study_time'] = _obter_escolha_numerada("Tempo de Estudo Semanal (Atual):", mapa_study_ui)
        
        # 3. Envia AMBOS os dicionários para o serviço de IA (via socket)
        # Usa o stub 'servicos_ia' que aponta para 'cliente.py'
        resultado = servicos_ia.prever_risco_aluno_rf(perfil_estatico, dados_dinamicos)
        
        if isinstance(resultado, float):
            print("\n--- Resultado da Análise (Random Forest) ---")
            print(f"Probabilidade de Risco Geral: {resultado * 100:.2f}%")
            if resultado > 0.70: 
                print("ALERTA MÁXIMO: Intervenção pedagógica urgente.")
            elif resultado > 0.45: 
                print("ALERTA: Aluno em situação de atenção.")
            else: 
                print("BAIXO RISCO: Aluno em situação confortável.")
        else:
            print(f"\nErro na análise: {resultado}")
            
    except ValueError:
        print("ERRO: ID, notas e faltas devem ser números.")
    
    input("Pressione ENTER para voltar ao menu...")