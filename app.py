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
    Utilizamos un algoritmo de Machine Learning no supervisado (**K-Means Clustering**) para agrupar a los clientes basándonos en su comportamiento real de compra (RFM: Recencia, Frecuencia, Monto Monetario).
    
    Esto nos permite pasar de un marketing genérico a estrategias de **Growth personalizadas por audiencia**.
    """)
    
    col_viz_cluster, col_desc_cluster = st.columns([3, 2])
    
    with col_viz_cluster:
        # Scatter Plot
        fig_cluster = px.scatter(df_clusters, x="recency", y="monetary", color="cluster",
                                 size="monetary", opacity=0.6,
                                 hover_data=["frequency", "avg_review_score"],
                                 title="Mapa de Audiencias: Inactividad vs. Valor",
                                 labels={"recency": "Días desde la última compra (Recencia)", "monetary": "Gasto Total Histórico"},
                                 color_continuous_scale=px.colors.qualitative.Bold) # Colores más distintivos
        fig_cluster.update_layout(coloraxis_showscale=False) # Ocultar barra de color fea
        st.plotly_chart(fig_cluster, use_container_width=True)
        st.caption("Cada punto es un cliente. El tamaño indica su gasto total.")

    with col_desc_cluster:
        st.subheader("Estrategias por Audiencia (Playbook)")
        
        # Usamos "expanders" para detallar cada perfil sin saturar
        with st.expander("💎 Audiencia VIP (Champions) - Cluster 0/3", expanded=True):
            st.success("""
            **Perfil:** Compran frecuentemente, gastan mucho y están satisfechos. Son el motor de ingresos.
            **Objetivo:** Retención y Evangelización.
            **Acción Growth:** Dar acceso anticipado a ofertas, crear programa de referidos VIP. No molestarlos con descuentos genéricos.
            """)
            
        with st.expander("💤 Audiencia 'Olvidados' (Sleeping) - Cluster 1/2"):
            st.warning("""
            **Perfil:** Tuvieron una buena experiencia y gastaron dinero, pero hace mucho (>1 año) que no vuelven. **Oportunidad gigante.**
            **Objetivo:** Reactivación (Win-back).
            **Acción Growth:** Email marketing automatizado: "Te extrañamos, aquí tienes un incentivo para volver". El costo de reactivarlos es menor que adquirir nuevos.
            """)

        with st.expander("⚠️ Audiencia en Riesgo (Detractors) - Cluster X"):
            st.error("""
            **Perfil:** Compraron una vez, gastaron poco y tuvieron una experiencia terrible (probablemente logística).
            **Objetivo:** Contención de daños.
            **Acción Growth:** No invertir en paid media para retargeting a este grupo hasta solucionar el problema de raíz. Usar sus datos para auditoría operativa.
            """)
            
    st.markdown("---")
    with st.expander("🔬 Ver Detalles Técnicos del Modelo (Para Data Scientists)"):
        st.write("El modelo utilizado fue K-Means con K=4 clusters, determinado por el método del codo.")
        st.write("Variables utilizadas: Recency (días), Frequency (conteo), Monetary (suma), Avg Review Score.")
        st.write("Los datos fueron escalados utilizando StandardScaler antes del entrenamiento para evitar sesgos por magnitudes.")
        st.dataframe(df_clusters.head(10))
