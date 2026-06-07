import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
 
# ── 1. CONFIGURACIÓN DE PÁGINA ──
st.set_page_config(
    page_title="Churn Hunters · Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
ROSA_FUERTE = "#ff2a6d"
ROSA_MEDIO  = "#05d9e8"
ROSA_PASTEL = "#f178b6"
MAGENTA     = "#d6006e"
NEGRO_BG    = "#0d0f14"
CARD_BG     = "#161a24"
BORDE       = "#252b3b"
ESCALA_ROSAS = [[0.0, "#3a1225"], [0.5, "#d6006e"], [1.0, "#ff2a6d"]]
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
 
[data-testid="stHeader"], .stAppHeader, [data-testid="stAppViewContainer"] {
    background-color: #0d0f14 !important;
    background: #0d0f14 !important;
}
.stApp { background: #0d0f14; color: #e8eaf0; }
[data-testid="stSidebar"] { background: #13161e !important; border-right: 1px solid #1f2433; }
[data-testid="stSidebar"] * { color: #c4c9d8 !important; }
 
span[data-baseweb="tag"] {
    background-color: #d6006e !important;
    border-radius: 6px !important;
    padding-left: 8px !important;
}
span[data-baseweb="tag"] span { color: #ffffff !important; }
[data-baseweb="select"] > div:hover { border-color: #ff2a6d !important; }
[data-baseweb="select"] > div {
    border-color: #252b3b !important;
    background-color: #161a24 !important;
}
 
[data-testid="metric-container"] {
    background: #161a24; border: 1px solid #252b3b;
    border-radius: 12px; padding: 16px 20px;
}
[data-testid="metric-container"]:hover { border-color: #ff2a6d; }
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important; letter-spacing: 0.08em;
    text-transform: uppercase; color: #7a8099 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.9rem !important; font-weight: 700 !important; color: #ffffff !important;
}
.brand-line {
    height: 3px;
    background: linear-gradient(90deg, #ff2a6d, #d6006e, transparent);
    margin: 8px 0 24px 0;
}
</style>
""", unsafe_allow_html=True)
 
# ── 2. CARGA DE DATOS ──
# ────────────────────────────────────────────────────────────────────────────
# 🛡️ CORRECCIÓN: La función de carga ya NO reconstruye features desde cero.
#    Ahora depende del archivo generado por procesar_ia.py como fuente única
#    de verdad, evitando que la lógica de features se duplique (y diverja)
#    entre este módulo y el pipeline de ML.
# ────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando análisis avanzado de Churn...")
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
 
    # Fuente principal: scoring precalculado por procesar_ia.py
    path_scoring  = os.path.join(base_dir, "data", "clientes_scoring_precalculado.csv")
    # Fallback legacy (si existe de una ejecución anterior del dashboard)
    path_procesado = os.path.join(base_dir, "data", "clientes_procesados.csv")
    path_train     = os.path.join(base_dir, "data", "sales_churn_train.csv")
 
    if os.path.exists(path_scoring):
        cust_df = pd.read_csv(path_scoring)
    elif os.path.exists(path_procesado):
        cust_df = pd.read_csv(path_procesado)
    else:
        st.error(
            "⚠️ No se encontró el archivo de datos procesados. "
            "Ejecuta primero `python procesar_ia.py` para generar el scoring."
        )
        st.stop()
 
    # Serie temporal de churn (necesita el CSV de entrenamiento)
    if not os.path.exists(path_train):
        monthly_df = pd.DataFrame(columns=["fecha", "churn_events", "churn_rate"])
    else:
        train_df = pd.read_csv(path_train)
        monthly = (
            train_df[train_df["target"] == 1]
            .groupby("calmonth").size()
            .reset_index(name="churn_events")
        )
        monthly["fecha"] = pd.to_datetime(
            monthly["calmonth"].astype(str), format="%Y%m", errors="coerce"
        )
        monthly_total = train_df.groupby("calmonth").size().reset_index(name="total_rows")
        monthly = monthly.merge(monthly_total, on="calmonth", how="left")
        monthly["churn_rate"] = (
            monthly["churn_events"] / monthly["total_rows"] * 100
        ).fillna(0)
        monthly_df = monthly
 
    return cust_df, monthly_df
 
cust_df, monthly_df = load_data()
 
# ── 3. FILTROS LATERALES ──
with st.sidebar:
    st.markdown("### Churn Hunters")
    st.markdown("<div class='brand-line'></div>", unsafe_allow_html=True)
    st.markdown("**Filtros globales**")
    st.markdown("---")
 
    territorios = sorted(cust_df["territory_d"].dropna().unique()) if "territory_d" in cust_df.columns else []
    territorios_sel = st.multiselect("📍 Región / Territorio", options=territorios, default=territorios)
 
    canales = sorted(cust_df["comercial_subchannel_d"].dropna().unique()) if "comercial_subchannel_d" in cust_df.columns else []
    canales_sel = st.multiselect("🏪 Canal comercial", options=canales, default=canales)
 
    tamanios = ["Mini", "Pequeño", "Mediano", "Grande", "Gigante"]
    tamanios_disponibles = (
        [t for t in tamanios if t in cust_df["rtm_customer_size_d"].unique()]
        if "rtm_customer_size_d" in cust_df.columns else []
    )
    tamanios_sel = st.multiselect("Tamaño de cliente", options=tamanios_disponibles, default=tamanios_disponibles)
 
    cooler_filter = st.selectbox("Enfriador asignado", options=["Todos", "Con enfriador", "Sin enfriador"])
 
# ── Filtrado dinámico con warning si queda vacío ──
# ────────────────────────────────────────────────────────────────────────────
# 🛡️ CORRECCIÓN: Antes, si todos los filtros se deseleccionaban, el DataFrame
#    quedaba vacío y los gráficos fallaban silenciosamente. Ahora se muestra
#    un aviso claro y se detiene el renderizado para evitar errores.
# ────────────────────────────────────────────────────────────────────────────
df = cust_df.copy()
if territorios_sel:
    df = df[df["territory_d"].isin(territorios_sel)]
if canales_sel:
    df = df[df["comercial_subchannel_d"].isin(canales_sel)]
if "rtm_customer_size_d" in df.columns and tamanios_sel:
    df = df[df["rtm_customer_size_d"].isin(tamanios_sel)]
if cooler_filter == "Con enfriador":
    df = df[df["tiene_cooler"] == 1]
elif cooler_filter == "Sin enfriador":
    df = df[df["tiene_cooler"] == 0]
 
if df.empty:
    st.warning("⚠️ La combinación de filtros seleccionada no arroja resultados. Ajusta los filtros del menú lateral.")
    st.stop()
 
n_total   = len(df)
n_churned = df["churned"].sum() if "churned" in df.columns else 0
tasa_churn = (n_churned / n_total * 100) if n_total > 0 else 0
 
# ── 4. ENCABEZADO ──
st.markdown("<h1>📊 Dashboard de Riesgo de Abandono</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#7a8099; margin:-10px 0 20px 0;'>"
    "Distribuidora Coca-Cola · Análisis de Churn · Hackathon 2026"
    "</p>",
    unsafe_allow_html=True
)
st.markdown("<div class='brand-line'></div>", unsafe_allow_html=True)
 
# ── 5. KPIs ──
st.markdown("## Panorama General")
k1, k2, k3, k4, k5, k6 = st.columns(6)
 
with k1:
    st.metric("Tasa de Churn", f"{tasa_churn:.1f}%", f"{int(n_churned):,} clientes")
with k2:
    mini_churn = (
        df[(df["rtm_customer_size_d"].str.contains("Mini|Micro|Pequeño", na=True)) & (df["churned"] == 1)].shape[0]
        if "rtm_customer_size_d" in df.columns else 0
    )
    st.metric("Clientes Mini Perdidos", f"{mini_churn:,}", "Segmento vulnerable")
with k3:
    cajas_riesgo = df[df["churned"] == 1]["total_boxes"].sum() if "total_boxes" in df.columns else 0
    st.metric("Cajas en Riesgo", f"{cajas_riesgo/1000:.0f}K", "Unidades pérdidas")
with k4:
    freq_act = df[df["churned"] == 0]["avg_transacciones"].mean() if "avg_transacciones" in df.columns else 0
    st.metric("Freq. Media Activos", f"{freq_act:.0f}", "pedidos / mes")
with k5:
    sin_cooler = (df["tiene_cooler"] == 0).mean() * 100 if n_total > 0 else 0
    st.metric("Sin Enfriador", f"{sin_cooler:.1f}%", "Falta de equipamiento")
with k6:
    if n_total > 0 and "territory_d" in df.columns and not df.groupby("territory_d")["churned"].mean().empty:
        reg_critica = df.groupby("territory_d")["churned"].mean().idxmax()
    else:
        reg_critica = "N/A"
    st.metric("Región Más Crítica", reg_critica, "Tasa máxima")
 
# ── 6. SECCIÓN GEOGRÁFICA Y TAMAÑO ──
st.markdown("---")
st.markdown("## ¿Dónde está el problema?")
col_left, col_right = st.columns([1.3, 1], gap="medium")
 
with col_left:
    st.markdown("### Tasa de Churn por Región")
    if "territory_d" in df.columns:
        terr_data = (
            df.groupby("territory_d")
            .agg(total=("churned","count"), churned=("churned","sum"))
            .reset_index()
        )
        terr_data["churn_rate"] = (terr_data["churned"] / terr_data["total"] * 100).round(1)
        terr_data = terr_data.sort_values("churn_rate").tail(15)
        fig_terr = px.bar(
            terr_data, x="churn_rate", y="territory_d", orientation="h",
            color="churn_rate", color_continuous_scale=ESCALA_ROSAS,
            text=terr_data["churn_rate"].astype(str) + "%"
        )
        fig_terr.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(family="DM Sans", color="#c4c9d8"),
            showlegend=False, coloraxis_showscale=False, height=400,
            xaxis_title="Tasa de Churn (%)", yaxis_title=""
        )
        st.plotly_chart(fig_terr, use_container_width=True)
 
with col_right:
    st.markdown("### Clientes Perdidos por Tamaño")
    if "rtm_customer_size_d" in df.columns:
        size_data = (
            df.groupby("rtm_customer_size_d")
            .agg(churned=("churned","sum"))
            .reset_index()
        )
        fig_size = px.pie(
            size_data, names="rtm_customer_size_d", values="churned", hole=0.55,
            color_discrete_sequence=[ROSA_FUERTE, MAGENTA, ROSA_PASTEL, "#5c1331", "#3a1225"]
        )
        fig_size.add_annotation(
            text=f"<b>{int(n_churned):,}</b><br><span style='font-size:11px'>bajas</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#ffffff")
        )
        fig_size.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(family="DM Sans", color="#c4c9d8"), height=400
        )
        st.plotly_chart(fig_size, use_container_width=True)
 
# ── 7. COMPORTAMIENTO DE COMPRA ──
st.markdown("---")
st.markdown("## Comportamiento de Compra y Abandono")
col_a, col_b = st.columns(2, gap="medium")
 
with col_a:
    st.markdown("### Frecuencia de Compra: ¿Quién abandona?")
    if "avg_transacciones" in df.columns:
        freq_hist = df[df["avg_transacciones"] > 0].copy()
        freq_hist["Estado"] = freq_hist["churned"].map({1: "Abandonó", 0: "Activo"})
        fig_freq = px.histogram(
            freq_hist, x="avg_transacciones", color="Estado", nbins=50,
            barmode="overlay", opacity=0.75,
            color_discrete_map={"Abandonó": ROSA_FUERTE, "Activo": "#343a40"},
            range_x=[0, 300]
        )
        fig_freq.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(family="DM Sans", color="#c4c9d8"),
            height=340, xaxis_title="Transacciones promedio / mes", yaxis_title="Clientes"
        )
        st.plotly_chart(fig_freq, use_container_width=True)
 
with col_b:
    st.markdown("### Volumen Comprado: Activos vs Churned")
    if "avg_boxes" in df.columns:
        vol_data = df[df["avg_boxes"].between(0, 800)].copy()
        vol_data["Estado"] = vol_data["churned"].map({1: "Abandonó", 0: "Activo"})
        fig_vol = px.box(
            vol_data, x="Estado", y="avg_boxes", color="Estado",
            color_discrete_map={"Abandonó": ROSA_FUERTE, "Activo": "#5c1331"},
            points=False
        )
        fig_vol.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(family="DM Sans", color="#c4c9d8"),
            height=340, showlegend=False,
            yaxis_title="Cajas promedio / mes", xaxis_title=""
        )
        st.plotly_chart(fig_vol, use_container_width=True)
 
# ── 8. EVOLUCIÓN TEMPORAL Y CANALES ──
st.markdown("---")
st.markdown("## Evolución Temporal del Churn y Canales Críticos")
col_c, col_d = st.columns([1.6, 1], gap="medium")
 
with col_c:
    st.markdown("### Histórico Mensual de Bajas")
    if not monthly_df.empty:
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(
            x=monthly_df["fecha"], y=monthly_df["churn_events"],
            fill="tozeroy", fillcolor="rgba(255, 42, 109, 0.1)",
            line=dict(color=ROSA_FUERTE, width=2.5), name="Bajas"
        ))
        fig_time.add_trace(go.Scatter(
            x=monthly_df["fecha"], y=monthly_df["churn_rate"],
            line=dict(color=ROSA_PASTEL, width=1.5, dash="dot"),
            name="Tasa %", yaxis="y2"
        ))
        fig_time.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(family="DM Sans", color="#c4c9d8"), height=340,
            yaxis=dict(title="Clientes que abandonaron", gridcolor="#1f2433"),
            yaxis2=dict(title="Tasa de Churn (%)", overlaying="y", side="right"),
            legend=dict(orientation="h", y=-0.15)
        )
        st.plotly_chart(fig_time, use_container_width=True)
 
with col_d:
    st.markdown("### Churn por Canal Comercial")
    if "comercial_subchannel_d" in df.columns:
        canal_data = (
            df.groupby("comercial_subchannel_d")
            .agg(total=("churned","count"), churned=("churned","sum"))
            .reset_index()
        )
        canal_data["churn_rate"] = (canal_data["churned"] / canal_data["total"] * 100).round(1)
        canal_data = canal_data.sort_values("churn_rate")
        fig_canal = px.bar(
            canal_data, x="churn_rate", y="comercial_subchannel_d", orientation="h",
            color="churn_rate", color_continuous_scale=ESCALA_ROSAS,
            text=canal_data["churn_rate"].astype(str) + "%"
        )
        fig_canal.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(family="DM Sans", color="#c4c9d8"),
            height=340, showlegend=False, coloraxis_showscale=False,
            xaxis_title="Tasa %", yaxis_title=""
        )
        st.plotly_chart(fig_canal, use_container_width=True)
 
# ── 9. MÉTRICAS DEL MODELO ──────────────────────────────────────────────────
# 🛡️ NUEVO: Sección completa de desempeño del modelo para los jueces.
#    Lee el archivo metricas_modelo.json generado por procesar_ia.py.
# ────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Desempeño del Modelo de IA")
 
base_dir   = os.path.dirname(os.path.abspath(__file__))
path_metricas     = os.path.join(base_dir, "data", "metricas_modelo.json")
path_importancias = os.path.join(base_dir, "data", "importancias.json")
 
if not os.path.exists(path_metricas):
    st.info(
        "ℹ️ No se encontraron métricas del modelo. "
        "Ejecuta `python procesar_ia.py` para entrenar el modelo y generarlas."
    )
else:
    with open(path_metricas) as f:
        metricas = json.load(f)
 
    # KPIs del modelo
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("AUC-ROC", f"{metricas['auc_roc']:.3f}", "↑ mejor cuanto más cerca de 1.0")
    with m2:
        st.metric("Precisión (Churn=1)", f"{metricas['precision']:.3f}", "De los que predice como churn, ¿cuántos lo son?")
    with m3:
        st.metric("Recall (Churn=1)", f"{metricas['recall']:.3f}", "De los que realmente hacen churn, ¿cuántos detecta?")
    with m4:
        st.metric("F1-Score", f"{metricas['f1_score']:.3f}", "Balance precisión / recall")
 
    st.caption(
        f"Métricas evaluadas sobre un conjunto de prueba independiente "
        f"({metricas['test_size']} clientes, 20% del total). "
        f"El modelo nunca vio estos datos durante el entrenamiento."
    )
 
    col_roc, col_imp = st.columns(2, gap="medium")
 
    # Curva ROC
    with col_roc:
        st.markdown("### Curva ROC")
        roc_data = metricas.get("roc_curve", {})
        if roc_data:
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(
                x=roc_data["fpr"], y=roc_data["tpr"],
                mode="lines", line=dict(color=ROSA_FUERTE, width=2.5),
                name=f"AUC = {metricas['auc_roc']:.3f}"
            ))
            fig_roc.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode="lines", line=dict(color="#7a8099", width=1, dash="dash"),
                name="Clasificador aleatorio"
            ))
            fig_roc.update_layout(
                paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
                font=dict(family="DM Sans", color="#c4c9d8"),
                height=320,
                xaxis=dict(title="Tasa de Falsos Positivos", gridcolor="#1f2433"),
                yaxis=dict(title="Tasa de Verdaderos Positivos", gridcolor="#1f2433"),
                legend=dict(orientation="h", y=-0.2)
            )
            st.plotly_chart(fig_roc, use_container_width=True)
 
    # Importancia de features
    with col_imp:
        st.markdown("### Importancia de Variables")
        if os.path.exists(path_importancias):
            with open(path_importancias) as f:
                importancias = json.load(f)
 
            imp_df = (
                pd.Series(importancias)
                .reset_index()
                .rename(columns={"index": "Feature", 0: "Importancia"})
                .sort_values("Importancia")
            )
            fig_imp = px.bar(
                imp_df, x="Importancia", y="Feature", orientation="h",
                color="Importancia", color_continuous_scale=ESCALA_ROSAS
            )
            fig_imp.update_layout(
                paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
                font=dict(family="DM Sans", color="#c4c9d8"),
                height=320, coloraxis_showscale=False,
                xaxis_title="Importancia relativa", yaxis_title=""
            )
            st.plotly_chart(fig_imp, use_container_width=True)
 