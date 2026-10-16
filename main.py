
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io

st.set_page_config(
    page_title="Chatbot del Salón",
    page_icon="🎙️",
    layout="wide"
)

# Diseño
st.markdown("""
<style>
.stApp {
    background-color: #f4f0ff;
}
h1, h2, h3 {
    color: #6539a6;
}
.stButton button {
    background-color: #7546b8;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎙️ Chatbot del Salón")
st.write(
    "Un chatbot con la personalidad creada a partir "
    "de los gustos y características de nuestros compañeros."
)

# PREGUNTAS DE LA ENTREVISTA
st.sidebar.header("📋 Entrevista a los compañeros")

with st.sidebar.form("entrevista"):
    nombre = st.text_input("Nombre o código del compañero")
    cancion = st.text_input("¿Cuál es tu canción favorita?")
    pelicula = st.text_input("¿Qué películas te gustan?")
    deporte = st.text_input("¿Cuál es tu deporte favorito?")
    materia = st.text_input("¿Cuál es tu materia favorita?")
    comida = st.text_input("¿Cuál es tu comida favorita?")
    fortalezas = st.text_input("¿Cuáles son tus fortalezas?")
    debilidades = st.text_input("¿Qué aspectos quieres mejorar?")
    personalidad = st.text_input(
        "Descríbete en tres palabras"
    )

    guardar = st.form_submit_button("Guardar entrevista")

if "entrevistas" not in st.session_state:
    st.session_state.entrevistas = []

if guardar:
    if all([
        cancion.strip(), pelicula.strip(), deporte.strip(),
        materia.strip(), comida.strip(), fortalezas.strip(),
        debilidades.strip(), personalidad.strip()
    ]):
        st.session_state.entrevistas.append({
            "nombre": nombre.strip() or
                      f"Compañero {len(st.session_state.entrevistas)+1}",
            "cancion": cancion,
            "pelicula": pelicula,
            "deporte": deporte,
            "materia": materia,
            "comida": comida,
            "fortalezas": fortalezas,
            "debilidades": debilidades,
            "personalidad": personalidad
        })
        st.success("¡Entrevista guardada!")
    else:
        st.warning("Completa todas las preguntas antes de guardar.")

# CONSTRUIR PERSONALIDAD COLECTIVA
def gustos(campo):
    respuestas = [
        persona[campo].strip()
        for persona in st.session_state.entrevistas
        if persona[campo].strip()
    ]
    if not respuestas:
        return "Todavía no hay respuestas registradas"
    return "; ".join(respuestas)

musica = gustos("cancion")
peliculas = gustos("pelicula")
deportes = gustos("deporte")
materias = gustos("materia")
comidas = gustos("comida")
fortalezas_grupo = gustos("fortalezas")
mejoras = gustos("debilidades")
rasgos = gustos("personalidad")

# RESPUESTAS DEL CHATBOT
def responder(pregunta):
    p = pregunta.lower()

    if any(x in p for x in ["hola", "buenas", "hey"]):
        return (
            "¡Holaaa! Soy el Chatbot del Salón. "
            "Tengo una personalidad construida con las "
            "respuestas de nuestros compañeros. ¿De qué hablamos?"
        )

    if any(x in p for x in ["canción", "canciones", "música", "cantante"]):
        return f"Los gustos musicales registrados son: {musica}."

    if any(x in p for x in ["película", "películas", "cine"]):
        return f"Estas son las películas favoritas registradas: {peliculas}."

    if any(x in p for x in ["deporte", "deportes", "fútbol", "jugar"]):
        return f"En las entrevistas aparecen estos deportes: {deportes}."

    if any(x in p for x in ["materia", "asignatura", "clase favorita"]):
        return f"Las materias mencionadas por el grupo son: {materias}."

    if any(x in p for x in ["comida", "comer", "plato favorito"]):
        return f"Entre las comidas favoritas están: {comidas}."

    if any(x in p for x in ["fortaleza", "fortalezas", "habilidad"]):
        return f"Estas son algunas fortalezas mencionadas: {fortalezas_grupo}."

    if any(x in p for x in ["debilidad", "debilidades", "mejorar"]):
        return (
            f"Los aspectos que los compañeros quieren mejorar son: {mejoras}. "
            "Todos podemos aprender y desarrollar nuevas habilidades."
        )

    if any(x in p for x in ["personalidad", "cómo eres", "quién eres"]):
        return (
            f"Los compañeros se describieron así: {rasgos}. "
            "Mi estilo es juvenil, amigable, respetuoso y creativo."
        )

    if any(x in p for x in ["compañeros", "entrevistas", "grupo"]):
        return (
            f"He registrado {len(st.session_state.entrevistas)} entrevistas. "
            "Represento las respuestas recopiladas, aunque no todos "
            "los compañeros tienen los mismos gustos."
        )

    if any(x in p for x in ["chatbot", "parecido", "similitud"]):
        return (
            "Me parezco a Character.AI porque tengo una personalidad "
            "definida para conversar. La diferencia es que represento "
            "los gustos recopilados de un grupo escolar."
        )

    return (
        "¡Qué interesante! Puedes preguntarme sobre música, películas, "
        "deportes, materias, comidas, fortalezas o personalidad."
    )

# MOSTRAR INFORMACIÓN
st.header("📊 Resultados de las entrevistas")
st.metric("Entrevistas registradas", len(st.session_state.entrevistas))

if st.session_state.entrevistas:
    st.dataframe(
        st.session_state.entrevistas,
        use_container_width=True
    )
else:
    st.info("Registra entrevistas desde el menú lateral para construir la personalidad.")

st.header("💬 Conversa con nuestro chatbot")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["texto"])

pregunta = st.chat_input("Escribe tu pregunta...")

if pregunta:
    respuesta = responder(pregunta)
    st.session_state.mensajes.append({
        "rol": "user",
        "texto": pregunta
    })
    st.session_state.mensajes.append({
        "rol": "assistant",
        "texto": respuesta
    })
    st.rerun()

st.divider()
st.subheader("🎤 Chatbot de voz")

audio = st.audio_input("Graba una pregunta con tu voz")

if st.button("Reconocer y responder") and audio is not None:
    try:
        reconocedor = sr.Recognizer()

        with sr.AudioFile(io.BytesIO(audio.getvalue())) as fuente:
            datos_audio = reconocedor.record(fuente)

        pregunta_voz = reconocedor.recognize_google(
            datos_audio,
            language="es-CO"
        )
        respuesta_voz = responder(pregunta_voz)

        st.write("**Pregunta reconocida:**", pregunta_voz)
        st.write("**Respuesta:**", respuesta_voz)

        voz = gTTS(text=respuesta_voz, lang="es")
        archivo = io.BytesIO()
        voz.write_to_fp(archivo)

        st.audio(archivo.getvalue(), format="audio/mpeg")

    except sr.UnknownValueError:
        st.warning("No se entendió el audio. Intenta grabarlo nuevamente.")
    except Exception:
        st.error(
            "No se pudo procesar la voz. Revisa tu conexión "
            "a internet y los permisos del micrófono."
        )

# COMPARACIÓN CON OTROS CHATBOTS
st.divider()
st.header("🤖 Comparación con otros chatbots")

st.subheader("Character.AI")
st.write(
    "Se parece a nuestro proyecto porque permite crear personajes "
    "con una personalidad definida y conversar con ellos. Nuestro "
    "chatbot se diferencia porque su personalidad se construye con "
    "las respuestas de los compañeros entrevistados."
)

st.subheader("Replika")
st.write(
    "Se parece porque busca mantener conversaciones cercanas y "
    "personalizadas. Nuestro proyecto tiene un propósito escolar "
    "y representa los gustos compartidos del grupo."
)

st.success(
    "Proyecto terminado: recopila entrevistas, construye una "
    "personalidad colectiva y permite conversar por texto y voz."
)
