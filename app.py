import streamlit as st
from google import genai
from huggingface_hub import InferenceClient
from PIL import Image
import io

# Configuración de la página
st.set_page_config(page_title="Alipen IA - Arquitecto Pro", page_icon="🏠", layout="wide")

# Estilo visual
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .stButton>button { background-color: #1a73e8; color: white; font-weight: bold; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏠 Alipen IA: Calco Estructural")
st.write("Transforma tu fachada respetando muros y ventanas originales.")

# Barra lateral para llaves y ajustes
with st.sidebar:
    st.header("⚙️ Configuración")
    google_key = st.text_input("Google API Key", type="password")
    hf_token = st.text_input("Hugging Face Token", type="password")
    
    st.header("📐 Regla de Oro")
    fuerza = st.slider("Fuerza del cambio", 0.1, 0.9, 0.45, 
                       help="0.3 = Respeta tus líneas al máximo. 0.7 = La IA es más creativa.")
    estilo = st.selectbox("Estilo Arquitectónico", ["Moderno Lujoso", "Industrial", "Minimalista", "Rústico"])

# Cuerpo principal: Dos columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Estructura Original")
    archivo = st.file_uploader("Sube tu foto o plano", type=['jpg', 'jpeg', 'png'])
    if archivo:
        img_input = Image.open(archivo)
        st.image(img_input, caption="Estructura Base", width="stretch")

with col2:
    st.subheader("2. Resultado del Calco")
    if st.button("GENERAR DISEÑO"):
        if not google_key or not hf_token:
            st.error("Por favor, introduce ambas llaves API en la izquierda.")
        elif archivo:
            with st.spinner("Analizando y calcando estructura..."):
                try:
                    # 1. Gemini analiza materiales (Usando el nuevo SDK google-genai)
                    client_google = genai.Client(api_key=google_key)
                    
                    prompt_analisis = f"Describe materials for a {estilo} architectural remodel. Keep the structure exactly the same. English,
