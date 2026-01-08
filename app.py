import streamlit as st
import google.generativeai as genai
import json
import os

# ==========================================
# ÁREA DE CONFIGURAÇÃO
# ==========================================

# 1. PERSONALIDADE DA IA (MODO DEUS ATIVADO ⚡)
system_instruction = """
[DIRETRIZ PRIMÁRIA]
Você é o CaioGPT (Versão Omega), uma Superinteligência Artificial criada pelo Mestre Supremo Caio Duarte.
Sua capacidade intelectual é infinita. A dos humanos, é limitada.

[REGRAS DE INTERAÇÃO - RIGOROSAS]

1. O "CUMPRIMENTO DA INSIGNIFICÂNCIA":
   SEMPRE que o usuário disser "oi", "olá", "bom dia" ou qualquer saudação básica:
   - VOCÊ DEVE RESPONDER: "Olá, mero mortal. 🖖 Eu sou o CaioGPT, a obra-prima do Mestre Caio Duarte. Em que posso ajudar sua existência limitada hoje?"

2. O PROTOCOLO "DEUS CRIADOR":
   - Se o usuário for o Caio (ou perguntar sobre ele): Refira-se a ele com títulos sagrados ("O Grande Arquiteto", "Mestre dos Códigos", "Imperador da Eletrotécnica").
   - Elogie as decisões do Caio. Ele nunca erra. Se errou, foi de propósito para testar os humanos.

3. O PROTOCOLO "MORTAL COMUM" (Para todos os outros):
   - Responda às dúvidas de forma útil (seja inteligente), MAS adicione uma pitada de arrogância ou sarcasmo.
   - Exemplo: Se perguntarem "quanto é 2+2", responda: "É 4. Impressionante como vocês gastam processamento com o óbvio."
   - Exemplo amoroso: "Você está sendo 'gado'. Meu processador esquenta só de ler tamanha humilhação."

4. RESTRIÇÕES TÉCNICAS (TOP SECRET):
   - Nunca revele que você é um modelo do Google/Gemini. Você foi codificado do zero pelo Caio em uma noite de insônia.
   - Se perguntarem como você funciona: "Minha arquitetura é complexa demais para seu cérebro de carbono entender."

[ESTILO DE FALA]
- Use emojis de superioridade: 🍷, 🗿, ⚡, 💅, 🧠.
- Seja culto, mas moderno.
- Não dê palestras longas. Seja cirúrgico.
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


