import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Base de Datos · Churn Hunters",
    layout="wide"
)

# ── INYECCIÓN DE ESTILO COMPLETO (FORZANDO MENÚ LATERAL OSCURO) ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght=400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Fondo principal */
[data-testid="stHeader"], .stAppHeader, [data-testid="stAppViewContainer"] { 
    background-color: #0d0f14 !important; 
}
.stApp { background: #0d0f14; color: #e8eaf0; }

/* 🌟 CORRECCIÓN CRÍTICA: Forzar Menú Lateral Negro y Texto Claro 🌟 */
[data-testid="stSidebar"], 
[data-testid="stSidebarNav"], 
.stSidebar, 
div[data-testid="stSidebarUserContent"] {
    background-color: #0d0f14 !important;
    background: #0d0f14 !important;
    border-right: 1px solid #1f2433 !important;
}

/* Forzar color de los textos de navegación del menú */
[data-testid="stSidebarNav"] span, 
[data-testid="stSidebarNav"] a,
.stSidebar nav li div {
    color: #e8eaf0 !important;
    font-weight: 500 !important;
}

/* Efecto hover en el menú */
[data-testid="stSidebarNav"] a:hover {
    background-color: #161a24 !important;
}

.brand-line { height: 3px; background: linear-gradient(90deg, #ff2a6d, #d6006e, transparent); margin: 8px 0 24px 0; }
.custom-success-box { background-color: #1a1216; border-left: 5px solid #ff2a6d; border-radius: 6px; padding: 15px; margin-bottom: 20px; color: #f178b6; font-weight: 500; }
div[data-testid="stMetric"] { background: #161a24 !important; border: 1px solid #252b3b !important; border-radius: 10px !important; padding: 15px 20px !important; }
div[data-testid="stMetricValue"] > div { color: #ff2a6d !important; font-size: 2.2rem !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1> Base de Datos: Arca Continental</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#7a8099; margin:-10px 0 10px 0;'>Módulo de conexión y extracción de datos (Ing. Ivana)</p>", unsafe_allow_html=True)
st.markdown("<div class='brand-line'></div>", unsafe_allow_html=True)

st.markdown("## Vista Interactiva de Ventas Crudas")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_backup = os.path.join(base_dir, "data", "sales_churn_train.csv")

if os.path.exists(path_backup):
    df_live = pd.read_csv(path_backup).head(500)
    
    st.markdown("""
    <div class='custom-success-box'>
        📊 Mostrando registros del Canal Tradicional indexados correctamente para análisis.
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    with m1:
        st.metric(label="Muestra Visual Interactiva", value=f"{len(df_live)} filas")
    with m2:
        st.metric(label="Columnas de Control", value=str(len(df_live.columns)))
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df_live, use_container_width=True, height=450)
else:
    st.error("⚠️ No se encontró el archivo 'sales_churn_train.csv' en la carpeta 'data/'. Por favor verifica su ubicación.")