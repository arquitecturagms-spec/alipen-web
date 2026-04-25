import os
import io
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
from google import genai
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

# 1. CONFIGURACIÓN DE LLAVES (Secrets)
HF_TOKEN = os.environ.get("HF_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")

# 2. CLIENTES DE IA
client_google = genai.Client(api_key=GOOGLE_KEY) if GOOGLE_KEY else None
client_img = InferenceClient("runwayml/stable-diffusion-v1-5", token=HF_TOKEN)

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/remodelar", methods=["POST"])
def remodelar():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No se recibió imagen"}), 400
        
        file = request.files['image']
        img_input = Image.open(file.stream).convert("RGB")
        
        # REGLA DE ORO: Redimensionar para calco exacto
        img_input.thumbnail((768, 768))
        
        prompt_ia = "modern luxury architecture, high-end materials, glass and wood, realistic, 8k"

        # PASO 1: Gemini analiza materiales
        if client_google:
            try:
                response = client_google.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=["Describe only materials for a modern remodel. Keep the structure exactly the same. English, 15 words max.", img_input]
                )
                if response.text:
                    prompt_ia = response.text.strip()
            except:
                pass

        # PASO 2: Hugging Face hace el calco (Image-to-Image)
        # Intentamos hasta 3 veces por si el servidor está ocupado
        for i in range(3):
            try:
                imagen_final = client_img.image_to_image(
                    image=img_input,
                    prompt=f"Professional architectural photo, {prompt_ia}, cinematic lighting, highly detailed",
                    negative_prompt="changed structure, extra windows, distorted walls, blurry, bad architecture",
                    strength=0.45, # Mantiene el 55% de tu estructura original
                    guidance_scale=7.5
                )
                
                # Convertir resultado a bytes para enviar al HTML
                img_io = io.BytesIO()
                imagen_final.save(img_io, 'PNG')
                img_io.seek(0)
                return send_file(img_io, mimetype='image/png')
            
            except Exception as e:
                if "503" in str(e):
                    time.sleep(10)
                    continue
                raise e

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Puerto 7860 para compatibilidad total
    app.run(host="0.0.0.0", port=7860)
