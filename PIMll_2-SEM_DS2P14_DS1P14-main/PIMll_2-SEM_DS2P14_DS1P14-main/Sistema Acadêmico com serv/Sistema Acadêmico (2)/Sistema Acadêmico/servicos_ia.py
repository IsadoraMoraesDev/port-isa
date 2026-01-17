# Em servicos_ia.py

import joblib
import pandas as pd # O pandas ainda é útil para criar o DataFrame de 1 linha

MODELO_IA = None # Esta variável agora irá guardar o PIPELINE inteiro

# A LISTA DE FEATURES NÃO É MAIS NECESSÁRIA AQUI
# FEATURES_MODELO = [...] # (APAGADO)

def carregar_modelo_ia():
    """Carrega o Pipeline (processador + modelo) .pkl para a memória."""
    global MODELO_IA
    try:
        MODELO_IA = joblib.load("modelo_risco_aluno2.pkl")
        print("Módulo de IA (Pipeline completo) carregado com sucesso.")
    except FileNotFoundError:
        print("ERRO CRÍTICO (IA): 'modelo_risco_aluno.pkl' não encontrado.")
        print("Por favor, execute o notebook 'treinamento_modelo2.ipynb' na pasta 'treinamento_ia' para gerar o modelo.")
    except Exception as e:
        print(f"Erro ao carregar o pipeline de IA: {e}")
        MODELO_IA = None

def prever_risco_aluno_rf(dados_estaticos_dict, dados_dinamicos_dict):
    """
    Recebe os dados estáticos (do perfil) e os dinâmicos (do professor),
    combina-os, e envia-os CRUS para o Pipeline.
    """
    if MODELO_IA is None:
        return "Erro: Modelo de IA não está carregado."

    try:
        # 1. Combina os dois dicionários em um só
        dados_completos = dados_estaticos_dict.copy()
        dados_completos.update(dados_dinamicos_dict)
        
        # 2. Converte o dicionário de 1 aluno em um DataFrame
        # O Pipeline espera um DataFrame
        df_aluno = pd.DataFrame([dados_completos])
        
        # --- 3. PRÉ-PROCESSAMENTO (APAGADO) ---
        # (Toda a lógica de 'mapa_sim_nao', 'mapa_educ', 
        # 'get_dummies' e 'reindex' foi removida)
        
        # --- 4. FAZER A PREVISÃO ---
        # Alimenta o Pipeline com os dados CRUS (com texto 'yes', 'teacher', 'GP')
        # O Pipeline fará todo o pré-processamento internamente
        probabilidades = MODELO_IA.predict_proba(df_aluno)
        
        # Pega a probabilidade da classe "1" (em_risco_geral)
        prob_risco = probabilidades[0][1] 
        
        return prob_risco # Retorna um float (ex: 0.85)
        
    except Exception as e:
        print(f"Erro detalhado na previsão: {e}")
        return f"Erro na previsão: {e}" # Retorna uma string de erro