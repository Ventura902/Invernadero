import streamlit as st
import requests
import time

st.set_page_config(page_title="Invernadero", layout="wide")
st.title("🌿 Sistema Inteligente de Invernadero")

def convertir_humedad(valor):
    seco = 800
    humedo = 300
    try:
        valor = int(float(valor))
        porcentaje = (seco - valor) * 100 / (seco - humedo)
        porcentaje = max(0, min(100, porcentaje))
        return round(porcentaje, 1)
    except:
        return 0

url = f"https://api.thingspeak.com/channels/3358332/feeds/last.json?nocache={time.time()}"

try:
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        data = response.json()

        if data and data.get("field1"):
            h1 = data["field1"]
            h2 = data["field2"]
            temp = float(data["field3"])
            humA = float(data["field4"])

            h1p = convertir_humedad(h1)
            h2p = convertir_humedad(h2)

            col1, col2 = st.columns(2)

            col1.metric("🌡️ Temperatura", f"{temp} °C")
            col1.metric("❄️🔥 Humedad Aire", f"{humA} %")

            col2.metric("🌱 Primer Nivel", f"{h1p} %")
            col2.metric("🌱 Segundo Nivel", f"{h2p} %")

            st.subheader("❄️🔥 Estado del ambiente")

            if humA < 40:
                st.error("❌ Aire seco (baja humedad)")
            elif humA <= 70:
                st.success("✅ Humedad ideal")
            else:
                st.warning("⚠️ Aire muy húmedo")

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

        else:
            st.warning("⏳ Esperando datos del invernadero...")
    else:
        st.error("❌ Error al obtener datos de ThingSpeak")

except:
    st.error("❌ No se pudo conectar con ThingSpeak")

st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)
