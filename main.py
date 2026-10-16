
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io

st.set_page_config(
    page_title="Voces del Salon",
    page_icon="🎙️",
    layout="wide"
)

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

st.title("🎙️ Voces del Salón")
st.write(
    "Un chatbot de voz creado con los gustos y "
    "la personalidad de nuestros compañeros."
)

# DATOS DE LAS ENTREVISTAS
st.sidebar.header("📋 Entrevistas")

with st.sidebar.form("entrevista"):
    nombre = st.text_input("Nombre o código del compañero")
    musica = st.text_input("Canción o género musical favorito")
    pelicula = st.text_input("Películas favoritas")
    deporte = st.text_input("Deporte favorito")
    materia = st.text_input("Materia favorita")
    comida = st.text_input("Comida favorita")
    fortalezas = st.text_input("Fortalezas")
    debilidades = st.text_input("Aspectos por mejorar")
    rasgos = st.text_input("Personalidad en tres palabras")

    guardar = st.form_submit_button("Guardar entrevista")

if "entrevistas" not in st.session_state:
    st.session_state.entrevistas = []

if guardar:
    respuestas = [
        musica, pelicula, deporte, materia, comida,
        fortalezas, debilidades, rasgos
    ]

    if all(r.strip() for r in respuestas):
        st.session_state.entrevistas.append({
            "Compañero": nombre.strip() or "Anónimo",
            "Música": musica,
            "Películas": pelicula,
            "Deportes": deporte,
            "Materias": materia,
            "Comidas": comida,
            "Fortalezas": fortalezas,
            "Por mejorar": debilidades,
            "Personalidad": rasgos
        })
        st.sidebar.success("¡Entrevista guardada!")
    else:
        st.sidebar.warning("Completa todas las preguntas.")

# CREAR LA PERSONALIDAD COLECTIVA
def obtener_datos(campo):
    datos = [
        persona[campo]
        for persona in st.session_state.entrevistas
        if persona[campo].strip()
    ]
    if not datos:
        return "Aún no hay datos. Registra entrevistas."
    return ", ".join(datos)

def responder(pregunta):
    p = pregunta.lower()

    if any(x in p for x in ["hola", "buenas", "hey"]):
        return (
            "¡Hola! Soy Voces del Salón, un chatbot amigable, "
            "creativo y respetuoso. Mi personalidad se basa "
            "en las respuestas de los compañeros."
        )

    if any(x in p for x in ["música", "musica", "canción", "canciones"]):
        return "Los gustos musicales del grupo son: " + obtener_datos("Música")

    if any(x in p for x in ["película", "peliculas", "películas", "cine"]):
        return "Las películas favoritas son: " + obtener_datos("Películas")

    if any(x in p for x in ["deporte", "fútbol", "deportes"]):
        return "Los deportes favoritos son: " + obtener_datos("Deportes")

    if any(x in p for x in ["materia", "asignatura", "clase"]):
        return "Las materias favoritas son: " + obtener_datos("Materias")

    if any(x in p for x in ["comida", "comer", "plato"]):
        return "Las comidas favoritas son: " + obtener_datos("Comidas")

    if any(x in p for x in ["fortaleza", "habilidades"]):
        return "Las fortalezas del grupo son: " + obtener_datos("Fortalezas")

    if any(x in p for x in ["debilidad", "mejorar"]):
        return (
            "Los aspectos que los compañeros quieren mejorar son: "
            + obtener_datos("Por mejorar")
            + ". Reconocerlos nos ayuda a aprender."
        )

    if any(x in p for x in ["personalidad", "quién eres", "quien eres"]):
        return (
            "Los compañeros describieron su personalidad así: "
            + obtener_datos("Personalidad")
            + ". Mi estilo es juvenil, amigable y colaborativo."
        )

    if any(x in p for x in ["compañeros", "entrevistas", "grupo"]):
        return (
            f"He registrado {len(st.session_state.entrevistas)} entrevistas. "
            "Represento los gustos recopilados, aunque no todos "
            "tenemos las mismas preferencias."
        )

    if any(x in p for x in ["chatbot", "parecido", "similitud"]):
        return (
            "Me parezco a Character.AI porque tengo una personalidad "
            "definida para conversar. La diferencia es que yo represento "
            "los gustos de un grupo escolar."
        )

    if any(x in p for x in ["gracias", "chao", "adiós", "adios"]):
        return "¡Con gusto! Gracias por conversar conmigo. ¡Hasta pronto!"

    return (
        "¡Qué interesante! Puedes preguntarme por música, películas, "
        "deportes, materias, comidas, fortalezas o personalidad."
    )

# MOSTRAR ENTREVISTAS
st.header("📊 Resultados de las entrevistas")
st.metric("Compañeros entrevistados", len(st.session_state.entrevistas))

if st.session_state.entrevistas:
    st.dataframe(
        st.session_state.entrevistas,
        use_container_width=True
    )
else:
    st.info("Registra las entrevistas desde el menú lateral.")

# CHAT POR TEXTO
st.header("💬 Habla con el chatbot")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["texto"])

pregunta = st.chat_input("Escribe tu pregunta aquí...")

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

# CHAT POR VOZ
st.divider()
st.header("🎤 Chatbot de voz")

st.write("Graba una pregunta y el chatbot responderá hablando.")

audio = st.audio_input("Graba tu pregunta")

if st.button("Reconocer voz y responder"):
    if audio is None:
        st.warning("Primero debes grabar una pregunta.")
    else:
        try:
            reconocedor = sr.Recognizer()

            with sr.AudioFile(io.BytesIO(audio.getvalue())) as fuente:
                grabacion = reconocedor.record(fuente)

            pregunta_voz = reconocedor.recognize_google(
                grabacion,
                language="es-CO"
            )

            respuesta_voz = responder(pregunta_voz)

            st.write("**Tu pregunta:**", pregunta_voz)
            st.write("**Respuesta del chatbot:**", respuesta_voz)

            voz = gTTS(text=respuesta_voz, lang="es")
            audio_respuesta = io.BytesIO()
            voz.write_to_fp(audio_respuesta)

            st.audio(
                audio_respuesta.getvalue(),
                format="audio/mpeg"
            )

        except sr.UnknownValueError:
            st.warning("No se entendió la grabación. Inténtalo otra vez.")
        except Exception as error:
            st.error(
                "No se pudo procesar el audio. Verifica tu conexión "
                "a internet y los permisos del micrófono."
            )

# COMPARACIÓN CON OTROS CHATBOTS
st.divider()
st.header("🤖 Comparación con otros chatbots")

st.subheader("Character.AI")
st.write(
    "Se parece a nuestro chatbot porque permite crear personajes "
    "con una personalidad definida. La diferencia es que Voces "
    "del Salón se construye a partir de entrevistas escolares."
)

st.subheader("Replika")
st.write(
    "Se parece porque está orientado a mantener conversaciones "
    "cercanas y personalizadas. Nuestro proyecto representa los "
    "gustos y características recopilados de un grupo."
)

st.success("¡Voces del Salón está listo para probarse!")
