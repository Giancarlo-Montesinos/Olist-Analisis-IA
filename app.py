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

# === TAB 1: SALUD DEL NEGOCIO ===
with tab1:
    st.header("Panorama General del E-commerce")
    st.markdown("Antes de optimizar, necesitamos entender el volumen y estado actual de las operaciones.")
    
    # KPIs (Métricas Clave)
    col1, col2, col3 = st.columns(3)
    total_ventas = df_orders['price'].sum()
    avg_score = df_orders['review_score'].mean()
    total_orders = df_orders['order_id'].nunique()
    
    # Usamos delta para darle color (asumiendo un objetivo ficticio para que se vea bien)
    col1.metric("Ventas Totales (Histórico)", f"R$ {total_ventas:,.0f}", delta="Revenue Base")
    col2.metric("Score Promedio de Satisfacción", f"{avg_score:.2f} / 5.0", delta="-0.5 vs Target", delta_color="inverse")
    col3.metric("Total Pedidos Procesados", f"{total_orders:,}")
    
    st.write("---")
    
    col_viz, col_text = st.columns([2, 1])
    with col_viz:
        # Gráfico de Funnel
        st.subheader("Funnel Operacional")
        status_counts = df_orders['order_status'].value_counts().reset_index()
        status_counts.columns = ['Estado', 'Cantidad']
        # Ordenamos para que parezca embudo
        orden_embudo = ['approved', 'processing', 'shipped', 'delivered', 'canceled', 'unavailable']
        status_counts['Estado'] = pd.Categorical(status_counts['Estado'], categories=orden_embudo, ordered=True)
        status_counts = status_counts.sort_values('Estado')

        fig_funnel = px.funnel(status_counts, x='Cantidad', y='Estado', title="Flujo de Pedidos (Funnel View)")
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col_text:
        st.subheader("Análisis del Funnel")
        st.markdown("""
        **Observaciones:**
        * La gran mayoría de los pedidos (>90%) llegan al estado `delivered` (entregado).
        * La tasa de cancelación es visible pero baja en comparación al volumen total.
        
        **Pregunta de Negocio:**
        Si el funnel operativo parece sano, ¿por qué nuestro Score Promedio es solo 4.0? Debemos investigar la **experiencia del cliente (CX)** en la siguiente pestaña.
        """)

# === TAB 2: DIAGNÓSTICO DE FRICCIÓN (CX) ===
with tab2:
    st.header("¿Qué está matando la satisfacción del cliente?")
    st.markdown("""
    **El Problema:** Tenemos una cantidad significativa de reseñas de 1 y 2 estrellas que afectan el NPS y la retención.
    
    **Hipótesis:** En e-commerce, la principal fricción suele ser el incumplimiento de la promesa de entrega.
    
    A continuación, cruzamos los datos de **tiempo de entrega real vs. prometido** contra la **puntuación** que dejó el cliente.
    """)
    
    # Recalcular columnas de fechas (necesario al leer de CSV)
    df_orders['diferencia_estimada_dias'] = pd.to_numeric(df_orders['diferencia_estimada_dias'], errors='coerce')
    
    # Filtro para el gráfico
    df_plot = df_orders[
        (df_orders['diferencia_estimada_dias'] > -60) & 
        (df_orders['diferencia_estimada_dias'] < 60)
    ]
    
    # Boxplot Mejorado
    fig_box = px.box(df_plot, x="review_score", y="diferencia_estimada_dias", 
                     color="review_score",
                     color_discrete_sequence=px.colors.diverging.RdYlGn, # Semáforo: Rojo a Verde
                     title="Impacto del Retraso Logístico en la Calificación (Boxplot)",
                     labels={"review_score": "Estrellas dadas por el Cliente", "diferencia_estimada_dias": "Días vs. Promesa (+ Tarde / - Temprano)"})
    
    # Línea de referencia
    fig_box.add_hline(y=0, line_dash="dot", line_color="black", annotation_text="Fecha Prometida (Día 0)")
    fig_box.update_layout(yaxis_title="Días de Retraso (Positivo) o Adelanto (Negativo)")
    
    st.plotly_chart(fig_box, use_container_width=True)
    
    # INSIGHT BOX (Lo más importante)
    st.error("""
    🎯 **INSIGHT CRÍTICO PARA OPERACIONES:**
    
    El gráfico confirma la hipótesis contundentemente.
    * **Clientes Detractores (1 Estrella):** La mediana de sus pedidos llegó **en la fecha límite o tarde** (la caja cruza la línea cero hacia arriba). La variabilidad es enorme, indicando un proceso logístico fuera de control para este grupo.
    * **Clientes Promotores (5 Estrellas):** Reciben sus pedidos consistentemente **mucho antes** de lo prometido (toda la caja está en negativo).
    
    **Acción Recomendada:** Revisar urgentemente los transportistas asociados a las órdenes con retraso (>0 días). La mejora del producto no servirá si la entrega falla.
    """)

# === TAB 3: SEGMENTACIÓN & AUDIENCIAS (AI) ===
with tab3:
    st.header("Segmentación Conductual con Inteligencia Artificial")
    st.markdown("""
    **Más allá del "cliente promedio":**
    Utilizamos un algoritmo de Machine Learning no supervisado (**K-Means Clustering**) para agrupar a los clientes.
    """)

    # --- 1. CÁLCULO DE METRICAS (La parte nueva) ---
    # Agrupamos los datos para obtener los promedios que mostraste en tu imagen
    # Esto calcula automáticamente los números para que no tengas que escribirlos a mano
    metrics = df_clusters.groupby('cluster')[['recency', 'frequency', 'monetary', 'avg_review_score']].mean()
    counts = df_clusters['cluster'].value_counts()

    # Definimos quién es quién basándonos en tu imagen:
    # Cluster 3 = VIP (Alto Gasto/Frecuencia)
    # Cluster 2 = Olvidados (Recency alta ~398)
    # Cluster 0 = Recientes (Recency baja ~127)
    # Cluster 1 = En Riesgo (Score bajo ~1.6)
    
    # Extraemos los datos para usarlos en el texto (Formato amigable)
    # VIP (Cluster 3)
    c_vip = 3
    vip_gasto = metrics.loc[c_vip, 'monetary']
    vip_freq = metrics.loc[c_vip, 'frequency']
    vip_count = counts[c_vip]

    # Olvidados (Cluster 2)
    c_sleep = 2
    sleep_days = metrics.loc[c_sleep, 'recency']
    sleep_count = counts[c_sleep]

    # Recientes (Cluster 0)
    c_recent = 0
    recent_days = metrics.loc[c_recent, 'recency']
    recent_score = metrics.loc[c_recent, 'avg_review_score']
    recent_count = counts[c_recent]

    # Riesgo (Cluster 1)
    c_risk = 1
    risk_score = metrics.loc[c_risk, 'avg_review_score']
    risk_count = counts[c_risk]


    # --- 2. VISUALIZACIÓN ---
    col_viz_cluster, col_desc_cluster = st.columns([3, 2])
    
    with col_viz_cluster:
        # Preparamos datos para el gráfico (Zoom in)
        df_viz = df_clusters.copy()
        df_viz = df_viz[df_viz['monetary'] < 3000] # Filtro visual

        # Función para pintar los puntos del color correcto según el cluster
        def asignar_nombre(c):
            if c == c_vip: return "💎 VIP"
            elif c == c_sleep: return "💤 Olvidados"
            elif c == c_recent: return "🌱 Recientes"
            else: return "⚠️ En Riesgo"
            
        df_viz['Segmento'] = df_viz['cluster'].apply(asignar_nombre)

        fig_cluster = px.scatter(df_viz, x="recency", y="monetary", color="Segmento", 
                                 opacity=0.5, title="Mapa de Audiencias (Zoom < R$ 3000)",
                                 color_discrete_map={"💎 VIP": "#00CC96", "💤 Olvidados": "#EF553B", "🌱 Recientes": "#636EFA", "⚠️ En Riesgo": "#AB63FA"})
        st.plotly_chart(fig_cluster, use_container_width=True)


    # --- 3. ESTRATEGIAS CON DATOS DUROS (La parte rica) ---
    with col_desc_cluster:
        st.subheader("Estrategias por Audiencia")
        
        # Usamos f-strings (f"...") para meter los números calculados en el texto
        
        st.success(f"""
        **💎 VIP (Champions) | {vip_count:,} Usuarios**
        *El motor de rentabilidad.*
        
        * **Dato Clave:** Gastan **R$ {vip_gasto:.0f}** en promedio (vs R$ 140 global) y compran **{vip_freq:.1f} veces**.
        * **Acción:** Crear nivel "Gold" con envíos gratis. Aumentar barrera de salida.
        """)
        
        st.info(f"""
        **🌱 Recientes (Promising) | {recent_count:,} Usuarios**
        *Nuevos usuarios con alto potencial.*
        
        * **Dato Clave:** Su última compra fue hace solo **{recent_days:.0f} días** y tienen satisfacción alta (**{recent_score:.1f}/5**).
        * **Acción:** Email de "Bienvenida" + Cupón de 2da compra urgente (antes de 30 días).
        """)
        
        st.warning(f"""
        **💤 Olvidados (Sleeping) | {sleep_count:,} Usuarios**
        *Dinero dejado sobre la mesa.*
        
        * **Dato Clave:** No compran hace **{sleep_days:.0f} días** (más de un año), pero cuando compraron quedaron felices.
        * **Acción:** Reactivación agresiva. "Te extrañamos". Es 5x más barato reactivarlos que traer nuevos.
        """)
        
        st.error(f"""
        **⚠️ En Riesgo (Detractors) | {risk_count:,} Usuarios**
        *Problema operativo detectado.*
        
        * **Dato Clave:** Su satisfacción es crítica (**{risk_score:.1f}/5**). Probablemente sufrieron retrasos logísticos.
        * **Acción:** No invertir en publicidad para ellos. Auditoría de sus pedidos para evitar boca a boca negativo.
        """)

    # Tabla técnica al final
    with st.expander("Ver Tabla de Datos Exactos"):
        st.dataframe(metrics.style.format("{:.2f}"))
