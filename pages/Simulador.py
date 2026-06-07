import streamlit as st
import pandas as pd
import os
import json
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Simulador IA · Churn Hunters", layout="wide")

# Estilo Cyberpunk forzado (con textos de barras y filtros maximizados)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght=400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stHeader"], .stAppHeader, [data-testid="stAppViewContainer"], .stApp { background-color: #0d0f14 !important; color: #e8eaf0; }
[data-testid="stSidebar"], [data-testid="stSidebarNav"], .stSidebar { background-color: #0d0f14 !important; border-right: 1px solid #1f2433 !important; }
[data-testid="stSidebarNav"] span { color: #e8eaf0 !important; font-weight: 500 !important; }
.brand-line { height: 3px; background: linear-gradient(90deg, #ff2a6d, #d6006e, transparent); margin: 8px 0 24px 0; }
.cyber-card { background: #141722; border: 1px solid #202636; border-radius: 12px; padding: 30px; text-align: center; }
.result-value { font-size: 4rem; font-weight: 800; line-height: 1; margin: 10px 0; }
.pink-text { color: #ff2a6d; }
.green-text { color: #00ffaa; }
.yellow-text { color: #ffaa00; }

/* =========================================================================
   🌟 MODIFICACIÓN PREMIUM: AGRANDAR Y ILUMINAR ETIQUETAS DE LOS SLIDERS Y CONTROLES 🌟
   ========================================================================= */

/* Aplica a los títulos de los Sliders (Barras a mover) */
div[data-testid="stSlider"] label p {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

/* Aplica al título del Radio button (Infraestructura de Frío) */
div[data-testid="stRadio"] > label p {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

/* Aplica a las opciones internas del Radio button ("Sin Cooler", "Con Cooler...") */
div[data-testid="stRadio"] div[role="radiogroup"] label p {
    font-size: 1.15rem !important;
    font-weight: 500 !important;
    color: #e8eaf0 !important;
}

/* Aplica al título del Number Input (Antigüedad del Cliente) */
div[data-testid="stNumberInput"] label p {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1> Simulador Prescriptivo de Riesgo</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#7a8099;'>Laboratorio de escenarios: Predice el impacto de tus decisiones comerciales antes de ejecutarlas.</p>", unsafe_allow_html=True)
st.markdown("<div class='brand-line'></div>", unsafe_allow_html=True)

# Carga de datos para entrenamiento flash del simulador
@st.cache_resource
def entrenar_modelo_simulador():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "clientes_scoring_precalculado.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        features = ['meses_activo', 'total_transacciones', 'avg_transacciones', 'avg_boxes', 'total_boxes', 'trend_ratio', 'tiene_cooler', 'avg_coolers', 'territorio_encoded']
        X = df[features].fillna(0)
        y = df['churned'].fillna(0).astype(int)
        model = RandomForestClassifier(n_estimators=50, max_depth=6, class_weight="balanced", random_state=42)
        model.fit(X, y)
        return model, features
    return None, None

model, feat_cols = entrenar_modelo_simulador()

if model:
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### 🛠️ Ajuste de Variables")
        s_boxes = st.slider("Volumen de Venta (Cajas/Mes)", 1, 500, 45)
        s_trans = st.slider("Frecuencia (Transacciones/Mes)", 1, 30, 8)
        s_trend = st.slider("Tendencia de Compra (Ratio)", 0.1, 2.0, 0.7, help="1.0 es estable, < 1.0 es caída.")
        s_cooler = st.radio("Infraestructura de Frío", ["Sin Cooler", "Con Cooler Comodato"], horizontal=True)
        s_antig = st.number_input("Antigüedad del Cliente (Meses)", 1, 120, 12)
        
    with col2:
        st.markdown("### 🎯 Predicción de la IA")
        input_data = pd.DataFrame([{
            'meses_activo': s_antig, 'total_transacciones': s_trans * 4, 'avg_transacciones': s_trans,
            'avg_boxes': s_boxes / 4, 'total_boxes': s_boxes, 'trend_ratio': s_trend,
            'tiene_cooler': 1 if "Con" in s_cooler else 0, 'avg_coolers': 1 if "Con" in s_cooler else 0,
            'territorio_encoded': 0
        }])
        
        prob = model.predict_proba(input_data[feat_cols])[0][1] * 100
        
        color_class = "pink-text" if prob > 70 else "yellow-text" if prob > 35 else "green-text"
        label = "RIESGO CRÍTICO" if prob > 70 else "RIESGO MEDIO" if prob > 35 else "SALUDABLE"
        
        st.markdown(f"""
        <div class="cyber-card">
            <div style="color: #7a8099; text-transform: uppercase; letter-spacing: 2px;">Probabilidad de Abandono</div>
            <div class="result-value {color_class}">{prob:.1f}%</div>
            <div style="font-size: 1.5rem; font-weight: 700;" class="{color_class}">{label}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💡 Recomendación Estratégica")
        if prob > 70:
            st.error("🚨 **ACCION INMEDIATA:** El modelo detecta una alta sensibilidad al volumen. Se recomienda instalar un Cooler y asignar un descuento por leeltad para evitar la fuga en los próximos 30 días.")
        else:
            st.success("✅ **ESTRATEGIA:** El cliente muestra estabilidad. Es momento de introducir nuevos productos (Cross-selling) para aumentar el ticket promedio.")

else:
    st.warning("Primero ejecuta el script de IA para activar el simulador.")