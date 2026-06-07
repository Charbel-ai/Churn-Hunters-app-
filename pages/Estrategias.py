import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px

st.set_page_config(
    page_title="Estrategias Predictivas · Churn Hunters",
    layout="wide"
)

# ── 1. INYECCIÓN DE ESTILO COMPLETO (CON TEXTOS Y FILTROS AMPLIADOS) ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght=400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Fondo principal */
[data-testid="stHeader"], .stAppHeader, [data-testid="stAppViewContainer"] { 
    background-color: #0d0f14 !important; 
}
.stApp { background: #0d0f14; color: #e8eaf0; }

/* Forzar Menú Lateral Negro y Texto Claro */
[data-testid="stSidebar"], 
[data-testid="stSidebarNav"], 
.stSidebar, 
div[data-testid="stSidebarUserContent"] {
    background-color: #0d0f14 !important;
    background: #0d0f14 !important;
    border-right: 1px solid #1f2433 !important;
}
[data-testid="stSidebarNav"] span, 
[data-testid="stSidebarNav"] a,
.stSidebar nav li div {
    color: #e8eaf0 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: #161a24 !important;
}

.brand-line { height: 3px; background: linear-gradient(90deg, #ff2a6d, #d6006e, transparent); margin: 8px 0 24px 0; }

/* Tarjetas Métricas Tradicionales */
div[data-testid="stMetric"] { background: #161a24 !important; border: 1px solid #252b3b !important; border-radius: 10px !important; padding: 15px 20px !important; }
div[data-testid="stMetricValue"] > div { color: #ff2a6d !important; font-size: 2.2rem !important; font-weight: 700 !important; }

/* Distribución de Riesgos */
.risk-bar-container {
    background: #141722;
    border: 1px solid #202636;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0 30px 0;
}
.risk-bar-title {
    font-size: 1.1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #a2a8c2;
    margin-bottom: 12px;
}
.risk-bar-track {
    display: flex;
    height: 24px;
    border-radius: 6px;
    overflow: hidden;
    background: #252b3b;
    margin-bottom: 15px;
}
.segment-bajo { background: #ffb3d1; height: 100%; }
.segment-medio { background: #d6006e; height: 100%; }
.segment-alto { background: #ff2a6d; height: 100%; }

.risk-legend-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
}
.legend-item {
    padding: 10px 15px;
    border-radius: 6px;
    background: #10131a;
    border: 1px solid #1f2535;
    text-align: center;
}
.legend-label { font-size: 0.85rem; color: #7a8099; text-transform: uppercase; margin-bottom: 4px; }
.legend-value { font-size: 1.4rem; font-weight: 700; }

/* 🌟 PREGUNTAS ANALÍTICAS 🌟 */
.pregunta-analitica {
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin-top: 15px !important;
    margin-bottom: 15px !important;
    display: block;
}

/* 🌟 FILTRO DE RADIO BUTTONS (NIVEL DE RIESGO) 🌟 */
div[data-testid="stRadio"] > label {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin-bottom: 12px !important;
}
div[data-testid="stRadio"] div[data-testid="stWidgetMarkdownClaims"] p {
    font-size: 1.15rem !important;
    font-weight: 500 !important;
}

/* Tarjetas Métricas del Consultor Individual */
.cyber-card {
    background: #141722;
    border: 1px solid #202636;
    border-radius: 8px;
    padding: 18px 22px;
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.cyber-label {
    color: #7a8099 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
    font-weight: 500;
}
.cyber-value-pink { color: #ff2a6d !important; font-size: 2.5rem !important; font-weight: 700 !important; line-height: 1; }
.cyber-value-green { color: #ffb3d1 !important; font-size: 1.8rem !important; font-weight: 700; } 
.cyber-value-red { color: #ff2a6d !important; font-size: 1.8rem !important; font-weight: 700 !important; }

/* Ficha de Datos Generales */
.data-profile-box { background: #10131a; border: 1px solid #1f2535; border-radius: 8px; padding: 15px 20px; margin-bottom: 20px; }
.data-profile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
.data-item b { color: #ff2a6d; }

/* Alertas de Contención */
.plan-container { margin-top: 25px; }
.plan-title { font-size: 1.4rem; font-weight: 700; color: #ffffff; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
.alert-box-warn { background-color: #1a1316; border: 1px solid #d6006e33; border-left: 5px solid #d6006e; border-radius: 6px; padding: 18px; color: #ffa3d1; font-size: 0.95rem; line-height: 1.5; }
.alert-box-crit { background-color: #1c1216; border: 1px solid #ff2a6d33; border-left: 5px solid #ff2a6d; border-radius: 6px; padding: 18px; color: #ff78a5; font-size: 0.95rem; line-height: 1.5; }
.alert-box-safe { background-color: #141115; border: 1px solid #ffb3d133; border-left: 5px solid #ffb3d1; border-radius: 6px; padding: 18px; color: #ffe3ee; font-size: 0.95rem; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ── 2. ENCABEZADO DE LA INTERFAZ ──────────────────────────────────
st.markdown("<h1>🧠 Panel de Decisiones Predictivas (IA)</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#7a8099; margin:-10px 0 10px 0;'>Sistema de scoring en tiempo real para la mitigación proactiva del abandono (Churn)</p>", unsafe_allow_html=True)
st.markdown("<div class='brand-line'></div>", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def cargar_scoring_optimizado():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_backup = os.path.join(base_dir, "data", "clientes_scoring_precalculado.csv")
    path_imp = os.path.join(base_dir, "data", "importancias.json")
    
    if os.path.exists(path_backup):
        df_scoring = pd.read_csv(path_backup)
        importancias = {}
        if os.path.exists(path_imp):
            with open(path_imp, 'r') as f:
                importancias = json.load(f)
        return df_scoring, importancias
    return pd.DataFrame(), {}

df_scoring, importancias_dict = cargar_scoring_optimizado()

if df_scoring.empty:
    st.error("⚠️ No se han encontrado datos precalculados. Ejecuta 'python procesar_ia.py' en tu terminal.")
else:
    df_scoring['Nivel_Riesgo'] = pd.cut(
        df_scoring['probabilidad_churn'], 
        bins=[0, 0.35, 0.70, 1.0], 
        labels=['Bajo', 'Medio', 'Alto']
    ).fillna('Bajo')

    # Métricas Globales Macro
    total_clientes = len(df_scoring)
    clientes_alto = len(df_scoring[df_scoring['Nivel_Riesgo'] == 'Alto'])
    clientes_medio = len(df_scoring[df_scoring['Nivel_Riesgo'] == 'Medio'])
    clientes_bajo = len(df_scoring[df_scoring['Nivel_Riesgo'] == 'Bajo'])

    pct_alto = (clientes_alto / total_clientes) * 100
    pct_medio = (clientes_medio / total_clientes) * 100
    pct_bajo = (clientes_bajo / total_clientes) * 100

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Total de Clientes Evaluados", value=f"{total_clientes:,}")
    with m2:
        st.metric(label="Clientes en Riesgo Crítico (Alto)", value=f"{clientes_alto:,}", delta=f"{pct_alto:.1f}%", delta_color="inverse")
    with m3:
        st.metric(label="Oportunidad de Captura Comercial", value="$12M MXN", delta="Meta del Reto")

    # Distribución Porcentual
    st.markdown(f"""
    <div class="risk-bar-container">
        <div class="risk-bar-title">📊 Distribución Porcentual del Riesgo en Cartera (Comportamiento Total)</div>
        <div class="risk-bar-track">
            <div class="segment-bajo" style="width: {pct_bajo}%;"></div>
            <div class="segment-medio" style="width: {pct_medio}%;"></div>
            <div class="segment-alto" style="width: {pct_alto}%;"></div>
        </div>
        <div class="risk-legend-grid">
            <div class="legend-item" style="border-bottom: 3px solid #ffb3d1;">
                <div class="legend-label">🌸 Riesgo Bajo (Saludables)</div>
                <div class="legend-value" style="color: #ffb3d1;">{pct_bajo:.1f}% <span style="font-size:0.9rem; color:#7a8099; font-weight:normal;">({clientes_bajo:,})</span></div>
            </div>
            <div class="legend-item" style="border-bottom: 3px solid #d6006e;">
                <div class="legend-label">🔮 Riesgo Medio (Inestables)</div>
                <div class="legend-value" style="color: #d6006e;">{pct_medio:.1f}% <span style="font-size:0.9rem; color:#7a8099; font-weight:normal;">({clientes_medio:,})</span></div>
            </div>
            <div class="legend-item" style="border-bottom: 3px solid #ff2a6d;">
                <div class="legend-label">🚨 Riesgo Alto (Críticos)</div>
                <div class="legend-value" style="color: #ff2a6d;">{pct_alto:.1f}% <span style="font-size:0.9rem; color:#7a8099; font-weight:normal;">({clientes_alto:,})</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Diagnóstico Gráfico
    st.markdown("## 📊 Diagnóstico y Visualización Analítica")
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.markdown('<span class="pregunta-analitica">🔍 Pregunta 1: ¿Qué variables influyen más en que un cliente deje de comprar?</span>', unsafe_allow_html=True)
        if importancias_dict:
            df_imp = pd.DataFrame(list(importancias_dict.items()), columns=['Variable', 'Importancia']).sort_values('Importancia', ascending=True)
            nombres_limpios = {
                'trend_ratio': 'Tendencia de Compra (Caída)', 'total_boxes': 'Volumen de Cajas Total',
                'avg_boxes': 'Promedio de Cajas por Mes', 'total_transacciones': 'Frecuencia de Transacciones',
                'meses_activo': 'Antigüedad del Cliente', 'tiene_cooler': 'Infraestructura de Frío',
                'avg_coolers': 'Cantidad de Coolers', 'territorio_encoded': 'Zona Geográfica'
            }
            df_imp['Variable'] = df_imp['Variable'].map(nombres_limpios).fillna(df_imp['Variable'])
            fig_imp = px.bar(df_imp, x='Importancia', y='Variable', orientation='h', color_discrete_sequence=['#ff2a6d'])
            fig_imp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=280)
            st.plotly_chart(fig_imp, use_container_width=True)

    with col_der:
        st.markdown('<span class="pregunta-analitica">📍 Pregunta 2: ¿El territorio o zona geográfica influye en la pérdida?</span>', unsafe_allow_html=True)
        df_geo = df_scoring.groupby('territory_id')['probabilidad_churn'].mean().reset_index()
        df_geo.columns = ['Territorio', 'Riesgo Promedio']
        df_geo = df_geo.sort_values('Riesgo Promedio', ascending=False).head(10)
        fig_geo = px.line(df_geo, x='Territorio', y='Riesgo Promedio', markers=True, color_discrete_sequence=['#d6006e'])
        fig_geo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=280)
        st.plotly_chart(fig_geo, use_container_width=True)

    st.markdown("---")

    # ── Análisis de Coolers Corregido ──
    st.markdown('<span class="pregunta-analitica">❄️ Pregunta 3: ¿La cantidad de coolers que tiene un cliente afecta su riesgo de churn?</span>', unsafe_allow_html=True)
    df_coolers_analysis = df_scoring.groupby('tiene_cooler')['probabilidad_churn'].mean().reset_index()
    
    # Validación segura de existencia de categorías
    tiene_con_cooler = 1 in df_coolers_analysis['tiene_cooler'].values
    tiene_sin_cooler = 0 in df_coolers_analysis['tiene_cooler'].values

    riesgo_con = df_coolers_analysis.loc[df_coolers_analysis['tiene_cooler'] == 1, 'probabilidad_churn'].values[0] * 100 if tiene_con_cooler else 0.0
    riesgo_sin = df_coolers_analysis.loc[df_coolers_analysis['tiene_cooler'] == 0, 'probabilidad_churn'].values[0] * 100 if tiene_sin_cooler else 0.0
    
    if tiene_sin_cooler:
        st.markdown(f"<p style='font-size:1.1rem;'>Los clientes <b>SIN infraestructura de frío</b> tienen un riesgo de <b>{riesgo_sin:.1f}%</b>, contra un <b>{riesgo_con:.1f}%</b> de los que sí tienen un cooler comodato.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='font-size:1.1rem;'>🎯 <b>Análisis de Infraestructura de Frío:</b> El 100% de la cartera de clientes cuenta actualmente con equipos de frío asignados. El riesgo promedio general optimizado manteniendo la salud de los coolers es de <b>{riesgo_con:.1f}%</b>.</p>", unsafe_allow_html=True)

    st.markdown("---")

    # ── 3. CONSULTOR INDIVIDUAL EXTENDIDO ──
    st.markdown("## 🔍 Consultor Individual de Clientes (Acción de Campo)")
    st.markdown("<p style='color:#7a8099; margin:-10px 0 15px 0;'>Filtra por categoría y selecciona el ID de cualquier tiendita para auditar sus datos generales y plan de acción de retención.</p>", unsafe_allow_html=True)
    
    filtro_riesgo = st.radio("🎯 Filtrar lista de clientes por nivel de riesgo:", options=["Alto", "Medio", "Bajo"], horizontal=True)
    
    clientes_filtrados = df_scoring[df_scoring['Nivel_Riesgo'] == filtro_riesgo]['customer_id'].unique()
    
    if len(clientes_filtrados) > 0:
        id_seleccionado = st.selectbox(f"🏪 Selecciona un ID de Cliente (Categoría: Riesgo {filtro_riesgo}):", options=clientes_filtrados)
        datos_cliente = df_scoring[df_scoring['customer_id'] == id_seleccionado].iloc[0]
        
        st.markdown("### 📋 Información General del Cliente")
        territorio_val = datos_cliente.get('territory_id', 'No Registrado')
        tamano_val = datos_cliente.get('size', datos_cliente.get('tamaño', 'Mediana (Canal Tradicional)'))
        segmento_val = datos_cliente.get('segment', datos_cliente.get('segmento', 'Miscelánea / Tiendita'))
        
        st.markdown(f"""
        <div class="data-profile-box">
            <div class="data-profile-grid">
                <div class="data-item">🆔 <b>ID Cliente:</b> <span style="color:#e8eaf0;">{id_seleccionado}</span></div>
                <div class="data-item">📍 <b>Territorio / Zona:</b> <span style="color:#e8eaf0;">{territorio_val}</span></div>
                <div class="data-item">📐 <b>Tamaño de Cliente:</b> <span style="color:#e8eaf0;">{tamano_val}</span></div>
                <div class="data-item">🏢 <b>Giro / Segmento:</b> <span style="color:#e8eaf0;">{segmento_val}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        card_col1, card_col2, card_col3, card_col4 = st.columns(4)
        with card_col1:
            st.markdown(f"""<div class="cyber-card"><div class="cyber-label">Riesgo de Abandono</div><div class="cyber-value-pink">{datos_cliente['probabilidad_churn']*100:.1f}%</div></div>""", unsafe_allow_html=True)
        with card_col2:
            st.markdown(f"""<div class="cyber-card"><div class="cyber-label">Compras Totales (Cajas)</div><div class="cyber-value-pink">{int(datos_cliente['total_boxes'])}</div></div>""", unsafe_allow_html=True)
        with card_col3:
            st.markdown(f"""<div class="cyber-card"><div class="cyber-label">Transacciones Totales</div><div class="cyber-value-pink">{int(datos_cliente['total_transacciones'])}</div></div>""", unsafe_allow_html=True)
        with card_col4:
            cooler_status_html = '<div class="cyber-value-green">Sí ✅</div>' if datos_cliente['tiene_cooler'] == 1 else '<div class="cyber-value-red">No ❌</div>'
            st.markdown(f"""<div class="cyber-card"><div class="cyber-label">¿Tiene Refrigerador?</div>{cooler_status_html}</div>""", unsafe_allow_html=True)
            
        st.markdown("""<div class="plan-container"><div class="plan-title">📋 Plan de Contención Comercial</div></div>""", unsafe_allow_html=True)
        
        # Lógica de planes adaptada a carteras con infraestructura de frío instalada
        if filtro_riesgo == "Alto":
            if datos_cliente['tiene_cooler'] == 0:
                st.markdown(f"""<div class="alert-box-crit">🪓 <b>ALERTA COMERCIAL CRÍTICA (ID {id_seleccionado}):</b> Cliente sin activo de frío y tendencia de compras baja (<b>{datos_cliente['trend_ratio']:.2f}</b>). <b>Acción:</b> Instalar refrigerador comodato urgente para amarrar la exclusividad antes de la fuga.</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="alert-box-crit">⚠️ <b>ALERTA DE VOLUMEN CRÍTICA (ID {id_seleccionado}):</b> Cuenta con cooler asignado pero sus transacciones y volumen de cajas cayeron drásticamente (Tendencia: <b>{datos_cliente['trend_ratio']:.2f}</b>). <b>Acción:</b> Enviar al supervisor de ruta urgentemente para verificar fallas mecánicas en el equipo de frío o negociar un ajuste de precios por volumen.</div>""", unsafe_allow_html=True)
        elif filtro_riesgo == "Medio":
            st.markdown(f"""<div class="alert-box-warn">⏳ <b>PREVENCIÓN TEMPRANA (ID {id_seleccionado}):</b> La tiendita muestra un comportamiento inestable en transacciones mensuales (<b>{datos_cliente['avg_transacciones']:.1f}</b>). <b>Acción:</b> Inyectar promociones del portafolio premium de Arca Continental en su próxima visita para incentivar la recompra.</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="alert-box-safe">🌸 <b>CLIENTE SALUDABLE (ID {id_seleccionado}):</b> Cuenta completamente estable y leal. Rendimiento excelente. <b>Acción:</b> Candidato óptimo para campañas de Cross-selling, introducción de nuevos sabores y aumento del espacio en anaquel (Share of Wallet).</div>""", unsafe_allow_html=True)
            
    else:
        st.info(f"No se encontraron registros de clientes en la categoría de riesgo {filtro_riesgo}.")