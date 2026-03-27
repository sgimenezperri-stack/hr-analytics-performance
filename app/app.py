import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR Analytics - Performance", layout="wide")

st.title("📊 Dashboard de Performance Comercial")

# Simulación de datos (después lo conectamos a Google Sheets)
data = pd.DataFrame({
    "Vendedor": ["Juan", "Ana", "Luis", "Sofía"],
    "Ventas": [120000, 95000, 143000, 110000],
    "Objetivo": [100000, 100000, 120000, 100000]
})

data["Cumplimiento (%)"] = (data["Ventas"] / data["Objetivo"]) * 100

st.subheader("📈 KPIs")

col1, col2 = st.columns(2)

col1.metric("Venta Total", f"${data['Ventas'].sum():,.0f}")
col2.metric("Cumplimiento Promedio", f"{data['Cumplimiento (%)'].mean():.1f}%")

st.subheader("📋 Detalle por vendedor")
st.dataframe(data)

st.subheader("🏆 Ranking")
st.bar_chart(data.set_index("Vendedor")["Ventas"])
