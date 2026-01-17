# Em servicos_sistema.py

import persistencia
import servicos_ia
import bcrypt   # Importa a biblioteca de senha segura
import re       # <-- (ADIÇÃO 1)

# --- Constantes do Módulo ---
NOME_ARQUIVO = "dados_sistema.json"

# --- Estado do Sistema (Mantido em Memória) ---
usuarios = {}
funcoes = {}
permissoes = {}
funcao_permissao = {}
perfis_aluno = {}
perfis_professor = {}
perfis_coordenador = {}
perfis_diretor = {}
perfis_vice_diretor = {}
proximo_id_disponivel = 1 # Contador de IDs

# --- Funções de Segurança (Hashing com Bcrypt) ---

def _hash_senha_bcrypt(senha: str) -> str:
    """Gera um hash Bcrypt da senha para armazenamento seguro."""
    if not senha:
        return None
    senha_bytes = senha.encode('utf-8')
    hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    return hash_bytes.decode('utf-8')

def _verificar_senha_bcrypt(senha_plana: str, hash_salvo: str) -> bool:
    """Verifica se a senha em texto plano bate com o hash salvo."""
    if not senha_plana or not hash_salvo:
        return False
    try:
        senha_plana_bytes = senha_plana.encode('utf-8')
        hash_salvo_bytes = hash_salvo.encode('utf-8')
        return bcrypt.checkpw(senha_plana_bytes, hash_salvo_bytes)
    except Exception as e:
        print(f"Aviso (Bcrypt): Erro ao verificar senha (hash mal formado?): {e}")
        return False

# --- Funções de Inicialização ---

def inicializar_sistema():
    """ 
    Carrega os dados do JSON ou cria um arquivo padrão mínimo.
    Retorna True se um novo banco de dados foi criado, False caso contrário.
    """
    global usuarios, funcoes, permissoes, funcao_permissao, \
           perfis_aluno, perfis_professor, perfis_coordenador, \
           perfis_diretor, perfis_vice_diretor, proximo_id_disponivel
           
    base_de_dados_nova = False

    dados = persistencia.carregar_json(NOME_ARQUIVO)
    
    if dados is None:
        print("Arquivo de dados não encontrado. Criando base de dados inicial...")
        _criar_dados_padrao() 
        base_de_dados_nova = True
    else:
        # Preenche as variáveis globais
        usuarios = dados.get("usuarios", {})
        funcoes = dados.get("funcoes", {})
        permissoes = dados.get("permissoes", {})
        funcao_permissao = dados.get("funcao_permissao", {})
        perfis_aluno = dados.get("perfis_aluno", {})
        perfis_professor = dados.get("perfis_professor", {})
        perfis_coordenador = dados.get("perfis_coordenador", {})
        perfis_diretor = dados.get("perfis_diretor", {})
        perfis_vice_diretor = dados.get("perfis_vice_diretor", {})
        proximo_id_disponivel = dados.get("proximo_id_disponivel", 1)
        print("Serviços de gestão (JSON) inicializados.")

    servicos_ia.carregar_modelo_ia()
    print("Módulo de IA (RF) pronto.")
    
    return base_de_dados_nova


def _criar_dados_padrao():
    """
    Função "privada" para popular o sistema APENAS COM O ADMIN.
    """
    global permissoes, funcoes, funcao_permissao, usuarios, proximo_id_disponivel
    
    permissoes = {
        "p1": "cadastrar_usuario", "p2": "lancar_nota", "p3": "ver_boletim",
        "p4": "gerar_relatorio_turma", "p5": "acessar_relatorio_financeiro",
        "p6": "prever_risco_aluno_rf", "p8": "gerenciar_mensalidades",
        "p9": "desligar_usuario", "p10": "homologar_boletins",
        "p11": "configurar_ano_letivo", "p12": "alocar_professor_turma",
        "p13": "criar_turma", "p14": "editar_nota_bloqueada",
        "p15": "gerenciar_ocorrencias",
        "p16": "visualizar_lista_usuarios"
    }
    
    funcoes = {
        "f1": "Admin", "f2": "Coordenador", "f3": "Professor",
        "f4": "Aluno", "f5": "Diretor", "f6": "Vice-Diretor"
    }
    
    funcao_permissao = {
        "f1": list(permissoes.keys()),
        "f2": ["p1", "p2", "p3", "p4", "p6", "p12", "p13", "p14", "p15"],
        "f3": ["p2", "p3", "p6"], "f4": ["p3"],
        "f5": list(permissoes.keys()),
        "f6": ["p2", "p3", "p4", "p5", "p6", "p8", "p14", "p15"]
    }
    
    # A senha padrão para o admin é "admin123"
    # Adicionamos um CPF 'placeholder' válido para o admin
    admin_cpf = "11111111111" # (Este é um CPF inválido pela regra, vamos usar um válido)
    admin_cpf = "12345678909" # (Exemplo, este também é inválido)
    # Vamos usar um gerado válido para o exemplo:
    admin_cpf = "78343272033" 
    
    usuarios = {
        "1": {"nome": "Admin Mestre", "username": "admin", "senha_hash": _hash_senha_bcrypt("admin123"), "id_funcao": "f1", "cpf": admin_cpf}
    }
    proximo_id_disponivel = 2
    
    perfis_aluno = {}
    perfis_professor = {}
    perfis_coordenador = {}
    perfis_diretor = {}
    perfis_vice_diretor = {}

    print("Salvando dados padrão (Admin) no disco...")
    salvar_sistema()

# --- (INÍCIO DA LÓGICA DE HIERARQUIA DE CADASTRO) ---

# 1. Constantes de Papel
ROLE_ADMIN = "Admin"
ROLE_DIRETOR = "Diretor"
ROLE_VICE_DIRETOR = "Vice-Diretor"
ROLE_COORDENADOR = "Coordenador"
ROLE_PROFESSOR = "Professor"
ROLE_ALUNO = "Aluno"

# 2. A "Fonte da Verdade" da Hierarquia
_ALLOWED_CREATIONS = {
    ROLE_ADMIN: {ROLE_DIRETOR, ROLE_VICE_DIRETOR, ROLE_COORDENADOR, ROLE_PROFESSOR, ROLE_ALUNO},
    ROLE_DIRETOR: {ROLE_VICE_DIRETOR, ROLE_COORDENADOR, ROLE_PROFESSOR, ROLE_ALUNO},
    ROLE_COORDENADOR: {ROLE_PROFESSOR, ROLE_ALUNO},
    ROLE_VICE_DIRETOR: set(),
    ROLE_PROFESSOR: set(),
    ROLE_ALUNO: set(),
}

def _get_role_name(id_funcao: str) -> str:
    """Função auxiliar para pegar o NOME do papel (ex: "Admin") a partir do ID (ex: "f1")."""
    return funcoes.get(id_funcao, None)

def _funcao_ja_existe_no_sistema(id_funcao_alvo: str) -> bool:
    """Função auxiliar para o LIMITADOR DE FUNÇÕES e DEPENDÊNCIAS."""
    for usuario in usuarios.values():
        if usuario.get('id_funcao') == id_funcao_alvo:
            return True
    return False

def pode_cadastrar(id_de_quem_cadastra, id_funcao_alvo):
    """
    Função "Guarda" que verifica a hierarquia de permissão de cadastro.
    Retorna (True, None) se permitido, ou (False, mensagem) se negado.
    """
    id_cad = str(id_de_quem_cadastra)
    if id_cad not in usuarios:
        return False, "Usuário cadastrador não existe."

    papel_cadastrador = _get_role_name(usuarios[id_cad].get("id_funcao"))
    papel_alvo = _get_role_name(id_funcao_alvo)

    if not papel_cadastrador or not papel_alvo:
        return False, "Não foi possível determinar os papéis (cadastrador ou alvo)."

    allowed_set = _ALLOWED_CREATIONS.get(papel_cadastrador, set())
    
    if papel_alvo in allowed_set:
        return True, None
    else:
        if papel_cadastrador == ROLE_ADMIN and papel_alvo == ROLE_ADMIN:
            return False, "ERRO: O Admin Mestre (Root) é único e não pode criar outro Admin."
        
        return False, f"ERRO: O seu cargo '{papel_cadastrador}' não tem permissão hierárquica para cadastrar um '{papel_alvo}'."

def get_funcoes_cadastraveis(id_de_quem_cadastra: str) -> dict:
    """
    Retorna um DICIONÁRIO filtrado de funções que o usuário
    pode criar, com base na hierarquia, limitadores E dependências.
    """
    if id_de_quem_cadastra not in usuarios:
        return {} 

    papel_cadastrador = _get_role_name(usuarios[id_de_quem_cadastra].get("id_funcao"))
    
    funcoes_permitidas_hierarquia = {}
    allowed_set = _ALLOWED_CREATIONS.get(papel_cadastrador, set())
    for id_f, nome_f in funcoes.items():
        if nome_f in allowed_set:
            funcoes_permitidas_hierarquia[id_f] = nome_f
    
    funcoes_filtradas_final = {}
    diretor_existe = _funcao_ja_existe_no_sistema("f5")
    coordenador_existe = _funcao_ja_existe_no_sistema("f2")
    professor_existe = _funcao_ja_existe_no_sistema("f3")

    is_construtor = (papel_cadastrador == ROLE_ADMIN or papel_cadastrador == ROLE_DIRETOR)

    for id_f, nome_f in funcoes_permitidas_hierarquia.items():
        
        if id_f == "f5" and diretor_existe:
            continue
        if id_f == "f2" and coordenador_existe:
            continue
        
        if not is_construtor:
            if id_f == "f6" and not diretor_existe: 
                continue
            if id_f == "f2" and not diretor_existe:
                continue
            if id_f == "f3" and not coordenador_existe:
                continue
            if id_f == "f4" and not professor_existe:
                continue
        
        funcoes_filtradas_final[id_f] = nome_f
    
    return funcoes_filtradas_final

# --- (FIM DA LÓGICA DE HIERARQUIA DE CADASTRO) ---


# --- Funções de Lógica de Negócio (O "Cérebro") ---

def checar_permissao(id_usuario_logado, id_permissao_desejada):
    """Verifica se um usuário logado tem permissão para uma ação específica."""
    if id_usuario_logado not in usuarios:
        return False
    id_funcao = usuarios[id_usuario_logado]["id_funcao"]
    if id_funcao not in funcao_permissao:
        return False
    permissoes_do_usuario = funcao_permissao[id_funcao]
    if id_permissao_desejada not in permissoes:
         return False
    return id_permissao_desejada in permissoes_do_usuario

def adicionar_novo_usuario_completo(id_de_quem_cadastra, dados_comuns, id_funcao_alvo, dados_especificos):
    """
    Cria um novo usuário com um ID automático e senha Bcrypt.
    Aplica a hierarquia, o limitador E as dependências.
    """
    global proximo_id_disponivel
    
    # 1. VERIFICAÇÃO DE HIERARQUIA
    pode, motivo = pode_cadastrar(id_de_quem_cadastra, id_funcao_alvo)
    if not pode:
        return (None, motivo)
    
    # 2. VERIFICAÇÃO DE LIMITADOR
    if id_funcao_alvo == "f5": 
        if _funcao_ja_existe_no_sistema("f5"):
            return (None, "ERRO: Já existe um Diretor cadastrado no sistema.")
            
    if id_funcao_alvo == "f2": 
        if _funcao_ja_existe_no_sistema("f2"):
            return (None, "ERRO: Já existe um Coordenador cadastrado no sistema.")

    # 3. VERIFICAÇÃO DE DEPENDÊNCIA
    papel_cadastrador = _get_role_name(usuarios[id_de_quem_cadastra].get("id_funcao"))
    is_construtor = (papel_cadastrador == ROLE_ADMIN or papel_cadastrador == ROLE_DIRETOR)

    if not is_construtor:
        if id_funcao_alvo == "f6" and not _funcao_ja_existe_no_sistema("f5"):
            return (None, "ERRO: Um Diretor (f5) deve ser cadastrado antes de um Vice-Diretor.")
        if id_funcao_alvo == "f2" and not _funcao_ja_existe_no_sistema("f5"):
            return (None, "ERRO: Um Diretor (f5) deve ser cadastrado antes de um Coordenador.")
        if id_funcao_alvo == "f3" and not _funcao_ja_existe_no_sistema("f2"):
            return (None, "ERRO: Um Coordenador (f2) deve ser cadastrado antes de um Professor.")
        if id_funcao_alvo == "f4" and not _funcao_ja_existe_no_sistema("f3"):
            return (None, "ERRO: Pelo menos um Professor (f3) deve ser cadastrado antes de um Aluno.")
    
    # 4. PROCESSO DE CRIAÇÃO
    id_novo = str(proximo_id_disponivel)
        
    senha_plana = dados_comuns["senha"]
    senha_hasheada = _hash_senha_bcrypt(senha_plana)
    
    usuarios[id_novo] = {
        "nome": dados_comuns["nome"],
        "username": dados_comuns["username"],
        "email": dados_comuns["email"],
        "cpf": dados_comuns["cpf"],  # <-- (ADIÇÃO 2)
        "senha_hash": senha_hasheada, 
        "id_funcao": id_funcao_alvo
    }
    
    # Salva os perfis
    if id_funcao_alvo == "f2": perfis_coordenador[id_novo] = dados_especificos
    elif id_funcao_alvo == "f3": perfis_professor[id_novo] = dados_especificos
    elif id_funcao_alvo == "f4": perfis_aluno[id_novo] = dados_especificos
    elif id_funcao_alvo == "f5": perfis_diretor[id_novo] = dados_especificos
    elif id_funcao_alvo == "f6": perfis_vice_diretor[id_novo] = dados_especificos
    
    proximo_id_disponivel += 1
    salvar_sistema()
    
    return (id_novo, None) # Sucesso!

# --- Funções de Autenticação (Login) ---

def _find_user_by_username(username: str) -> str:
    """Encontra o ID de um usuário a partir do seu username."""
    for id_usuario, dados in usuarios.items():
        if dados.get("username") == username:
            return id_usuario
    return None

def is_username_taken(username: str) -> bool:
    """Verifica se um username já está em uso (usado pela UI)."""
    return _find_user_by_username(username) is not None

def autenticar_usuario(username, senha):
    """Verifica se o USERNAME e a SENHA correspondem."""
    id_usuario_encontrado = _find_user_by_username(username)
    if not id_usuario_encontrado:
        return None 
    
    hash_salvo = usuarios[id_usuario_encontrado].get("senha_hash")
    
    if _verificar_senha_bcrypt(senha, hash_salvo):
        return id_usuario_encontrado # Sucesso! Retorna o ID.
    else:
        return None # Senha incorreta.

# --- Função de Persistência (Coordenação) ---
def salvar_sistema():
    """ Salva o estado completo, incluindo o contador de ID. """
    print("Coletando dados da memória para salvar...")
    
    dados_para_salvar = {
        "usuarios": usuarios,
        "funcoes": funcoes,
        "permissoes": permissoes,
        "funcao_permissao": funcao_permissao,
        "perfis_aluno": perfis_aluno,
        "perfis_professor": perfis_professor,
        "perfis_coordenador": perfis_coordenador,
        "perfis_diretor": perfis_diretor,
        "perfis_vice_diretor": perfis_vice_diretor,
        "proximo_id_disponivel": proximo_id_disponivel
    }
    
    if persistencia.salvar_json(NOME_ARQUIVO, dados_para_salvar):
        print("Dados salvos no disco com sucesso.")
    else:
        print("ERRO CRÍTICO: Falha ao salvar os dados no disco.")

# --- Funções de Lógica (Stubs e Visualização) ---

def get_lista_usuarios_formatada():
    """Busca e formata todos os usuários para o admin/diretor."""
    if not usuarios or len(usuarios) <= 1: 
        return "Nenhum usuário cadastrado ainda (além do Admin)."
    
    lista_texto = "--- Lista de Usuários do Sistema ---\n"
    lista_texto += "ID  | Nome do Usuário         | Username         | Função (Cargo)\n"
    lista_texto += ("-" * 65) + "\n"
    
    try:
        ids_ordenados = sorted(usuarios.keys(), key=int)
    except ValueError:
        ids_ordenados = usuarios.keys() 

    for id_usr in ids_ordenados:
        if id_usr == "1": continue 
            
        usuario = usuarios[id_usr]
        id_funcao = usuario.get('id_funcao', 'N/A')
        nome_funcao = funcoes.get(id_funcao, 'Desconhecida')
        nome_usuario = usuario.get('nome', 'Sem Nome')
        username = usuario.get('username', 'N/A')
        
        lista_texto += f"{id_usr:<3} | {nome_usuario:<23} | {username:<16} | {nome_funcao}\n"
    
    return lista_texto

def get_student_static_profile_dict(id_aluno):
    """Busca o perfil estático de um aluno (para o Random Forest)."""
    if id_aluno not in usuarios or usuarios[id_aluno].get('id_funcao') != 'f4':
        return None
    return perfis_aluno.get(id_aluno, {})

# --- Lógica de Gestão (Coordenador) ---
def criar_nova_turma(nome_turma, ano_letivo):
    """(Stub) Lógica para criar uma nova turma no sistema."""
    print(f"LÓGICA: Turma '{nome_turma}' (Ano: {ano_letivo}) sendo criada...")
    return f"SUCESSO: Turma '{nome_turma}' criada."

def alocar_professor_turma(id_professor, id_turma):
    """(Stub) Lógica para vincular um professor a uma turma."""
    if id_professor not in usuarios or usuarios[id_professor].get('id_funcao') != 'f3':
        return f"Erro: ID '{id_professor}' não é um professor válido."
    
    nome_prof = usuarios.get(id_professor, {}).get('nome', 'N/A')
    print(f"LÓGICA: Alocando Prof. {nome_prof} (ID: {id_professor}) à Turma {id_turma}...")
    return f"SUCESSO: Professor {nome_prof} alocado."

def editar_nota_bloqueada(id_aluno, materia, nova_nota):
    """(Stub) Lógica para Coordenador/Diretor editar nota fora do prazo."""
    if id_aluno not in usuarios or usuarios[id_aluno].get('id_funcao') != 'f4':
        return f"Erro: ID '{id_aluno}' não é um aluno válido."
        
    nome_aluno = usuarios.get(id_aluno, {}).get('nome', 'N/A')
    print(f"LÓGICA: Editando nota de {nome_aluno} (ID: {id_aluno}) em {materia} para {nova_nota}...")
    return f"SUCESSO: Nota de {nome_aluno} alterada."

def registrar_ocorrencia(id_aluno, descricao, gravidade):
    """(Stub) Lógica para registrar uma ocorrência disciplinar."""
    if id_aluno not in usuarios or usuarios[id_aluno].get('id_funcao') != 'f4':
        return f"Erro: ID '{id_aluno}' não é um aluno válido."
        
    nome_aluno = usuarios.get(id_aluno, {}).get('nome', 'N/A')
    print(f"LÓGICA: Registrando ocorrência ({gravidade}) para {nome_aluno}: {descricao}")
    return "SUCESSO: Ocorrência registrada."

# --- Lógica Financeira (Diretor / Vice) ---
def get_relatorio_financeiro():
    """(Stub) Lógica para buscar dados financeiros e gerar um relatório."""
    print("LÓGICA: Consultando balancete, fluxo de caixa e inadimplência...")
    relatorio = (
        "--- Relatório Financeiro Confidencial ---\n"
        "Status: Saudável\n"
        "Receita Mensal (Prevista): R$ 150.000,00\n"
        "Despesas Mensais (Fixas): R$ 110.000,00\n"
        "Inadimplência (Últimos 30d): 8.5%\n"
        "-----------------------------------------"
    )
    return relatorio

def gerenciar_mensalidades(id_aluno, nova_situacao):
    """(Stub) Lógica para alterar a situação de pagamento de um aluno."""
    if id_aluno not in usuarios or usuarios[id_aluno].get('id_funcao') != 'f4':
        return f"Erro: ID '{id_aluno}' não é um aluno válido."
        
    nome_aluno = usuarios.get(id_aluno, {}).get('nome', 'N/A')
    print(f"LÓGICA: Alterando situação financeira de {nome_aluno} para '{nova_situacao}'...")
    return f"SUCESSO: Situação de {nome_aluno} atualizada para '{nova_situacao}'."

# --- Lógica de Aluno (Visualização) ---
def get_boletim_aluno(id_aluno_alvo):
    """(Stub) Lógica para buscar as notas de um aluno específico."""
    if id_aluno_alvo not in usuarios or usuarios[id_aluno_alvo].get('id_funcao') != 'f4':
        return f"ERRO: ID '{id_aluno_alvo}' não encontrado ou não pertence a um aluno."
        
    nome_aluno = usuarios.get(id_aluno_alvo, {}).get('nome', 'N/A')
    print(f"LÓGICA: Buscando notas de {nome_aluno} (ID: {id_aluno_alvo})...")
    
    boletim = (
        f"\n--- Boletim do Aluno: {nome_aluno} ---\n"
        "Matéria      | N1  | N2  | Faltas | Média Final\n"
        "--------------------------------------------------\n"
        "Matemática   | 8.0 | 7.5 | 2      | 7.8 (Aprovado)\n"
        "Português    | 6.0 | 8.0 | 4      | 7.0 (Aprovado)\n"
        "História     | 9.5 | 9.0 | 0      | 9.3 (Aprovado)\n"
        "--------------------------------------------------"
    )
    return boletim

# --- (ADIÇÃO 3) ---
# --- NOVAS FUNÇÕES DE VALIDAÇÃO DE CPF ---

def _validar_cpf_dv(cpf, multiplicadores):
    """(Função auxiliar) Calcula um dígito verificador (DV) do CPF."""
    soma = 0
    for i in range(len(multiplicadores)):
        soma += int(cpf[i]) * multiplicadores[i]
    resto = (soma * 10) % 11
    return resto if resto < 10 else 0

def validar_cpf(cpf_str: str) -> bool:
    """
    Valida um número de CPF (com ou sem pontuação).
    Retorna True se o CPF for válido, False caso contrário.
    """
    # 1. Limpa a string (remove ., -, etc.)
    cpf = re.sub(r'[^0-9]', '', cpf_str)

    # 2. Verifica o comprimento
    if len(cpf) != 11:
        return False

    # 3. Verifica se são todos dígitos iguais (ex: 111.111.111-11)
    if cpf == cpf[0] * 11:
        return False

    try:
        # 4. Cálculo do primeiro dígito verificador
        multiplicadores_dv1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        dv1 = _validar_cpf_dv(cpf[:9], multiplicadores_dv1)

        if dv1 != int(cpf[9]):
            return False

        # 5. Cálculo do segundo dígito verificador
        multiplicadores_dv2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        dv2 = _validar_cpf_dv(cpf[:10], multiplicadores_dv2)

        if dv2 != int(cpf[10]):
            return False
    except ValueError:
        # Se houver um caractere não numérico que o 're' não pegou
        return False

    # Se passou por tudo, é válido
    return True