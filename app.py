import streamlit as st
import requests

st.set_page_config(page_title="Invernadero", layout="wide")

st.title("🌿 Sistema Inteligente de Invernadero")

url = "https://api.thingspeak.com/channels/3358332/feeds/last.json"
data = requests.get(url).json()

h1 = data["field1"]
h2 = data["field2"]
temp = data["field3"]
humA = data["field4"]

col1, col2 = st.columns(2)

col1.metric("🌡️ Temperatura", f"{temp} °C")
col1.metric("❄️🔥 Humedad Aire", f"{humA} %")

col2.metric("🌱 Nivel 1", h1)
col2.metric("🌱 Nivel 2", h2)

# Auto refresco
st.experimental_rerun()
