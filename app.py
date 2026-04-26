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

placeholder = st.empty()

while True:
    try:
        url = "https://api.thingspeak.com/channels/3358332/feeds/last.json"
        data = requests.get(url).json()

        if data and data.get("field1"):

            h1 = data["field1"]
            h2 = data["field2"]
            temp = float(data["field3"])
            humA = float(data["field4"])

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

    except:
        st.warning("⏳ Esperando datos...")

    time.sleep(15)
