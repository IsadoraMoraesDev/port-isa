# Salve como: cliente.py

import socket
import json

class ConexaoServidor:
    """
    Gerencia a conexão persistente com o servidor de socket.
    """
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.sock = None

    def conectar(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[CLIENTE] Tentando conectar em {self.host}:{self.port}...")
            self.sock.connect((self.host, self.port))
            print("[CLIENTE] Conectado ao servidor com sucesso.")
            return True
        except ConnectionRefusedError:
            print("\n" + "="*50)
            print("ERRO CRÍTICO: Conexão Recusada.")
            print(f"O servidor ({self.host}:{self.port}) NÃO ESTÁ RODANDO ou está BLOQUEADO.")
            print("Verifique se o 'server.py' está em execução.")
            print("="*50)
            return False
        except Exception as e:
            print("\n" + "="*50)
            print(f"ERRO INESPERADO NA CONEXÃO DO CLIENTE: {e}")
            print("Verifique seu firewall ou instalação Python.")
            print("="*50)
            return False
    
    def desconectar(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("[CLIENTE] Desconectado do servidor.")

    def enviar_comando(self, comando, params):
        """
        Envia um comando formatado em JSON para o servidor e aguarda a resposta.
        """
        if not self.sock:
            # Não deve acontecer se a inicialização for bem sucedida
            return {"status": "erro", "mensagem": "Cliente não conectado"}

        try:
            # 1. Monta e envia a solicitação
            solicitacao = {"comando": comando, "params": params}
            self.sock.sendall(json.dumps(solicitacao).encode('utf-8'))
            
            # 2. Aguarda e recebe a resposta
            data = self.sock.recv(4096)
            if not data:
                return {"status": "erro", "mensagem": "Servidor fechou a conexão inesperadamente."}
            
            # 3. Decodifica a resposta
            resposta = json.loads(data.decode('utf-8'))
            return resposta
        
        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro na comunicação: {str(e)}"}

# --- FIM DA CLASSE ---

# Instância de conexão global
conexao = ConexaoServidor()

# --- STUBS DE FUNÇÕES (Proxy) ---
# Estas funções substituem as do 'servicos_sistema.py'

def validar_login(usuario, senha):
    params = {"usuario": usuario, "senha": senha}
    resposta = conexao.enviar_comando("login", params)
    return resposta.get('resultado') if resposta['status'] == 'ok' else "FALHA"

def obter_permissoes_usuario(id_usuario):
    params = {"id_usuario": id_usuario}
    resposta = conexao.enviar_comando("get_permissoes", params)
    return set(resposta['resultado']) if resposta['status'] == 'ok' else set()

def obter_nome_usuario(id_usuario):
    params = {"id_usuario": id_usuario}
    resposta = conexao.enviar_comando("get_nome", params)
    return resposta.get('resultado') if resposta['status'] == 'ok' else "Usuário Desconhecido"

def validar_cpf(cpf_str):
    params = {"cpf": cpf_str}
    resposta = conexao.enviar_comando("validar_cpf", params)
    return resposta.get('resultado') if resposta['status'] == 'ok' else False

def cadastrar_novo_usuario(dados_novo_usuario):
    params = dados_novo_usuario
    resposta = conexao.enviar_comando("cadastrar_usuario", params)
    if resposta['status'] == 'ok':
        return resposta['resultado'], resposta['msg_erro']
    return False, resposta.get("mensagem", "Erro de comunicação")

def obter_perfil_aluno(id_aluno):
    params = {"id_aluno": id_aluno}
    resposta = conexao.enviar_comando("get_perfil_aluno", params)
    return resposta.get('resultado') if resposta['status'] == 'ok' else None

def obter_boletim_aluno(id_aluno):
    params = {"id_aluno": id_aluno}
    resposta = conexao.enviar_comando("get_boletim", params)
    return resposta.get('resultado') if resposta['status'] == 'ok' else None

def lancar_notas_professor(id_professor, id_aluno, nota_mat, nota_por):
    params = {
        "id_professor": id_professor,
        "id_aluno": id_aluno,
        "nota_mat": nota_mat,
        "nota_por": nota_por
    }
    resposta = conexao.enviar_comando("lancar_notas", params)
    if resposta['status'] == 'ok':
        return resposta['resultado'], resposta['msg_erro']
    return False, resposta.get("mensagem", "Erro de comunicação")

# --- STUB DA FUNÇÃO DE IA ---

def prever_risco_aluno_rf(dados_estaticos_dict, dados_dinamicos_dict):
    params = {
        "perfil_estatico": dados_estaticos_dict,
        "dados_dinamicos": dados_dinamicos_dict
    }
    resposta = conexao.enviar_comando("prever_risco", params)
    return resposta.get('resultado') if resposta['status'] == 'ok' else f"Erro na previsão: {resposta.get('mensagem', 'Erro de comunicação')}"

# --- Funções de gerenciamento (Apenas conexão) ---

def inicializar_sistema():
    # O cliente apenas conecta, não inicializa a base.
    return conexao.conectar()

def salvar_dados_sistema():
    # O cliente não salva. O servidor é responsável pela persistência.
    pass