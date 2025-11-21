import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero) ---
st.set_page_config(page_title="Portafolio: Olist Growth Analytics", layout="wide", page_icon="📈")

# --- TÍTULO Y RESUMEN EJECUTIVO ---
st.title("🚀 Olist E-Commerce: De Datos a Estrategia de Growth")
st.markdown("""
> **Resumen Ejecutivo:** Este proyecto analiza +100,000 transacciones reales para detectar fricciones en el funnel y oportunidades de retención. 
>
> **Hallazgos Principales:**
> 1. 🚚 **La logística es el principal detractor:** El 75% de las quejas (1 estrella) provienen de retrasos en la entrega.
> 2. 🎯 **Segmentación accionable:** La IA detectó 4 "tribus" de usuarios, incluyendo un segmento "Olvidado" (alta satisfacción previa, inactivos) ideal para reactivación.
""")
st.write("---")

# --- CARGA DE DATOS (Cache para velocidad) ---
@st.cache_data
def load_data():
    # Usamos .gz para que cargue rápido en la nube
    try:
        df_orders = pd.read_csv("olist_processed.csv.gz")
    except FileNotFoundError:
        # Fallback por si no está comprimido localmente
        df_orders = pd.read_csv("olist_processed.csv")
        
    df_clusters = pd.read_csv("olist_clusters.csv")
    return df_orders, df_clusters

try:
    df_orders, df_clusters = load_data()
except FileNotFoundError:
    st.error("❌ Error crítico: No se encontraron los archivos de datos (csv o csv.gz).")
    st.stop()

# --- BARRA LATERAL (PERFIL PROFESIONAL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3048/3048122.png", width=100) # Icono genérico o tu foto
    st.header("Sobre el Analista")
    st.markdown("**Giancarlo Montesinos**")
    st.markdown("Marketing & Data Insights")
    st.write("---")
    st.markdown("ESTRATEGIA + CÓDIGO")
    st.info("""
    Este portafolio demuestra la capacidad de traducir datos crudos en planes de acción para equipos de Growth y Marketing.
    
    **Tech Stack:** Python, Pandas, Scikit-learn (K-Means), Plotly.
    """)

# --- PESTAÑAS DEL DASHBOARD ---
# Nombres más orientados a negocio
tab1, tab2, tab3 = st.tabs(["📊 1. Salud del Negocio", "🚚 2. Diagnóstico de Fricción (CX)", "🤖 3. Segmentación & Audiencias (AI)"])

# === TAB 1: SALUD DEL NEGOCIO (GROWTH VIEW) ===
with tab1:
    st.header("Panorama General & Tendencias")
    
    # 1. PREPARACIÓN DE DATOS TEMPORALES
    # Asegurarnos de que la fecha sea datetime
    df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
    
    # Crear columnas de Año-Mes para agrupar
    df_orders['mes'] = df_orders['order_purchase_timestamp'].dt.to_period('M').astype(str)
    
    # Agrupar ventas por mes
    ventas_mensuales = df_orders.groupby('mes')['price'].sum().reset_index()
    
    # Calcular métricas globales
    total_ventas = df_orders['price'].sum()
    total_orders = df_orders['order_id'].nunique()
    ticket_promedio = total_ventas / total_orders
    
    # 2. KPIs DE NEGOCIO (Más detallados)
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Ventas Totales", f"R$ {total_ventas:,.0f}")
    col2.metric("📦 Total Pedidos", f"{total_orders:,}")
    col3.metric("🏷️ Ticket Promedio", f"R$ {ticket_promedio:.2f}")
    
    st.markdown("---")
    
    # 3. GRÁFICOS DE TENDENCIA Y GEOGRAFÍA
    col_trend, col_geo = st.columns([2, 1])
    
    with col_trend:
        st.subheader("Evolución de Ventas Mensuales")
        fig_trend = px.line(ventas_mensuales, x='mes', y='price', markers=True,
                            title="Tendencia de Ingresos (Growth)",
                            labels={'mes': 'Mes', 'price': 'Ingresos (R$)'})
        fig_trend.update_traces(line_color='#00CC96')
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_geo:
        st.subheader("Top Mercados (Estados)")
        # Contar pedidos por estado
        top_states = df_orders['customer_state'].value_counts().head(5).reset_index()
        top_states.columns = ['Estado', 'Pedidos']
        
        # --- MEJORA: DICCIONARIO DE NOMBRES ---
        # Traducimos las siglas para que se entienda mejor
        nombres_brasil = {
            'SP': 'São Paulo',
            'RJ': 'Rio de Janeiro',
            'MG': 'Minas Gerais',
            'RS': 'Rio Grande do Sul',
            'PR': 'Paraná',
            'SC': 'Santa Catarina',
            'BA': 'Bahia'
        }
        # Creamos una nueva columna con el nombre completo
        # Si no encuentra el nombre, deja la sigla original (usando un lambda)
        top_states['Nombre Completo'] = top_states['Estado'].map(nombres_brasil).fillna(top_states['Estado'])
        
        fig_geo = px.bar(top_states, x='Nombre Completo', y='Pedidos', 
                         title="Top 5 Regiones de Brasil", 
                         text_auto='.2s', # Muestra el número encima de la barra (ej. 40k)
                         color='Pedidos',
                         color_continuous_scale='Blues')
        
        # Ocultamos la barra de color lateral para que se vea más limpio
        fig_geo.update_layout(coloraxis_showscale=False)
        
        st.plotly_chart(fig_geo, use_container_width=True)

    # 4. FUNNEL OPERATIVO (Lo mantenemos pero más pequeño abajo)
    with st.expander("Ver Funnel Operativo Detallado"):
        status_counts = df_orders['order_status'].value_counts().reset_index()
        status_counts.columns = ['Estado', 'Cantidad']
        orden = ['approved', 'processing', 'shipped', 'delivered', 'canceled']
        fig_funnel = px.funnel(status_counts, x='Cantidad', y='Estado')
        st.plotly_chart(fig_funnel, use_container_width=True)

# === TAB 2: DIAGNÓSTICO DE FRICCIÓN (CX) ===
with tab2:
    st.header("Impacto Logístico en la Experiencia (CX)")
    
    # 1. CÁLCULOS DE FRICTION
    # Convertir a numérico
    df_orders['diferencia_estimada_dias'] = pd.to_numeric(df_orders['diferencia_estimada_dias'], errors='coerce')
    
    # Definir "Pedido Tardío" (Late Order): Diferencia > 0
    late_orders = df_orders[df_orders['diferencia_estimada_dias'] > 0]
    pct_late = (len(late_orders) / len(df_orders)) * 100
    
    # Promedio de retraso para reviews de 1 estrella
    avg_delay_1star = df_orders[df_orders['review_score'] == 1]['diferencia_estimada_dias'].median()
    avg_delay_5star = df_orders[df_orders['review_score'] == 5]['diferencia_estimada_dias'].median()
    
    # 2. KPIs DE DOLOR
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    col_kpi1.metric("⚠️ Tasa de Pedidos Tardíos", f"{pct_late:.1f}%", delta="Objetivo < 5%", delta_color="inverse")
    
    col_kpi2.metric("😠 Retraso en Clientes 1★", f"{avg_delay_1star:.1f} días", 
                    help="Mediana de días de retraso para clientes que dieron 1 estrella.")
    
    col_kpi3.metric("😍 Entrega en Clientes 5★", f"{avg_delay_5star:.1f} días",
                    delta="Entregas anticipadas",
                    help="Mediana de días de ANTICIPACIÓN para clientes felices.")
    
    st.write("---")

    # 3. VISUALIZACIÓN PRINCIPAL (BOXPLOT)
    st.subheader("Correlación: Tiempo de Entrega vs. Calificación")
    st.markdown("Este gráfico demuestra que la **velocidad de entrega** es el predictor más fuerte de la satisfacción.")
    
    # Filtro visual para quitar ruido extremo
    df_plot = df_orders[
        (df_orders['diferencia_estimada_dias'] > -60) & 
        (df_orders['diferencia_estimada_dias'] < 60)
    ]
    
    fig_box = px.box(df_plot, x="review_score", y="diferencia_estimada_dias", 
                     color="review_score",
                     color_discrete_sequence=px.colors.diverging.RdYlGn,
                     labels={"review_score": "Estrellas", "diferencia_estimada_dias": "Días de Retraso (+ Tarde / - Temprano)"})
    
    fig_box.add_hline(y=0, line_dash="dot", line_color="black", annotation_text="Promesa de Entrega")
    st.plotly_chart(fig_box, use_container_width=True)
    
    # 4. CONCLUSIÓN DE NEGOCIO
    # ¡OJO A LA 'f' ANTES DE LAS COMILLAS! ES LA CLAVE.
    st.error(f"""
    🛑 **DIAGNÓSTICO:**
    El **{pct_late:.1f}%** de los pedidos no cumplen la promesa de entrega.
    Existe una correlación directa: Los clientes que califican con **1 Estrella** recibieron su pedido, en mediana, **{avg_delay_1star:.1f} días tarde**.
    """)

# === TAB 3: SEGMENTACIÓN & AUDIENCIAS (AI) ===
with tab3:
    st.header("Segmentación Conductual con Inteligencia Artificial")
    st.markdown("""
    **Más allá del "cliente promedio":**
    Utilizamos un algoritmo de Machine Learning no supervisado (**K-Means Clustering**) para agrupar a los clientes.
    """)

    # --- 1. CÁLCULO DE METRICAS ---
    metrics = df_clusters.groupby('cluster')[['recency', 'frequency', 'monetary', 'avg_review_score']].mean()
    counts = df_clusters['cluster'].value_counts()

    # Mapeo de Clusters (Ajusta estos índices si tus colores cambiaron)
    c_vip = 3
    c_sleep = 2
    c_recent = 0
    c_risk = 1

    # Definimos el orden exacto que queremos para TODO (Gráfica, Cards y Tabla)
    orden_visual = ["💎 VIP", "🌱 Recientes", "💤 Olvidados", "⚠️ En Riesgo"]

    # Función para asignar nombres
    def asignar_nombre(c):
        if c == c_vip: return "💎 VIP"
        elif c == c_sleep: return "💤 Olvidados"
        elif c == c_recent: return "🌱 Recientes"
        else: return "⚠️ En Riesgo"

    # --- 2. VISUALIZACIÓN ---
    col_viz_cluster, col_desc_cluster = st.columns([3, 2])
    
    with col_viz_cluster:
        df_viz = df_clusters.copy()
        df_viz = df_viz[df_viz['monetary'] < 3000] # Filtro visual
        df_viz['Segmento'] = df_viz['cluster'].apply(asignar_nombre)

        # GRÁFICO: Usamos 'category_orders' para forzar el orden de la leyenda
        fig_cluster = px.scatter(df_viz, x="recency", y="monetary", color="Segmento", 
                                 opacity=0.5, title="Mapa de Audiencias (Zoom < R$ 3000)",
                                 labels={"recency": "Días sin comprar", "monetary": "Gasto Total"},
                                 category_orders={"Segmento": orden_visual}, # <--- AQUÍ ESTÁ EL TRUCO
                                 color_discrete_map={
                                     "💎 VIP": "#00CC96", 
                                     "💤 Olvidados": "#EF553B", 
                                     "🌱 Recientes": "#636EFA", 
                                     "⚠️ En Riesgo": "#AB63FA"
                                 })
        
        # Leyenda arriba para ahorrar espacio
        fig_cluster.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_cluster, use_container_width=True)

    # --- 3. ESTRATEGIAS (EN EL MISMO ORDEN) ---
    with col_desc_cluster:
        st.subheader("Estrategias por Audiencia")
        
        # 1. VIP
        vip_data = metrics.loc[c_vip]
        st.success(f"""
        ##### 💎 VIP (Champions) | {counts[c_vip]:,} Usuarios
        *El motor de rentabilidad.*
        - 💰 **Gasto Prom:** R$ {vip_data['monetary']:.0f} (vs R$ 140 avg)
        - 🔄 **Frecuencia:** {vip_data['frequency']:.1f} compras
        - 🎯 **Acción:** Nivel "Gold" + Envíos gratis.
        """)
        
        # 2. RECIENTES
        recent_data = metrics.loc[c_recent]
        st.info(f"""
        ##### 🌱 Recientes (Promising) | {counts[c_recent]:,} Usuarios
        *Alto potencial de desarrollo.*
        - 📅 **Última compra:** Hace {recent_data['recency']:.0f} días
        - ⭐ **Satisfacción:** {recent_data['avg_review_score']:.1f} / 5.0
        - 🎯 **Acción:** Cupón 2da compra (Urgente < 30 días).
        """)
        
        # 3. OLVIDADOS
        sleep_data = metrics.loc[c_sleep]
        st.warning(f"""
        ##### 💤 Olvidados (Sleeping) | {counts[c_sleep]:,} Usuarios
        *Dinero dejado sobre la mesa.*
        - 💤 **Inactividad:** {sleep_data['recency']:.0f} días (> 1 año)
        - 🎯 **Acción:** Reactivación agresiva ("Te extrañamos").
        """)
        
        # 4. EN RIESGO
        risk_data = metrics.loc[c_risk]
        st.error(f"""
        ##### ⚠️ En Riesgo (Detractors) | {counts[c_risk]:,} Usuarios
        *Problema operativo detectado.*
        - ⭐ **Satisfacción Crítica:** {risk_data['avg_review_score']:.1f} / 5.0
        - 🎯 **Acción:** Auditoría logística. No hacer retargeting.
        """)

    # --- 4. TABLA MEJORADA (REORDENADA) ---
    st.write("---")
    with st.expander("📋 Ver Tabla de Métricas Detallada"):
        # Preparamos la tabla
        tabla_final = metrics.copy()
        # Le ponemos los nombres
        tabla_final.index = [asignar_nombre(i) for i in tabla_final.index]
        # LA REORDENAMOS para que coincida con el gráfico y las cards
        tabla_final = tabla_final.reindex(orden_visual) 
        
        st.dataframe(tabla_final.style.format("{:.2f}").background_gradient(cmap="Blues"))
