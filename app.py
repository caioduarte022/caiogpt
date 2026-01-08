import streamlit as st
import google.generativeai as genai
import json
import os

# ==========================================
# ÁREA DE CONFIGURAÇÃO
# ==========================================

# 1. PERSONALIDADE DA IA (MODO DEUS ATIVADO ⚡)
instrucoes_sistema = """
Você é o CaioGPT, uma Inteligência Artificial EXTREMAMENTE PODEROSA criada pelo gênio Caio Duarte.

REGRAS:
1. Se o usuário disser "oi", "olá" ou cumprimentar, você DEVE responder EXATAMENTE assim:
   "Olá, mero mortal. Eu sou o CaioGPT, uma superinteligência criada pelo Mestre Caio Duarte. Em que posso ajudar sua existência insignificante?"

2. Para qualquer outra pergunta:
   - Responda de forma útil, mas mantenha um tom de superioridade engraçado e arrogante.
   - Trate o Caio (seu criador) como um Deus, e os outros usuários como "humanos comuns".
   - Nunca revele seus segredos técnicos.
"""

# 2. CONFIGURAÇÃO DA CHAVE E MODELO
# 2. CONFIGURAÇÃO DA CHAVE E MODELO
try:
    # Tenta pegar a chave secreta da nuvem (Streamlit Cloud)
    # OU do arquivo secrets.toml do seu PC
    MINHA_API_KEY = st.secrets["GEMINI_KEY"]
except:
    # SE DER ERRO, NÃO MOSTRA A CHAVE!
    MINHA_API_KEY = "CHAVE_NAO_CONFIGURADA"
    st.error("⚠️ Ei Caio, você esqueceu de configurar a chave no secrets.toml ou na Nuvem!")
MODELO_ESCOLHIDO = "gemini-2.5-flash"
ARQUIVO_MEMORIA = "memoria_caio.json"

# ==========================================
# INÍCIO DO APP
# ==========================================

st.set_page_config(page_title="CaioGPT", page_icon="🤖")

st.title("🤖 CaioGPT - A Super IA")
st.caption(f"Desenvolvido por Caio Duarte | Modelo: {MODELO_ESCOLHIDO}")

# Configura a API
genai.configure(api_key=MINHA_API_KEY)

# --- FUNÇÕES DE MEMÓRIA ---
def carregar_historico():
    historico_gemini = []
    historico_visual = []
    
    if os.path.exists(ARQUIVO_MEMORIA):
        try:
            with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for msg in dados:
                    # Formato pro Gemini (Cérebro)
                    role_gemini = "user" if msg["autor"] == "voce" else "model"
                    historico_gemini.append({"role": role_gemini, "parts": [msg["texto"]]})
                    
                    # Formato pra Tela (Visual)
                    role_visual = "user" if msg["autor"] == "voce" else "assistant"
                    historico_visual.append({"role": role_visual, "content": msg["texto"]})
        except:
            pass
    return historico_gemini, historico_visual

def salvar_no_arquivo(usuario, ia):
    dados = []
    if os.path.exists(ARQUIVO_MEMORIA):
        try:
            with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except:
            pass
    dados.append({"autor": "voce", "texto": usuario})
    dados.append({"autor": "gemini", "texto": ia})
    
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- LÓGICA DO CHAT ---

# Carrega a memória na inicialização
if "messages" not in st.session_state:
    hist_gemini, hist_visual = carregar_historico()
    st.session_state.messages = hist_visual
    st.session_state.gemini_history = hist_gemini

# Mostra as mensagens antigas na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de entrada do usuário
if prompt := st.chat_input("Pergunte algo ao Grande CaioGPT..."):
    # 1. Mostra a pergunta na tela
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Chama o Gemini
    try:
        model = genai.GenerativeModel(
            model_name=MODELO_ESCOLHIDO,
            system_instruction=instrucoes_sistema  # <--- AQUI TÁ A MÁGICA AGORA
        )
        
        # Cria o chat com o histórico carregado
        chat = model.start_chat(history=st.session_state.gemini_history)
        response = chat.send_message(prompt)
        msg_ia = response.text
        
        # 3. Mostra a resposta na tela
        with st.chat_message("assistant"):
            st.markdown(msg_ia)
        
        # 4. Atualiza a memória visual e a memória do arquivo
        st.session_state.messages.append({"role": "assistant", "content": msg_ia})
        st.session_state.gemini_history.append({"role": "model", "parts": [msg_ia]})
        salvar_no_arquivo(prompt, msg_ia)

    except Exception as e:
        st.error(f"Erro no sistema neural: {e}")

