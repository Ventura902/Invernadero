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
    seco = 900
    humedo = 500

    try:
        valor = float(valor)
        porcentaje = (seco - valor) * 100 / (seco - humedo)
        return max(0, min(100, round(porcentaje, 1)))
    except:
        return 0


def obtener_datos():
    try:
        response = requests.get(FIREBASE_URL, timeout=2)

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

El invernadero tiene dos pisos:
- Piso 1: Tomates
- Piso 2: Lechuga

Datos actuales:
- Temperatura: {temp} °C
- Humedad del aire: {humA} %
- Humedad del suelo piso 1 tomates: {h1p} %
- Humedad del suelo piso 2 lechuga: {h2p} %

Rangos de referencia:
- Tomate: temperatura ideal aproximada entre 17 °C y 25 °C.
- Lechuga: temperatura ideal aproximada entre 15 °C y 22 °C.
- Humedad de suelo recomendada: entre 40 % y 70 %.
- Humedad de aire recomendada: entre 50 % y 80 %.

Genera un informe claro con este formato:

🌡️ Temperatura
- Estado:
- Riesgo:
- Recomendación:

💨 Humedad del aire
- Estado:
- Riesgo:
- Recomendación:

🍅 Suelo piso 1 tomates
- Estado:
- Riesgo:
- Recomendación:

🥬 Suelo piso 2 lechuga
- Estado:
- Riesgo:
- Recomendación:

📋 Conclusión general
- Panorama:
- Acción recomendada:
"""

    respuesta = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return respuesta.text


if "analisis_ia" not in st.session_state:
    st.session_state.analisis_ia = ""

if "datos_analizados" not in st.session_state:
    st.session_state.datos_analizados = None

if "analizando" not in st.session_state:
    st.session_state.analizando = False

if "ultima_firma_ia" not in st.session_state:
    st.session_state.ultima_firma_ia = None

if "estado_bomba" not in st.session_state:
    st.session_state.estado_bomba = False

if "estado_humi" not in st.session_state:
    st.session_state.estado_humi = False


if not st.session_state.analizando:
    st_autorefresh(interval=1000, key="refresh_datos")


datos = obtener_datos()

if datos:

    h1 = datos.get("h1", 0)
    h2 = datos.get("h2", 0)
    temp = datos.get("temp", 0)
    humA = datos.get("humA", 0)
    timestamp = datos.get("timestamp", 0)

    h1p = convertir_humedad(h1)
    h2p = convertir_humedad(h2)

    # Estado calculado de la bomba según la misma lógica del Arduino
    if h1 < 15 and h2 < 15:
        st.session_state.estado_bomba = True
    elif h1 > 85 and h2 > 85:
        st.session_state.estado_bomba = False

    # Estado calculado del humidificador o ventilador según la misma lógica del Arduino
    if temp > 30:
        st.session_state.estado_humi = True
    elif temp < 28:
        st.session_state.estado_humi = False

    st.subheader("📡 Datos en tiempo real")

    col1, col2 = st.columns(2)

    col1.metric("🌡️ Temperatura", f"{temp} °C")
    col1.metric("💨 Humedad del aire", f"{humA} %")

    col2.metric("🍅 Humedad suelo - Piso 1 Tomates", f"{h1p} %")
    col2.metric("🥬 Humedad suelo - Piso 2 Lechuga", f"{h2p} %")

    st.subheader("⚙️ Estado de procesos automáticos")

    col3, col4 = st.columns(2)

    with col3:
        if st.session_state.estado_bomba:
            st.success("🚰 BOMBA ENCENDIDA - Riego activo")
        else:
            st.info("🚰 BOMBA APAGADA")

    with col4:
        if st.session_state.estado_humi:
            st.success("❄️ HUMIDIFICADOR / VENTILADOR ENCENDIDO")
        else:
            st.info("❄️ HUMIDIFICADOR / VENTILADOR APAGADO")

    st.subheader("💨 Estado de humedad del aire")

    if humA <= 30:
        st.error("🚨 Aire seco: humedad ambiental baja")
    elif humA <= 80:
        st.success("✅ Humedad ambiental adecuada")
    else:
        st.warning("💧 Aire muy húmedo")

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

    st.divider()

    st.subheader("🤖 IA del invernadero")

    if st.button("Analizar invernadero con IA"):
        st.session_state.datos_analizados = datos.copy()
        st.session_state.analizando = True
        st.rerun()

    if st.session_state.analizando:

        datos_ia = st.session_state.datos_analizados

        h1p_ia = convertir_humedad(datos_ia.get("h1", 0))
        h2p_ia = convertir_humedad(datos_ia.get("h2", 0))
        temp_ia = round(float(datos_ia.get("temp", 0)), 1)
        humA_ia = round(float(datos_ia.get("humA", 0)), 1)

        firma_actual = {
            "temp": temp_ia,
            "humA": humA_ia,
            "h1p": round(h1p_ia, 0),
            "h2p": round(h2p_ia, 0),
        }

        if st.session_state.ultima_firma_ia == firma_actual:
            st.info("📌 Los datos no cambiaron mucho. Se reutiliza el análisis anterior.")
        else:
            with st.spinner("🤖 Analizando el invernadero durante 5 segundos..."):
                try:
                    st.session_state.analisis_ia = analizar_con_ia(datos_ia)
                    st.session_state.ultima_firma_ia = firma_actual
                except Exception as e:
                    st.session_state.analisis_ia = f"⚠️ Error al analizar con IA: {e}"

        st.session_state.analizando = False
        st.rerun()

    if st.session_state.datos_analizados:
        st.caption("📌 Datos usados por la IA:")
        st.json(st.session_state.datos_analizados)

    if st.session_state.analisis_ia:
        st.markdown(st.session_state.analisis_ia)

else:
    st.warning("⏳ Esperando datos desde Firebase...")
