import streamlit as st
import requests
import time

st.set_page_config(page_title="Invernadero", layout="wide")
st.title("🌿 Sistema Inteligente de Invernadero")

FIREBASE_URL = "https://invernadero-f2926-default-rtdb.firebaseio.com/invernadero.json"

def convertir_humedad(valor):
    seco = 830
    humedo = 415
    try:
        porcentaje = (seco - valor) * 100 / (seco - humedo)
        return max(0, min(100, round(porcentaje, 1)))
    except:
        return 0

placeholder = st.empty()

while True:
    try:
        data = requests.get(FIREBASE_URL).json()

        if data:
            h1 = data["h1"]
            h2 = data["h2"]
            temp = data["temp"]
            humA = data["humA"]

            h1p = convertir_humedad(h1)
            h2p = convertir_humedad(h2)

            with placeholder.container():

                col1, col2 = st.columns(2)

                col1.metric("🌡️ Temperatura", f"{temp} °C")
                col1.metric("❄️🔥 Humedad Aire", f"{humA} %")

                col2.metric("🌱 Primer Nivel", f"{h1p} %")
                col2.metric("🌱 Segundo Nivel", f"{h2p} %")

                st.subheader("❄️🔥 Estado del ambiente")

                if humA < 40:
                    st.error("❌ Aire seco")
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

    except:
        st.warning("⏳ Esperando datos...")

    time.sleep(1)  # 🔥 actualización cada 1 segundo
