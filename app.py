import streamlit as st
import requests
from google import genai
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Invernadero", layout="wide")
st.title("🌿 Sistema Inteligente de Invernadero")

# refresca cada 1 segundo sin romper tanto la interfaz
st_autorefresh(interval=1000, key="refresh_datos")

FIREBASE_URL = "https://invernadero-f2926-default-rtdb.firebaseio.com/invernadero.json"

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def convertir_humedad(valor):
    seco = 830
    humedo = 415
    try:
        porcentaje = (seco - valor) * 100 / (seco - humedo)
        return max(0, min(100, round(porcentaje, 1)))
    except:
        return 0


def analizar_con_ia(datos):
    prompt = f"""
    Eres un asistente experto en invernaderos automatizados.

    Datos actuales:
    - Humedad suelo 1: {datos.get("h1")}%
    - Humedad suelo 2: {datos.get("h2")}%
    - Temperatura: {datos.get("temp")} °C
    - Humedad ambiente: {datos.get("humA")}%

    Responde en español, corto y claro:
    - Estado general
    - Problema detectado
    - Recomendación
    """

    respuesta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return respuesta.text


def obtener_datos():
    try:
        response = requests.get(FIREBASE_URL, timeout=3)
        return response.json()
    except:
        return None


if "analisis_ia" not in st.session_state:
    st.session_state.analisis_ia = ""

datos = obtener_datos()

if datos:
    h1 = datos.get("h1", 0)
    h2 = datos.get("h2", 0)
    temp = datos.get("temp", 0)
    humA = datos.get("humA", 0)

    h1p = convertir_humedad(h1)
    h2p = convertir_humedad(h2)

    col1, col2 = st.columns(2)

    col1.metric("🌡️ Temperatura", f"{temp} °C")
    col1.metric("❄️🔥 Humedad Aire", f"{humA} %")

    col2.metric("🌱 Primer Nivel", f"{h1p} %")
    col2.metric("🌱 Segundo Nivel", f"{h2p} %")

    st.subheader("❄️🔥 Estado del ambiente")

    if humA < 40:
        st.success("💧 Aire húmedo")
    elif humA <= 70:
        st.success("✅ Aire ideal")
    else:
        st.warning("⚠️ Falta de ventilación")

    st.subheader("🌱 Estado del suelo")

    if h1p < 30:
        st.error("⚠️ Primer Nivel seco")
    elif h1p < 60:
        st.warning("🌤️ Primer Nivel medio")
    else:
        st.success("💧 Primer Nivel húmedo")

    if h2p < 30:
        st.error("⚠️ Segundo Nivel seco")
    elif h2p < 60:
        st.warning("🌤️ Segundo Nivel medio")
    else:
        st.success("💧 Segundo Nivel húmedo")

    st.markdown(
        f"<h1 style='text-align: center; font-size: 70px;'>🌡️ {temp} °C</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<h1 style='text-align: center; font-size: 70px;'>❄️🔥 {humA} %</h1>",
        unsafe_allow_html=True
    )

    st.divider()
    st.subheader("🤖 IA del invernadero")

    if st.button("Analizar invernadero con IA"):
        st.session_state.analisis_ia = analizar_con_ia(datos)

    if st.session_state.analisis_ia:
        st.write(st.session_state.analisis_ia)

else:
    st.warning("⏳ Esperando datos desde Firebase...")
