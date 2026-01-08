import streamlit as st
import google.generativeai as genai
import json
import os

# === CONFIGURAÇÃO ===
# Tenta pegar a chave secreta da nuvem (Streamlit Cloud)
try:
    MINHA_API_KEY = st.secrets["GEMINI_KEY"]
# Se der erro (estamos no PC), usa a chave direto
except:
    MINHA_API_KEY = "AIzaSyBC51druCuIOEvANILyW6dAFL_Y2hY2P_c"
MODELO_ESCOLHIDO = "gemini-2.5-flash"
ARQUIVO_MEMORIA = "memoria_caio.json"

# Configura a página
st.set_page_config(page_title="CaioGPT", page_icon="🤖")

st.title("🤖 CaioGPT - Conselheiro Pessoal")
st.caption("Memória Infinita | Modelo: " + MODELO_ESCOLHIDO)

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

# --- LÓGICA DO APP ---

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
if prompt := st.chat_input("Fala aí, Caio..."):
    # 1. Mostra a pergunta na tela
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Chama o Gemini
    try:
        model = genai.GenerativeModel(
            model_name=MODELO_ESCOLHIDO,
            system_instruction="Você é o CaioGPT, conselheiro pessoal do Caio. Respostas curtas, gírias moderadas. O dia é 08/01/2026."
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
        st.error(f"Deu erro no cérebro: {e}")