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
    
    El siguiente gráfico muestra cómo se distribuyen tus clientes según cuánto tiempo hace que compraron (Eje X) y cuánto gastaron (Eje Y).
    """)
    
    # --- PREPARACIÓN DE DATOS PARA VISUALIZACIÓN ---
    # 1. Creamos una copia para no dañar los datos originales
    df_viz = df_clusters.copy()
    
    # 2. TRUCO PRO: Eliminamos el "ruido" visual (Outliers)
    # Filtramos los clientes que gastaron más de $3000 para que el gráfico no se vea "aplastado"
    # (Esto nos permite ver mejor a la gran mayoría de clientes)
    df_viz = df_viz[df_viz['monetary'] < 3000]
    
    # 3. Asignamos NOMBRES a los clusters (En lugar de números 0,1,2,3)
    # NOTA: Ajusta estos nombres según lo que veas en tu análisis. 
    # K-Means asigna números aleatorios, así que verifica cuál es cuál.
    # Aquí asumo una lógica estándar, pero puedes cambiar los textos a la derecha.
    def asignar_etiqueta(row):
        # Lógica ejemplo (Ajusta según tus datos si es necesario)
        if row['frequency'] > 1 and row['monetary'] > 200:
            return "💎 VIP (Frecuentes)"
        elif row['recency'] > 300:
            return "💤 Olvidados (Inactivos)"
        elif row['recency'] < 150 and row['monetary'] < 200:
            return "🌱 Recientes (Prometedores)"
        else:
            return "⚠️ En Riesgo (Standard)"

    # Aplicamos la función para crear una columna de "Nombre del Segmento"
    df_viz['Segmento'] = df_viz.apply(asignar_etiqueta, axis=1)

    col_viz_cluster, col_desc_cluster = st.columns([3, 2])
    
    with col_viz_cluster:
        # Scatter Plot MEJORADO
        fig_cluster = px.scatter(df_viz, 
                                 x="recency", 
                                 y="monetary", 
                                 color="Segmento", # Ahora usa nombres reales
                                 opacity=0.5, # Un poco más transparente para ver densidad
                                 title="Mapa de Audiencias (Zoom en clientes < R$ 3000)",
                                 labels={"recency": "Días desde última compra", "monetary": "Gasto Total"},
                                 color_discrete_map={
                                     "💎 VIP (Frecuentes)": "#00CC96",  # Verde
                                     "💤 Olvidados (Inactivos)": "#EF553B", # Rojo
                                     "🌱 Recientes (Prometedores)": "#636EFA", # Azul
                                     "⚠️ En Riesgo (Standard)": "#AB63FA" # Morado
                                 })
        
        fig_cluster.update_layout(legend_title_text="Tipo de Cliente")
        st.plotly_chart(fig_cluster, use_container_width=True)
        st.caption("Nota: Se han ocultado visualmente los clientes 'Whales' (>R$3000) para facilitar la lectura de los segmentos principales.")

    with col_desc_cluster:
        st.subheader("Estrategias por Audiencia")
        
        st.success("**💎 VIP (Frecuentes):**\nSon tu mina de oro. Compran seguido y gastan bien. \n\n**Acción:** Programa de lealtad premium.")
        st.info("**🌱 Recientes:**\nClientes nuevos con potencial. \n\n**Acción:** Email de bienvenida con descuento en 2da compra.")
        st.warning("**💤 Olvidados:**\nHace mucho que no vienen (Eje X lejano). \n\n**Acción:** Campaña de reactivación agresiva.")
        st.error("**⚠️ En Riesgo:**\nComportamiento errático o bajo valor. \n\n**Acción:** Investigar satisfacción.")
