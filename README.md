# 📊 Olist E-Commerce: AI Behavior Research

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-Deployed-success?style=for-the-badge)](https://giancarlomontesinos-olist-anlisis.streamlit.app/)

> **Behavioral Analytics & Customer Segmentation usando Machine Learning.**

---

## 🚀 Live Demo
¡Prueba la aplicación interactiva ahora mismo! No requiere instalación.

👉 **[Ver Dashboard en Streamlit Cloud](https://giancarlomontesinos-olist-anlisis.streamlit.app/)**

---

## 🎯 El Problema de Negocio
**Olist**, un gigante del e-commerce brasileño, enfrenta un desafío común: entender **por qué los clientes abandonan la plataforma** y cómo identificar a los usuarios más valiosos antes de perderlos.

El objetivo de este proyecto no fue solo visualizar datos, sino responder tres preguntas críticas:
1.  ¿Qué factor operativo tiene la mayor correlación con las reseñas negativas (1 estrella)?
2.  ¿Podemos predecir el abandono (*churn*) usando solo datos demográficos y transaccionales?
3.  ¿Existen "tribus" ocultas de clientes que permitan estrategias de marketing diferenciadas?

---

## 💡 Hallazgos Clave (Key Insights)

### 1. El Asesino Silencioso: La Logística
Mediante análisis estadístico, descubrí que el **retraso en la entrega** es el factor determinante #1 para los detractores.
* **Usuarios Felices (5★):** Reciben sus pedidos en promedio **13 días antes** de lo prometido.
* **Detractores (1★):** Tienen una mediana de entrega cercana a **0 o días de retraso**.
> *Insight:* No es un problema de producto, es un problema de cumplimiento de expectativas.

### 2. Segmentación Conductual (K-Means Clustering)
Utilizando un algoritmo no supervisado, segmenté a +100,000 usuarios en 4 perfiles accionables:

| Cluster | Perfil | Características | Estrategia Recomendada |
| :--- | :--- | :--- | :--- |
| **0 - VIPs** | 💎 **Champions** | Alta frecuencia, Gasto alto. | Programas de fidelidad exclusivos. |
| **1 - Olvidados** | 💤 **Sleeping** | Alta satisfacción previa, pero inactivos (>1 año). | Campañas de reactivación "Te extrañamos". |
| **2 - Nuevos** | 🌱 **Promising** | Recientes, buena experiencia, bajo gasto. | Cross-selling inmediato para aumentar LTV. |
| **3 - En Riesgo** | ⚠️ **Detractors** | Mala experiencia, bajo retorno. | Análisis de causa raíz y contención. |

---

## 🛠️ Stack Tecnológico

Este proyecto fue desarrollado íntegramente en **Python** utilizando las siguientes librerías:

* **Procesamiento de Datos:** `Pandas`, `NumPy`.
* **Machine Learning:** `Scikit-learn` (Logistic Regression, K-Means, StandardScaler).
* **Visualización:** `Plotly Express` (Gráficos interactivos), `Matplotlib`, `Seaborn`.
* **Despliegue Web:** `Streamlit` (Frontend interactivo).

---

## 📂 Estructura del Proyecto

```bash
├── app.py                   # Aplicación principal (Dashboard Streamlit)
├── requirements.txt         # Dependencias del proyecto
├── olist_processed.csv.gz   # Dataset limpio y comprimido (Transacciones)
├── olist_clusters.csv       # Resultados del modelo de ML (Segmentación)
└── README.md                # Documentación# Olist-Analisis-IA
