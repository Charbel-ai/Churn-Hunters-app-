import streamlit as st

#Configuracion de las pestaña
st.set_page_config(
    page_title="Churn Hunters",
    layout="wide"
)

#Diseño de la pagina principal
st.title("Plataforma Churn Hunters")
st.subheader("Sistema de Inteligenia de Retencion y Analisis de Clientes")
st.write("---")

st.markdown("""
### 👋 ¡Bienvenido al Centro de Control!
Esta aplicación web multipágina analiza y previene el abandono de clientes en tiempo real.

#### 🧭 Cómo navegar por la app:
Utiliza el **menú automático de arriba a la izquierda** para explorar las herramientas del equipo:
* **Bases datos(ivana):** Conexión en vivo con MongoDB Atlas.
* **Dashboard(sofi):** Gráficos interactivos de analítica.
* **Estrategia(charbel):** Nuestro simulador de riesgo individual.
""")

st.sidebar.success("Aplicacion Principal Activa ")
