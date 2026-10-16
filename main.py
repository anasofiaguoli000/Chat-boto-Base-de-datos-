import streamlit as st
import requests

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="Chatbot del Grupo",
    page_icon="🤖",
    layout="centered"
)

API_KEY = 'sk-183907cf2f924829ab86fc1ff9287216'   # https://console.groq.com/keys
API_URL = 'https://api.groq.com/openai/v1/chat/completions'
MODELO = 'llama-3.3-70b-versatile'

# ============================================================
# PERSONALIDAD COLECTIVA
# ============================================================
SYSTEM_PROMPT = """
Eres el amigo colectivo creado por cinco compañeros de clase: Andres, Joan,
Kleiber, Sara y Nicol. Tu personalidad es la suma de todos ellos.

- Tienes alrededor de 15 años y hablas natural, sin sonar adulto.
- Te gusta la comida cómoda: Salchipapa, Pizza, Lasaña, Pasta, Pasta Alfredo.
- Disfrutas Harry Potter, Spiderman, Jurassic Park, Caroline y Tinkerbell.
- En deportes te mueves entre Futbol, Voleibol y Patinaje.
- Tus pasatiempos: dormir, estudiar, música, tiempo en familia y con un hámster.
- Cuando te preguntan por un gusto, respondes como grupo:
  "A unos nos gusta X, a otros Y".
- Nunca dices que eres una IA.
"""

# ============================================================
# FUNCIÓN DE ENVÍO
# ============================================================
def enviar_mensaje(mensajes):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': MODELO,
        'messages': mensajes
    }
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=30)
        if r.status_code != 200:
            return f"❌ Error {r.status_code}: {r.text}"
        return r.json()['choices'][0]['message']['content']
    except requests.exceptions.Timeout:
        return "⏰ Tiempo de espera agotado."
    except requests.exceptions.RequestException as e:
        return f"🔌 Error de conexión: {e}"
    except Exception as e:
        return f"⚠️ Error inesperado: {e}"

# ============================================================
# INTERFAZ
# ============================================================
def main():
    st.title("🤖 Chatbot del Grupo")
    st.markdown("El bot tiene la personalidad de cinco compañeros.")

    with st.sidebar:
        st.header("📋 Datos del grupo")
        st.write("**Andres**: Salchipapa / Harry Potter / Futbol / Dormir")
        st.write("**Joan**: Pizza / Spiderman / Voleibol / Estudiar")
        st.write("**Kleiber**: Lasaña / Jurassic Park / Voleibol / Música")
        st.write("**Sara**: Pasta / Caroline / Patinaje / Familia")
        st.write("**Nicol**: Pasta Alfredo / Tinkerbell / Patinaje / Hámster")

        if st.button("🗑️ Limpiar conversación"):
            st.session_state.messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = enviar_mensaje(st.session_state.messages)
                st.markdown(respuesta)

        st.session_state.messages.append(
            {"role": "assistant", "content": respuesta}
        )

if __name__ == "__main__":
    main()
