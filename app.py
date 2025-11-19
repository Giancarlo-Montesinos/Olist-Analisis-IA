import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Olist Behavior Research", layout="wide")

# --- TÍTULO Y PRESENTACIÓN ---
st.title("📊 Olist E-Commerce: AI Behavior Research")
st.markdown("""
Esta aplicación interactiva demuestra cómo el uso de **Machine Learning** ayuda a entender 
la insatisfacción del cliente y a segmentar usuarios para estrategias de marketing.
""")

# --- CARGA DE DATOS (Cache para velocidad) ---
@st.cache_data
def load_data():
    # Asegúrate de que estos archivos estén en la misma carpeta
    df_orders = pd.read_csv("olist_processed.csv.gz")
    df_clusters = pd.read_csv("olist_clusters.csv")
    return df_orders, df_clusters

try:
    df_orders, df_clusters = load_data()
except FileNotFoundError:
    st.error("❌ No se encontraron los archivos CSV. Asegúrate de descargarlos del Colab y ponerlos en la misma carpeta.")
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros Globales")
st.sidebar.info("Este dashboard fue creado por [Tu Nombre] usando Python y Streamlit.")

# --- PESTAÑAS DEL DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["📈 Diagnóstico de Negocio", "🚚 Logística vs. Satisfacción", "🤖 Segmentación con IA"])

# === TAB 1: DIAGNÓSTICO DE NEGOCIO ===
with tab1:
    st.header("Panorama General")
    
    # KPIs (Métricas Clave)
    col1, col2, col3 = st.columns(3)
    total_ventas = df_orders['price'].sum()
    avg_score = df_orders['review_score'].mean()
    total_orders = df_orders['order_id'].nunique()
    
    col1.metric("Ventas Totales", f"R$ {total_ventas:,.0f}")
    col2.metric("Score Promedio", f"{avg_score:.2f} / 5.0")
    col3.metric("Total Pedidos", f"{total_orders:,}")
    
    st.markdown("---")
    
    # Gráfico de Funnel (Estado de las órdenes)
    st.subheader("Estado de los Pedidos")
    status_counts = df_orders['order_status'].value_counts().reset_index()
    status_counts.columns = ['Estado', 'Cantidad']
    
    fig_funnel = px.bar(status_counts, x='Estado', y='Cantidad', color='Cantidad', title="Funnel de Operaciones")
    st.plotly_chart(fig_funnel, use_container_width=True)

# === TAB 2: LOGÍSTICA VS SATISFACCIÓN ===
with tab2:
    st.header("¿Por qué se quejan los clientes?")
    st.markdown("Hipótesis: La insatisfacción (1 estrella) está correlacionada con el retraso en la entrega.")
    
    # Recalcular columnas de fechas (al leer CSV vienen como texto)
    df_orders['diferencia_estimada_dias'] = pd.to_numeric(df_orders['diferencia_estimada_dias'], errors='coerce')
    
    # Filtro para el gráfico (quitar outliers extremos para ver mejor)
    df_plot = df_orders[
        (df_orders['diferencia_estimada_dias'] > -50) & 
        (df_orders['diferencia_estimada_dias'] < 50)
    ]
    
    # Boxplot con Plotly (Interactivo)
    fig_box = px.box(df_plot, x="review_score", y="diferencia_estimada_dias", 
                     color="review_score",
                     title="Distribución de Retrasos según Calificación (Boxplot)",
                     labels={"review_score": "Estrellas", "diferencia_estimada_dias": "Días vs. Promesa (Positivo = Tarde)"})
    
    # Línea de referencia (Cero)
    fig_box.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Fecha Prometida")
    
    st.plotly_chart(fig_box, use_container_width=True)
    
    st.warning("💡 **Insight:** Los clientes que dan 1 estrella tienen una mediana de entrega cercana a 0 o positiva (tarde), mientras que los de 5 estrellas reciben sus pedidos mucho antes de lo esperado.")

# === TAB 3: SEGMENTACIÓN CON IA ===
with tab3:
    st.header("Clustering de Comportamiento (K-Means)")
    st.markdown("Utilizando un algoritmo no supervisado, detectamos 4 perfiles de usuarios basándonos en su Recencia, Frecuencia y Gasto.")
    
    # Scatter Plot Interactivo
    fig_cluster = px.scatter(df_clusters, x="recency", y="monetary", color="cluster",
                             size="monetary", hover_data=["frequency", "avg_review_score"],
                             title="Mapa de Clusters: Recencia vs. Valor Monetario",
                             color_continuous_scale=px.colors.sequential.Viridis)
    
    st.plotly_chart(fig_cluster, use_container_width=True)
    
    # Explicación de Clusters
    st.subheader("Perfiles Detectados")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.success("**Cluster VIP (Alta Frecuencia):** Usuarios leales que gastan más. Estrategia: Programa de Fidelidad.")
        st.info("**Cluster Recientes:** Nuevos usuarios con buena experiencia. Estrategia: Cross-selling inmediato.")
        
    with col_b:
        st.warning("**Cluster Olvidados:** Compraron hace mucho pero tuvieron buena experiencia. Estrategia: Win-back campaign.")
        st.error("**Cluster Detractores:** Mala experiencia y bajo retorno. Estrategia: Análisis de causa raíz logística.")

    # Mostrar datos crudos opcionalmente
    if st.checkbox("Ver datos de la muestra"):
        st.dataframe(df_clusters.head(50))
