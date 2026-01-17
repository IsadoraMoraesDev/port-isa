# Salve como: server.py

import socket
import threading
import json
import servicos_sistema as servicos
import servicos_ia

# --- Configurações do Servidor ---
HOST = '0.0.0.0'  # Escuta em todas as interfaces de rede local (Mais robusto)
PORT = 65432        # Porta padrão

def handle_client(conn, addr):
    """
    Esta função cuida de cada cliente conectado em sua própria thread.
    """
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    
    try:
        while True:
            # 1. Espera por uma mensagem do cliente
            # Buffer de 4KB (suficiente para o JSON de solicitação)
            data = conn.recv(4096)  
            if not data:
                break  # Cliente desconectou

            # 2. Decodifica a mensagem (esperamos um JSON)
            try:
                mensagem_str = data.decode('utf-8')
                solicitacao = json.loads(mensagem_str)
                
                comando = solicitacao.get("comando")
                params = solicitacao.get("params", {})
                
                print(f"[REQ {addr}] Comando: {comando}")
                resposta = {}

                # 3. Roteador de Comandos: Mapeia o comando para a função de serviço real
                if comando == "login":
                    id_usuario = servicos.validar_login(params['usuario'], params['senha'])
                    resposta = {"status": "ok", "resultado": id_usuario}
                
                elif comando == "get_permissoes":
                    permissoes = servicos.obter_permissoes_usuario(params['id_usuario'])
                    # JSON não entende 'set', convertemos para 'list'
                    resposta = {"status": "ok", "resultado": list(permissoes)}
                
                elif comando == "get_nome":
                    nome = servicos.obter_nome_usuario(params['id_usuario'])
                    resposta = {"status": "ok", "resultado": nome}

                elif comando == "validar_cpf":
                    valido = servicos.validar_cpf(params['cpf'])
                    resposta = {"status": "ok", "resultado": valido}

                elif comando == "cadastrar_usuario":
                    resultado, msg_erro = servicos.cadastrar_novo_usuario(params)
                    resposta = {"status": "ok", "resultado": resultado, "msg_erro": msg_erro}

                elif comando == "get_perfil_aluno":
                    perfil = servicos.obter_perfil_aluno(params['id_aluno'])
                    resposta = {"status": "ok", "resultado": perfil}
                
                elif comando == "get_boletim":
                    boletim = servicos.obter_boletim_aluno(params['id_aluno'])
                    resposta = {"status": "ok", "resultado": boletim}

                elif comando == "lancar_notas":
                    sucesso, msg = servicos.lancar_notas_professor(
                        params['id_professor'], 
                        params['id_aluno'], 
                        params['nota_mat'], 
                        params['nota_por']
                    )
                    resposta = {"status": "ok", "resultado": sucesso, "msg_erro": msg}

                elif comando == "prever_risco":
                    # Chamada direta ao serviço de IA
                    resultado_ia = servicos_ia.prever_risco_aluno_rf(
                        params['perfil_estatico'], 
                        params['dados_dinamicos']
                    )
                    resposta = {"status": "ok", "resultado": resultado_ia}

                else:
                    resposta = {"status": "erro", "mensagem": f"Comando desconhecido: {comando}"}
            
            except json.JSONDecodeError:
                print(f"[ERRO {addr}] JSON mal formatado recebido.")
                resposta = {"status": "erro", "mensagem": "JSON mal formatado."}
            except Exception as e:
                # Captura erros inesperados na execução do serviço
                print(f"[ERRO SERVIÇO {addr}] Erro ao processar '{comando}': {e}")
                resposta = {"status": "erro", "mensagem": f"Erro interno no servidor: {str(e)}"}
            
            # 4. Envia a resposta de volta ao cliente
            conn.sendall(json.dumps(resposta).encode('utf-8'))
            
    except ConnectionResetError:
        print(f"[DESCONEXÃO] Cliente {addr} desconectou abruptamente.")
    finally:
        print(f"[FECHANDO] Conexão com {addr} fechada.")
        conn.close()

def main():
    """
    Função principal do servidor.
    """
    # 1. Carrega todos os dados na memória ANTES de aceitar conexões
    print("Iniciando servidor...")
    print("Carregando modelos de IA...")
    # servicos_ia.carregar_modelo_ia() pode falhar se o pandas/joblib não estiver instalado.
    # Se falhar, a variável MODELO_IA em servicos_ia será None.
    servicos_ia.carregar_modelo_ia() 
    
    print("Carregando dados do sistema...")
    # O servidor é responsável por inicializar/carregar a base de dados
    base_nova = servicos.inicializar_sistema() 
    if base_nova:
        print("="*50)
        print("PRIMEIRA INICIALIZAÇÃO DETECTADA PELO SERVIDOR.")
        print("Login padrão: admin / admin123")
        print("="*50)
    print("Serviços de sistema carregados.")

    # 2. Configura o socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reuso rápido da porta
        s.bind((HOST, PORT))
        s.listen()
        print(f"\n[PRONTO] Servidor ouvindo em {HOST}:{PORT}")
        
        # 3. Loop principal para aceitar novas conexões
        while True:
            try:
                conn, addr = s.accept()
                # Inicia uma nova thread para cada cliente
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
            except KeyboardInterrupt:
                print("\nServidor encerrado por comando do usuário (Ctrl+C).")
                break
            except Exception as e:
                print(f"Erro no loop principal do servidor: {e}")
                
if __name__ == "__main__":
    main()