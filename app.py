import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient
from PIL import Image
import io

# Configuración de la página
st.set_page_config(page_title="Alipen IA - Arquitecto Pro", page_icon="🏠", layout="wide")

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
        st.image(img_input, caption="Estructura Base", use_container_width=True)

with col2:
    st.subheader("2. Resultado del Calco")
    if st.button("GENERAR DISEÑO"):
        if not google_key or not hf_token:
            st.error("Por favor, introduce ambas llaves API en la izquierda.")
        elif archivo:
            with st.spinner("Analizando y calcando estructura..."):
                try:
                    # 1. Gemini analiza materiales
                    genai.configure(api_key=google_key)
                    gemini = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Pedimos a Gemini que solo sugiera materiales para no confundir a la IA de imagen
                    res_gemini = gemini.generate_content([
                        f"Describe materials for a {estilo} architectural remodel. Keep the structure exactly the same. English, 10 words max.", 
                        img_input
                    ])
                    prompt_ia = res_gemini.text.strip()

                    # 2. Motor de Imagen (Usamos el cliente oficial para evitar errores de sintaxis)
                    client = InferenceClient("runwayml/stable-diffusion-v1-5", token=hf_token)
                    
                    # Redimensionar para que el servidor gratuito no se bloquee
                    img_input.thumbnail((768, 768))

                    # Llamada Image-to-Image (El Calco Real)
                    imagen_final = client.image_to_image(
                        image=img_input,
                        prompt=f"Professional architectural photo, {prompt_ia}, cinematic lighting, high-end materials, 8k, realistic",
                        negative_prompt="deformed, changed structure, extra windows, distorted walls, blurry, low quality",
                        strength=fuerza,
                        guidance_scale=8.0
                    )
                    
                    st.image(imagen_final, caption="Propuesta Alipen IA", use_container_width=True)
                    st.success(f"Materiales aplicados: {prompt_ia}")

                except Exception as e:
                    st.error(f"Error técnico: {e}")
        else:
            st.warning("Primero debes subir una imagen.")

st.markdown("---")
st.caption("Alipen IA 2026 - Tecnología de Precisión Arquitectónica")
