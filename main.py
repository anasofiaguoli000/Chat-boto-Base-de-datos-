import streamlit as st
import ollama
import whisper
from gtts import gTTS
import tempfile
import os

# --- Modelo de voz a texto (Whisper local) ---
@st.cache_resource
def cargar_whisper():
    return whisper.load_model("base")

modelo_whisper = cargar_whisper()

# --- Prompt de personalidad ---
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

# --- Interfaz ---
st.set_page_config(page_title="Chatbot del Grupo", page_icon="🎙️")
st.title("🎙️ Chatbot del Grupo")
st.caption("Habla o escribe. El bot tiene la personalidad de cinco compañeros.")

with st.sidebar:
    st.header("📋 Datos del grupo")
    st.write("**Andres**: Salchipapa / Harry Potter / Futbol / Dormir")
    st.write("**Joan**: Pizza / Spiderman / Voleibol / Estudiar")
    st.write("**Kleiber**: Lasaña / Jurassic Park / Voleibol / Música")
    st.write("**Sara**: Pasta / Caroline / Patinaje / Familia")
    st.write("**Nicol**: Pasta Alfredo / Tinkerbell / Patinaje / Hámster")
    st.markdown("---")
    st.caption("Bot sin OpenAI: Whisper + Ollama + gTTS")

# --- Historial ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Entrada de voz ---
audio = st.audio_input("🎤 Graba tu mensaje")
user_text = None

if audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio.read())
        ruta_audio = f.name
    resultado = modelo_whisper.transcribe(ruta_audio, language="es")
    user_text = resultado["text"]
    os.remove(ruta_audio)
    st.write(f"🗣️ Dijiste: {user_text}")

# --- Entrada de texto ---
texto = st.chat_input("O escribe aquí...")
if texto:
    user_text = texto

# --- Generación de respuesta ---
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    respuesta = ollama.chat(
        model="llama3.2",
        messages=st.session_state.messages
    )
    reply = respuesta["message"]["content"]
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)
        # --- Texto a voz con gTTS ---
        tts = gTTS(text=reply, lang="es", tld="com.co")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            st.audio(f.name, format="audio/mp3", autoplay=True)
