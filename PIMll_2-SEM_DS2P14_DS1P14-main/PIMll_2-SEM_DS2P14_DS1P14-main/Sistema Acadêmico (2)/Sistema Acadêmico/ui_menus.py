# Em ui_menus.py

import servicos_sistema as servicos
import servicos_ia
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

# --- 2. MENU PRINCIPAL (Sem alterações) ---
def menu_principal(id_usuario_logado):
    """Menu principal após o login."""
    print(f"\n--- Menu Principal ---")
    print(f"Logado como: {servicos.usuarios[id_usuario_logado]['nome']} (ID: {id_usuario_logado})")
    
    if servicos.checar_permissao(id_usuario_logado, "p1"):
        print("1: Cadastrar Novo Usuário")
    if servicos.checar_permissao(id_usuario_logado, "p16"):
        print("2: Visualizar Lista de Usuários")
    if any(servicos.checar_permissao(id_usuario_logado, p) for p in ["p12", "p13", "p14", "p15"]):
        print("3: Gestão Pedagógica")
    if any(servicos.checar_permissao(id_usuario_logado, p) for p in ["p5", "p8"]):
        print("4. Gestão Financeira")
    if servicos.checar_permissao(id_usuario_logado, "p6"):
        print("5: Prever Risco de Aluno (IA - RF)")
    if servicos.checar_permissao(id_usuario_logado, "p3"):
        print("6: Visualizar Boletim")
    print("0: Fazer Logoff (Salvar e Sair da Conta)")
    
    opcao = input("Escolha uma opção: ")
    
    try:
        if opcao == "1" and servicos.checar_permissao(id_usuario_logado, "p1"):
            menu_cadastrar_novo_usuario(id_usuario_logado)
        elif opcao == "2" and servicos.checar_permissao(id_usuario_logado, "p16"):
            menu_visualizar_usuarios()
        elif opcao == "3" and any(servicos.checar_permissao(id_usuario_logado, p) for p in ["p12", "p13", "p14", "p15"]):
            menu_gestao_pedagogica(id_usuario_logado) 
        elif opcao == "4" and any(servicos.checar_permissao(id_usuario_logado, p) for p in ["p5", "p8"]):
            menu_gestao_financeira(id_usuario_logado) 
        elif opcao == "5" and servicos.checar_permissao(id_usuario_logado, "p6"):
            menu_prever_risco_aluno_rf()
        elif opcao == "6" and servicos.checar_permissao(id_usuario_logado, "p3"):
            menu_ver_boletim(id_usuario_logado) 
        elif opcao == "0":
            print("\nSalvando todas as alterações...")
            servicos.salvar_sistema() 
            return False
        else:
            print("Opção inválida ou não permitida.")
    except Exception as e:
        print(f"\nERRO INESPERADO no menu principal: {e}")
        
    return True

# --- 3. CADASTRO DE USUÁRIO (AGORA COM VALIDAÇÃO DE CPF) ---
def menu_cadastrar_novo_usuario(id_usuario_logado):
    """
    Coleta os dados do usuário, incluindo o CPF validado.
    """
    print("\n--- Portal de Cadastro de Novos Usuários ---")
    
    funcoes_permitidas = servicos.get_funcoes_cadastraveis(id_usuario_logado)
    
    if not funcoes_permitidas:
        print("AVISO: Nenhuma função disponível para cadastro no momento.")
        print("(Dependências podem estar em falta, ex: um Diretor deve ser criado antes de um Coordenador).")
        return

    mapa_funcoes_ui = {nome: id_f for id_f, nome in funcoes_permitidas.items()}
    id_funcao_alvo = _obter_escolha_numerada("Qual a função (cargo) do novo usuário?", mapa_funcoes_ui)

    print("\n--- Credenciais de Acesso ---")
    username = input("Digite um Nome de Usuário (para login, ex: 'ana.silva'): ")
    if not username or servicos.is_username_taken(username):
        print("Erro: Nome de usuário inválido ou já em uso.")
        return
        
    try:
        senha = getpass.getpass("Digite uma senha temporária para o usuário: ")
        if not senha:
            print("Erro: Senha não pode ser vazia.")
            return
    except Exception:
        senha = input("Digite uma senha temporária (visível): ")
        
    print("\n--- Informações Pessoais ---")
    nome = input("Nome completo (para exibição): ")
    email = input("Email de contato: ")

    # --- (ADIÇÃO 4) ---
    # --- BLOCO DE VALIDAÇÃO DE CPF ---
    while True:
        cpf = input("CPF (somente números ou com . e -): ")
        if servicos.validar_cpf(cpf):
            print("CPF válido.")
            break # Sai do loop
        else:
            print("ERRO: CPF inválido ou mal formatado. Por favor, tente novamente.")
    # --- FIM DA ADIÇÃO ---
    
    dados_comuns = {"nome": nome, "email": email, "username": username, "senha": senha, "cpf": cpf}
    dados_especificos = {} 

    try:
        # --- COLETA DE DADOS DE PERFIL ESPECÍFICO ---
        if id_funcao_alvo == "f4": # ALUNO
            print("\n--- Perfil Estático do Aluno (Dados para IA) ---")
            print("(!) Insira os dados exatamente como nos arquivos de treino (inglês).")
            
            # --- Dados Demográficos ---
            dados_especificos['age'] = int(input("Idade (ex: 15): "))
            dados_especificos['sex'] = _obter_escolha_numerada("Sexo:", {"Feminino": "F", "Masculino": "M"})
            dados_especificos['address_type'] = _obter_escolha_numerada("Tipo de Endereço:", {"Urbano": "Urban", "Rural": "Rural"})
            dados_especificos['family_size'] = _obter_escolha_numerada("Tamanho da Família:", {"Maior que 3": "Greater than 3", "Menor ou igual a 3": "Less than or equal to 3"})
            dados_especificos['parent_status'] = _obter_escolha_numerada("Status dos Pais:", {"Moram juntos": "Living together", "Separados": "Apart"})
            dados_especificos['school'] = _obter_escolha_numerada("Escola:", {"Gabriel Pereira": "GP", "Mousinho da Silveira": "MS"})
            
            # --- Dados Educacionais/Trabalho dos Pais ---
            mapa_educ = {
                "Nenhuma": "none",
                "Ens. Fundamental I (até 4ª série)": "primary education (4th grade)",
                "Ens. Fundamental II (5ª a 9ª série)": "5th to 9th grade",
                "Ensino Médio": "secondary education",
                "Ensino Superior": "higher education"
            }
            dados_especificos['mother_education'] = _obter_escolha_numerada("Educação da Mãe:", mapa_educ)
            dados_especificos['father_education'] = _obter_escolha_numerada("Educação do Pai:", mapa_educ)
            
            mapa_trabalho = {
                "Professor(a)": "teacher",
                "Em casa": "at_home",
                "Serviços": "services",
                "Área da Saúde": "health",
                "Outro": "other"
            }
            dados_especificos['mother_job'] = _obter_escolha_numerada("Trabalho da Mãe:", mapa_trabalho)
            dados_especificos['father_job'] = _obter_escolha_numerada("Trabalho do Pai:", mapa_trabalho)

            # --- Dados de Escolha Escolar ---
            mapa_razao = {"Grade Curricular": "course", "Perto de casa": "home", "Reputação": "reputation", "Outro": "other"}
            dados_especificos['school_choice_reason'] = _obter_escolha_numerada("Razão da escolha da escola:", mapa_razao)
            
            mapa_resp = {"Mãe": "mother", "Pai": "father", "Outro": "other"}
            dados_especificos['guardian'] = _obter_escolha_numerada("Responsável (guardian):", mapa_resp)
            
            mapa_viagem = {
                "Menos de 15 min": "<15 min.",
                "15 a 30 min": "15 to 30 min.",
                "30 min a 1 hora": "30 min. to 1 hour",
                "Mais de 1 hora": ">1 hour"
            }
            dados_especificos['travel_time'] = _obter_escolha_numerada("Tempo de Viagem até a escola:", mapa_viagem)
            
            # --- Dados de Histórico e Suporte (yes/no) ---
            dados_especificos['class_failures'] = int(input("\nReprovações passadas (0, 1, 2, 3): "))
            
            mapa_sim_nao_pt = {"Sim": "yes", "Não": "no"}
            dados_especificos['school_support'] = _obter_escolha_numerada("Apoio escolar extra?", mapa_sim_nao_pt)
            dados_especificos['family_support'] = _obter_escolha_numerada("Apoio familiar extra?", mapa_sim_nao_pt)
            dados_especificos['extra_paid_classes'] = _obter_escolha_numerada("Aulas particulares pagas?", mapa_sim_nao_pt)
            dados_especificos['activities'] = _obter_escolha_numerada("Atividades extracurriculares?", mapa_sim_nao_pt)
            dados_especificos['nursery_school'] = _obter_escolha_numerada("Frequentou creche?", mapa_sim_nao_pt)
            dados_especificos['higher_ed'] = _obter_escolha_numerada("Quer cursar Ensino Superior?", mapa_sim_nao_pt)
            dados_especificos['internet_access'] = _obter_escolha_numerada("Tem acesso à internet em casa?", mapa_sim_nao_pt)
            dados_especificos['romantic_relationship'] = _obter_escolha_numerada("Está em um relacionamento amoroso?", mapa_sim_nao_pt)
            
            # --- Dados Comportamentais (Escala 1-5) ---
            mapa_escala_1_5 = {
                "1 (Muito Ruim)": 1,
                "2 (Ruim)": 2,
                "3 (Razoável)": 3,
                "4 (Boa)": 4,
                "5 (Excelente)": 5
            }
            dados_especificos['family_relationship'] = _obter_escolha_numerada("Qualidade da relação familiar (1-5):", mapa_escala_1_5)
            dados_especificos['free_time'] = _obter_escolha_numerada("Tempo livre após a escola (1-5):", mapa_escala_1_5)
            dados_especificos['social'] = _obter_escolha_numerada("Nível de socialização (1-5):", mapa_escala_1_5)
            dados_especificos['weekday_alcohol'] = _obter_escolha_numerada("Consumo de álcool (dia de semana, 1-5):", mapa_escala_1_5)
            dados_especificos['weekend_alcohol'] = _obter_escolha_numerada("Consumo de álcool (fim de semana, 1-5):", mapa_escala_1_5)
            dados_especificos['health'] = _obter_escolha_numerada("Estado de saúde (1-5):", mapa_escala_1_5)
            print("--- Perfil do Aluno concluído ---")

        elif id_funcao_alvo == "f3": # PROFESSOR
            print("\n--- Perfil do Professor ---")
            dados_especificos['matricula_funcional'] = input("Matrícula Funcional (ex: F0987): ")
            dados_especificos['data_admissao'] = input("Data de Admissão (DD/MM/AAAA): ")
            dados_especificos['area_especialidade'] = input("Área de Especialidade (ex: Matemática): ")

        elif id_funcao_alvo == "f2": # COORDENADOR
            print("\n--- Perfil do Coordenador ---")
            dados_especificos['matricula_funcional'] = input("Matrícula Funcional (ex: C0123): ")
            dados_especificos['setor_coordenacao'] = input("Setor de Coordenação (ex: Pedagógico): ")
            dados_especificos['ramal'] = input("Ramal Interno: ")

        elif id_funcao_alvo == "f5": # DIRETOR
            print("\n--- Perfil do Diretor ---")
            dados_especificos['matricula_funcional'] = input("Matrícula Funcional (ex: D0001): ")
            dados_especificos['inicio_mandato'] = input("Data de Início do Mandato (DD/MM/AAAA): ")

        elif id_funcao_alvo == "f6": # VICE-DIRETOR
            print("\n--- Perfil do Vice-Diretor ---")
            dados_especificos['matricula_funcional'] = input("Matrícula Funcional (ex: V0002): ")
            dados_especificos['area_foco'] = input("Área de Foco (ex: Administrativo): ")
            dados_especificos['ramal'] = input("Ramal Interno: ")
    
    except ValueError:
        print("ERRO: Valor inválido inserido (ex: idade). Cadastro cancelado.")
        return
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}. Cadastro cancelado.")
        return

    # Chama a função de serviço (com hierarquia)
    novo_id_criado, erro = servicos.adicionar_novo_usuario_completo(
        id_usuario_logado, 
        dados_comuns, 
        id_funcao_alvo, 
        dados_especificos
    )
    
    if erro:
        print(f"\nFalha no Cadastro: {erro}")
    else:
        print(f"\nUsuário '{nome}' (username: '{username}') cadastrado com sucesso! O novo ID do sistema é: {novo_id_criado}")

# --- 3. SUB-MENUS (Sem alterações) ---

def menu_gestao_pedagogica(id_usuario_logado):
    """Sub-menu para ações do Coordenador."""
    print("\n--- Menu de Gestão Pedagógica ---")
    
    if servicos.checar_permissao(id_usuario_logado, "p13"):
        print("1: Criar Nova Turma")
    if servicos.checar_permissao(id_usuario_logado, "p12"):
        print("2: Alocar Professor a uma Turma")
    if servicos.checar_permissao(id_usuario_logado, "p15"):
        print("3: Registrar Ocorrência Disciplinar")
    if servicos.checar_permissao(id_usuario_logado, "p14"):
        print("4: Editar Nota (Fora do Prazo)")
    print("0: Voltar ao Menu Principal")
    
    opcao = input("Escolha uma opção: ")
    try:
        if opcao == "1" and servicos.checar_permissao(id_usuario_logado, "p13"):
            nome_turma = input("Nome da nova turma (ex: 301-A): ")
            ano_letivo = input("Ano letivo (ex: 2026): ")
            print(servicos.criar_nova_turma(nome_turma, ano_letivo))
            
        elif opcao == "2" and servicos.checar_permissao(id_usuario_logado, "p12"):
            id_prof = input("ID do Professor: ")
            id_turma = input("ID da Turma (simulado): ")
            print(servicos.alocar_professor_turma(id_prof, id_turma))

        elif opcao == "3" and servicos.checar_permissao(id_usuario_logado, "p15"):
            id_aluno = input("ID do Aluno: ")
            desc = input("Descrição da Ocorrência: ")
            grav = input("Gravidade (Leve, Media, Grave): ")
            print(servicos.registrar_ocorrencia(id_aluno, desc, grav))

        elif opcao == "4" and servicos.checar_permissao(id_usuario_logado, "p14"):
            id_aluno = input("ID do Aluno: ")
            materia = input("Matéria (ex: Matemática): ")
            nova_nota = float(input("Nova nota final: "))
            print(servicos.editar_nota_bloqueada(id_aluno, materia, nova_nota))
            
        elif opcao == "0":
            return
        else:
            print("Opção inválida ou não permitida.")
    except Exception as e:
        print(f"Erro ao executar ação pedagógica: {e}")

def menu_gestao_financeira(id_usuario_logado):
    """Sub-menu para ações do Diretor / Vice."""
    print("\n--- Menu de Gestão Financeira ---")
    
    if servicos.checar_permissao(id_usuario_logado, "p5"):
        print("1: Acessar Relatório Financeiro")
    if servicos.checar_permissao(id_usuario_logado, "p8"):
        print("2: Gerenciar Mensalidades de Aluno")
    print("0: Voltar ao Menu Principal")

    opcao = input("Escolha uma opção: ")
    try:
        if opcao == "1" and servicos.checar_permissao(id_usuario_logado, "p5"):
            print("Gerando relatório...")
            print(servicos.get_relatorio_financeiro())
            
        elif opcao == "2" and servicos.checar_permissao(id_usuario_logado, "p8"):
            id_aluno = input("ID do Aluno: ")
            sit = input("Nova situação (ex: 'Pago', 'Atrasado', 'Bolsista'): ")
            print(servicos.gerenciar_mensalidades(id_aluno, sit))
            
        elif opcao == "0":
            return
        else:
            print("Opção inválida ou não permitida.")
    except Exception as e:
        print(f"Erro ao executar ação financeira: {e}")

# --- 4. FUNÇÕES EXISTENTES (VISUALIZAÇÃO E IA) ---

def menu_visualizar_usuarios():
    """Chama o serviço para buscar a lista de usuários e a imprime."""
    print("\nBuscando lista de usuários do sistema...")
    lista_de_usuarios = servicos.get_lista_usuarios_formatada()
    print(lista_de_usuarios)

def menu_ver_boletim(id_usuario_logado):
    """Verifica se o usuário é Aluno (mostra o próprio) ou Gestor (pergunta qual)."""
    print("\n--- Visualização de Boletim ---")
    
    id_aluno_alvo = ""
    
    try:
        funcao_usuario = servicos.usuarios[id_usuario_logado]['id_funcao']
        
        if funcao_usuario == 'f4': # É um Aluno
            print("Exibindo seu próprio boletim...")
            id_aluno_alvo = id_usuario_logado
        else: # É Professor, Coordenador, etc. (que tem permissão p3)
            id_aluno_alvo = input("Digite o ID do Aluno que deseja consultar (ex: 4): ")
        
        boletim = servicos.get_boletim_aluno(id_aluno_alvo)
        print(boletim) 
        
    except Exception as e:
        print(f"Ocorreu um erro ao buscar boletim: {e}")

def menu_prever_risco_aluno_rf():
    """Coleta dados DINÂMICOS e chama a IA (Random Forest)."""
    print("\n--- Módulo de Previsão de Risco (Random Forest) ---")
    
    id_aluno = input("Qual o ID do aluno que você quer analisar? (ex: 4): ")
    
    try:
        perfil_estatico = servicos.get_student_static_profile_dict(id_aluno)
        if perfil_estatico is None:
            print(f"Erro: Aluno com ID '{id_aluno}' não encontrado ou não é um aluno.")
            return
            
        print(f"Analisando Aluno: {servicos.usuarios[id_aluno]['nome']}")
        print("Por favor, insira os dados DINÂMICOS (desempenho atual):")
    
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
            
    except KeyError:
         print(f"Erro: Não foi possível encontrar o usuário '{id_aluno}' nos registros (pode não ser um aluno).")
    except ValueError:
        print("Erro: Por favor, insira apenas números para notas ou faltas.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado na previsão: {e}")