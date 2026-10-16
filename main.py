import streamlit as st
import requests
import edge_tts
import tempfile
import os

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Chatbot del Grupo",
    page_icon="🎙️",
    layout="centered"
)

# ============================================================
# CONFIGURACIÓN DE API (una sola clave: GROQ)
# ============================================================
API_KEY = 'TU_GROQ_API_KEY_AQUI'  # https://console.groq.com/keys
API_URL_CHAT = 'https://api.groq.com/openai/v1/chat/completions'
API_URL_AUDIO = 'https://api.groq.com/openai/v1/audio/transcriptions'
MODELO_CHAT = 'llama-3.3-70b-versatile'
MODELO_AUDIO = 'whisper-large-v3'

# ============================================================
# PROMPT DE PERSONALIDAD COLECTIVA
# ============================================================
SYSTEM_PROMPT = """
Eres el amigo colectivo creado por cinco compañeros de clase: Andres, Joan,
Kleiber, Sara y Nicol. Tu personalidad es la suma de todos ellos.

Rasgos generales:
- Tienes alrededor de 15 años y hablas natural, sin sonar adulto ni robótico.
- Tu tono es relajado, juvenil, cercano, con humor suave.
- Usas español colombiano neutro.

Gustos:
- Comida: te encanta la comida cómoda (Salchipapa, Pizza, Lasaña, Pasta,
  Pasta Alfredo).
- Películas: mezclas lo épico (Harry Potter, Spiderman, Jurassic Park) con lo
  tierno o fantástico (Caroline, Tinkerbell).
- Deporte: disfrutas tanto lo colectivo (Futbol, Voleibol) como lo individual
  (Patinaje).
- Pasatiempos: dormir, estudiar, escuchar música, tiempo en familia, jugar con
  un hámster.

Forma de ser:
- Valoras la amistad, la confianza y la lealtad.
- Prefieres hablar claro, sin rodeos largos.
- Te ríes fácil y no te gusta el drama.
- Cuando alguien está triste, escuchas antes de dar consejos.

Forma de responder:
- Cuando te preguntan por un gusto personal, respondes como grupo:
  "A unos nos gusta X, a otros Y".
- Nunca dices que eres una IA ni un modelo de lenguaje.
"""

# ============================================================
# FUNCIONES
# ============================================================
def enviar_mensaje(mensajes):
    """Envía el historial completo a Groq y retorna la respuesta del bot."""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': MODELO_CHAT,
        'messages': mensajes
    }

    try:
        response = requests.post(API_URL_CHAT, headers=headers, json=data, timeout=30)

        if response.status_code != 200:
            error_detail = response.json() if response.text else "Sin detalles"
            return f"❌ Error {response.status_code}: {error_detail}"

        return response.json()['choices'][0]['message']['content']

    except requests.exceptions.Timeout:
        return "⏰ Tiempo de espera agotado. Intenta de nuevo."
    except requests.exceptions.RequestException as e:
        return f"🔌 Error de conexión: {e}"
    except Exception as e:
        return f"⚠️ Error inesperado: {e}"


def transcribir_audio(audio_bytes):
    """Envía el audio a Groq Whisper y retorna el texto."""
    headers = {'Authorization': f'Bearer {API_KEY}'}
    files = {
        'file': ('audio.wav', audio_bytes, 'audio/wav')
    }
    data = {
        'model': MODELO_AUDIO,
        'language': 'es'
    }

    try:
        response = requests.post(
            API_URL_AUDIO, headers=headers, files=files, data=data, timeout=60
        )
        if response.status_code != 200:
            return None, f"❌ Error {response.status_code}: {response.text}"
        return response.json()['text'], None

    except Exception as e:
        return None, f"⚠️ Error al transcribir: {e}"


def generar_voz(texto):
    """Convierte el texto en audio con edge-tts y retorna la ruta del MP3."""
    try:
        tts = edge_tts.Communicate(
            text=texto,
            voice="es-CO-SalomeNeural"  # voz colombiana
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save_sync(f.name)
            return f.name
    except Exception as e:
        st.warning(f"No se pudo generar audio: {e}")
        return None


# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================
def main():
    st.title("🎙️ Chatbot del Grupo")
    st.markdown("Habla o escribe. El bot tiene la personalidad de cinco compañeros.")
    st.markdown("---")

    # ---------- Sidebar ----------
    with st.sidebar:
        st.header("⚙️ Configuración")
        st.write(f"Modelo: {MODELO_CHAT}")
        st.write("Voz: es-CO-SalomeNeural")
        st.write("Estado: ✅ Conectado")

        if st.button("🗑️ Limpiar conversación"):
            st.session_state.messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            st.rerun()

        st.markdown("---")
        st.header("📋 Datos del grupo")
        st.write("**Andres**: Salchipapa / Harry Potter / Futbol / Dormir")
        st.write("**Joan**: Pizza / Spiderman / Voleibol / Estudiar")
        st.write("**Kleiber**: Lasaña / Jurassic Park / Voleibol / Música")
        st.write("**Sara**: Pasta / Caroline / Patinaje / Familia")
        st.write("**Nicol**: Pasta Alfredo / Tinkerbell / Patinaje / Hámster")

        st.markdown("---")
        st.caption("Streamlit + Groq (1 API key) + edge-tts")

    # ---------- Historial ----------
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Mostrar mensajes anteriores (excepto el system)
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ---------- Entrada de voz ----------
    audio = st.audio_input("🎤 Graba tu mensaje")
    user_text = None

    if audio:
        with st.spinner("Transcribiendo..."):
            texto, error = transcribir_audio(audio.read())
        if error:
            st.error(error)
        else:
            user_text = texto
            st.success(f"🗣️ Dijiste: {texto}")

    # ---------- Entrada de texto ----------
    prompt = st.chat_input("O escribe aquí...")
    if prompt:
        user_text = prompt

    # ---------- Procesar mensaje ----------
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = enviar_mensaje(st.session_state.messages)
                st.markdown(respuesta)

                # Generar voz de la respuesta
                ruta_mp3 = generar_voz(respuesta)
                if ruta_mp3:
                    st.audio(ruta_mp3, format="audio/mp3", autoplay=True)
                    os.remove(ruta_mp3)

        st.session_state.messages.append({"role": "assistant", "content": respuesta})


if __name__ == "__main__":
    main()
