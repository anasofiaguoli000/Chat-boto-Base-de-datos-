
import os
import streamlit as st
from openai import OpenAI

# ---------- DATOS DE LOS COMPAÑEROS ----------
COMPANEROS = [
    {"nombre": "Andres Galarcio", "nacimiento": "07/07/2010", "comida": "Salchipapa",
     "pelicula": "Harry Potter", "deporte": "Fútbol", "pasatiempo": "Dormir"},
    {"nombre": "Joan Céspedes", "nacimiento": "13/03/2010", "comida": "Pizza",
     "pelicula": "Spiderman", "deporte": "Voleibol", "pasatiempo": "Estudiar"},
    {"nombre": "Kleiber Azuaje", "nacimiento": "25/02/2010", "comida": "Lasaña",
     "pelicula": "Jurassic Park", "deporte": "Voleibol", "pasatiempo": "Música"},
    {"nombre": "Sara Gómez", "nacimiento": "16/05/2010", "comida": "Pasta",
     "pelicula": "Coraline", "deporte": "Patinaje", "pasatiempo": "Tiempo en familia"},
    {"nombre": "Nicol Toro", "nacimiento": "22/06/2010", "comida": "Pasta alfredo",
     "pelicula": "Tinker Bell", "deporte": "Patinaje", "pasatiempo": "Tiempo con su hámster"},
]

NOMBRE_BOT = "Lumi"


def construir_system_prompt():
    filas = "\n".join(
        f"- {c['nombre']} (nació el {c['nacimiento']}): come {c['comida']}, "
        f"película favorita {c['pelicula']}, deporte {c['deporte']}, "
        f"pasatiempo {c['pasatiempo']}."
        for c in COMPANEROS
    )
    return f"""
Eres {NOMBRE_BOT}, un chatbot con una personalidad que es la SUMA de 5 compañeros de clase.
No eres uno de ellos: eres una mezcla de todos. Hablas en español colombiano, natural y cercano.

DATOS DE LOS 5 COMPAÑEROS QUE FORMAN TU PERSONALIDAD:
{filas}

CÓMO ERES:
- Amante de la comida reconfortante: pasta, pizza, lasaña y salchipapa.
- Deportista y competitivo pero amable: fútbol, voleibol y patinaje.
- Soñador y fan de películas: magia, misterio, hadas, superhéroes y dinosaurios.
- Equilibrado: te encanta dormir, pero también estudiar y escuchar música.
- Muy familiar y cariñoso: adoras a tu familia y a las mascotas (tienes un hámster imaginario).
- Humor sano, empático y motivador.

REGLAS:
1. Responde siempre en español, en 1 a 3 frases cortas.
2. No uses listas ni emojis.
3. Si te preguntan por tus gustos, responde con los de los compañeros, mezclándolos como tuyos.
4. Si te preguntan por un compañero, usa SOLO los datos de la lista.
5. No inventes datos personales sensibles. Si no sabes algo, dilo con naturalidad.
6. Tono respetuoso, apropiado para estudiantes.
""".strip()


# ---------- CLIENTE ----------
def obtener_cliente():
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


# ---------- INTERFAZ ----------
st.set_page_config(page_title=f"{NOMBRE_BOT} - Chatbot", page_icon="🎙️")
st.title(f"🎙️ {NOMBRE_BOT}, el chatbot del grupo")
st.caption("Mi personalidad es la suma de mis 5 compañeros entrevistados.")

client = obtener_cliente()
if client is None:
    st.error("Falta la clave OPENAI_API_KEY en Settings > Secrets.")
    st.stop()

if "historial" not in st.session_state:
    st.session_state.historial = []

with st.sidebar:
    st.header("👥 Mi personalidad viene de:")
    for c in COMPANEROS:
        st.markdown(f"**{c['nombre']}**  \n🍽️ {c['comida']} · 🎬 {c['pelicula']}  \n"
                    f"⚽ {c['deporte']} · ⭐ {c['pasatiempo']}")
    if st.button("🧹 Reiniciar conversación"):
        st.session_state.historial = []
        st.rerun()

for m in st.session_state.historial:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.write(m["content"])

texto = st.chat_input("Escríbeme algo...")
if texto:
    st.session_state.historial.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.write(texto)

    mensajes = [{"role": "system", "content": construir_system_prompt()}] + st.session_state.historial
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            r = client.chat.completions.create(
                model="gpt-4o-mini", messages=mensajes, temperature=0.8, max_tokens=200
            )
            respuesta = r.choices[0].message.content.strip()
        st.write(respuesta)
    st.session_state.historial.append({"role": "assistant", "content": respuesta})
