import streamlit as st
import google.generativeai as genai
import requests
import io
from PIL import Image
import time

# Configuración de la página
st.set_page_config(page_title="Alipen IA - Arquitecto Estructural", page_icon="🏠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .stButton>button { background-color: #1a73e8; color: white; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏠 Alipen IA: Calco Arquitectónico")
st.write("Esta versión usa tu imagen como molde exacto para la remodelación.")

# Barra lateral
with st.sidebar:
    st.header("⚙️ Configuración")
    google_key = st.text_input("Google API Key", type="password")
    hf_token = st.text_input("Hugging Face Token (hf_...)", type="password")
    
    st.header("📐 Regla de Oro")
    fuerza = st.slider("Nivel de fidelidad estructural", 0.1, 0.9, 0.5, help="Menor número = más parecido a tu foto original.")
    estilo = st.selectbox("Estilo", ["Moderno Lujoso", "Industrial", "Minimalista", "Rústico"])

# Cuerpo principal
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Estructura Original")
    archivo = st.file_uploader("Sube tu fachada o plano (CAD/Foto)", type=['jpg', 'jpeg', 'png'])
    if archivo:
        img_input = Image.open(archivo)
        st.image(img_input, caption="Tu diseño base", use_container_width=True)

with col2:
    st.subheader("2. Remodelación sobre Molde")
    if st.button("EJECUTAR REMODELACIÓN"):
        if not google_key or not hf_token:
            st.error("Faltan las llaves API en la barra lateral.")
        elif archivo:
            with st.spinner("Generando calco estructural..."):
                try:
                    # 1. Gemini analiza materiales
                    genai.configure(api_key=google_key)
                    gemini = genai.GenerativeModel('gemini-1.5-flash')
                    res_gemini = gemini.generate_content([f"Describe materials for a {estilo} remodel. Keep structure same. English, 10 words.", img_input])
                    prompt_ia = res_gemini.text.strip()

                    # 2. Preparar imagen para Hugging Face
