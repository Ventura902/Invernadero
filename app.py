import streamlit as st
import requests
import time
from google import genai
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Invernadero", layout="wide")
st.title("🌿 Sistema Inteligente de Invernadero")

FIREBASE_URL = "https://invernadero-f2926-default-rtdb.firebaseio.com/invernadero.json"
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def convertir_humedad(valor):
    seco = 800
    humedo = 400
    try:
        valor = float(valor)
        porcentaje = (seco - valor) * 100 / (seco - humedo)
        return max(0, min(100, round(porcentaje, 1)))
    except:
        return 0


def obtener_datos():
    try:
        response = requests.get(FIREBASE_URL, timeout=1)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None


def analizar_con_ia(datos):
    time.sleep(5)

    h1p = convertir_humedad(datos.get("h1", 0))
    h2p = convertir_humedad(datos.get("h2", 0))
    temp = datos.get("temp", 0)
    humA = datos.get("humA", 0)

    prompt = f"""
    Eres un asistente experto en invernaderos automatizados.

    Datos actuales:
    - Temperatura: {temp} °C
    - Humedad aire: {humA} %
    - Humedad suelo tomates: {h1p} %
    - Humedad suelo lechuga: {h2p} %

    Genera recomendaciones claras y concisas.
    """

    respuesta = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return respuesta.text


if "analisis_ia" not in st.session_state:
    st.session_state.analisis_ia = ""

if not st.session_state.get("analizando", False):
    st_autorefresh(interval=1000, key="refresh_datos")


datos = obtener_datos()

if datos:
    h1 = datos.get("h1", 0)
    h2 = datos.get("h2", 0)
    temp = datos.get("temp", 0)
    humA = datos.get("humA", 0)

    h1p = convertir_humedad(h1)
    h2p = convertir_humedad(h2)

    st.subheader("📡 Datos en tiempo real")

    col1, col2 = st.columns(2)

    col1.metric("🌡️ Temperatura", f"{temp} °C")
    col1.metric("💨 Humedad aire", f"{humA} %")

    col2.metric("🍅 Humedad Tomates", f"{h1p} %")
    col2.metric("🥬 Humedad Lechuga", f"{h2p} %")

    st.subheader("⚙️ Estado de procesos automáticos")

    # Lógica simple (como la tenías antes)
    bomba_encendida = h1p < 40 or h2p < 40
    humidificador_encendido = humA <= 30

    col3, col4 = st.columns(2)

    with col3:
        if bomba_encendida:
            st.success("🚰 BOMBA ENCENDIDA")
        else:
            st.info("🚰 Bomba apagada")

    with col4:
        if humidificador_encendido:
            st.success("💨 HUMIDIFICADOR ENCENDIDO")
        else:
            st.info("💨 Humidificador apagado")

    st.subheader("🌱 Estado del suelo")

    if h1p < 30:
        st.error("Tomates secos")
    elif h1p < 60:
        st.warning("Tomates medios")
    else:
        st.success("Tomates húmedos")

    if h2p < 30:
        st.error("Lechuga seca")
    elif h2p < 60:
        st.warning("Lechuga media")
    else:
        st.success("Lechuga húmeda")

    st.divider()
    st.subheader("🤖 IA")

    if st.button("Analizar"):
        with st.spinner("Analizando..."):
            st.session_state.analisis_ia = analizar_con_ia(datos)

    if st.session_state.analisis_ia:
        st.markdown(st.session_state.analisis_ia)

else:
    st.warning("⏳ Esperando datos...")
