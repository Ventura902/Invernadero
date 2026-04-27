import streamlit as st
import requests
import time
from google import genai
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Invernadero", layout="wide")
st.title("🌿 Sistema Inteligente de Invernadero")

# Actualiza los datos cada 2 segundos sin usar while True
st_autorefresh(interval=2000, key="refresh_datos")

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


def obtener_datos():
    try:
        response = requests.get(FIREBASE_URL, timeout=3)
        return response.json()
    except:
        return None


def analizar_con_ia(datos):
    # Simula análisis profundo mínimo de 5 segundos
    time.sleep(5)

    h1_raw = datos.get("h1", 0)
    h2_raw = datos.get("h2", 0)
    temp = datos.get("temp", 0)
    humA = datos.get("humA", 0)

    h1p = convertir_humedad(h1_raw)
    h2p = convertir_humedad(h2_raw)

    prompt = f"""
    Eres un asistente experto en invernaderos automatizados.

    El invernadero tiene dos pisos:
    - Piso 1: Tomates
    - Piso 2: Lechuga

    Datos actuales:
    - Temperatura ambiente: {temp} °C
    - Humedad ambiente: {humA} %
    - Humedad del suelo piso 1 tomates: {h1p} %
    - Humedad del suelo piso 2 lechuga: {h2p} %

    Rangos de referencia usados:
    - Tomate: temperatura ideal aproximada entre 17 °C y 25 °C.
    - Lechuga: temperatura ideal aproximada entre 15 °C y 22 °C.
    - Humedad de suelo recomendada: entre 40 % y 70 %.

    Genera un informe en español, claro y profesional, con este formato:

    🍅 Piso 1 - Tomates
    - Estado de temperatura:
    - Estado de humedad del suelo:
    - Riesgo:
    - Recomendación:

    🥬 Piso 2 - Lechuga
    - Estado de temperatura:
    - Estado de humedad del suelo:
    - Riesgo:
    - Recomendación:

    📋 Conclusión general
    - Panorama general:
    - Acción recomendada:
    """

    respuesta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return respuesta.text


if "analisis_ia" not in st.session_state:
    st.session_state.analisis_ia = ""

if "datos_analizados" not in st.session_state:
    st.session_state.datos_analizados = None


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
    col1.metric("❄️🔥 Humedad Aire", f"{humA} %")

    col2.metric("🍅 Piso 1 - Tomates", f"{h1p} %")
    col2.metric("🥬 Piso 2 - Lechuga", f"{h2p} %")

    st.subheader("❄️🔥 Estado del ambiente")

    if humA < 40:
        st.warning("💧 Humedad ambiental baja")
    elif humA <= 70:
        st.success("✅ Humedad ambiental adecuada")
    else:
        st.warning("⚠️ Humedad ambiental alta / posible falta de ventilación")

    st.subheader("🌱 Estado del suelo por cultivo")

    if h1p < 30:
        st.error("🚨 Tomates: suelo seco, se recomienda riego")
    elif h1p < 60:
        st.warning("🌤️ Tomates: humedad media, vigilar")
    else:
        st.success("💧 Tomates: suelo húmedo")

    if h2p < 30:
        st.error("🚨 Lechuga: suelo seco, se recomienda riego")
    elif h2p < 60:
        st.warning("🌤️ Lechuga: humedad media, vigilar")
    else:
        st.success("💧 Lechuga: suelo húmedo")

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
        datos_snapshot = datos.copy()
        st.session_state.datos_analizados = datos_snapshot

        try:
            with st.spinner("🤖 Analizando el panorama del invernadero durante 5 segundos..."):
                st.session_state.analisis_ia = analizar_con_ia(datos_snapshot)
        except Exception as e:
            st.session_state.analisis_ia = f"⚠️ Error al analizar con IA: {e}"

    if st.session_state.datos_analizados:
        st.caption("📌 Datos usados por la IA en el momento del análisis:")
        st.json(st.session_state.datos_analizados)

    if st.session_state.analisis_ia:
        st.markdown(st.session_state.analisis_ia)

else:
    st.warning("⏳ Esperando datos desde Firebase...")
