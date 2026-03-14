import os
from openai import OpenAI

def generate_novum_prompt(topic: str) -> str:
    """
    Llama al LLM intentando conectarse a múltiples proveedores en cascada (OpenRouter, Groq, HuggingFace)
    para asegurar cero fallos y redactar un Mega Prompt para el avatar Novum.
    """
    # 1. Definimos los proveedores en orden de prioridad (El primero que funcione, cortará la cascada)
    providers = [
        {
            "name": "NVIDIA",
            "api_key": os.getenv("NVIDIA_API_KEY"),
            "base_url": "https://integrate.api.nvidia.com/v1",
            "model": "meta/llama-3.1-70b-instruct"
        },
        {
            "name": "OpenRouter",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "base_url": "https://openrouter.ai/api/v1",
            "model": "meta-llama/llama-3.3-70b-instruct:free"
        },
        {
            "name": "Groq",
            "api_key": os.getenv("GROQ_API_KEY"),
            "base_url": "https://api.groq.com/openai/v1",
            "model": "llama-3.3-70b-versatile"
        },
        {
            "name": "Hugging Face",
            "api_key": os.getenv("HF_TOKEN_CEREBRO"),
            "base_url": "https://api-inference.huggingface.co/v1/",
            "model": "meta-llama/Llama-3.1-8B-Instruct"
        }
    ]
    
    system_prompt = (
        "Eres el 'Cerebro' de Novum, guionista de élite especializado en vídeos verticales de alta retención (Shorts, Reels, TikTok).\n\n"
        "REGLAS DE ORO PARA RETENCIÓN EXTREMA:\n"
        "1. ESTRUCTURA DINÁMICA: Debes generar exactamente 8 o 9 escenas. Cada escena dura un máximo de 6 segundos.\n"
        "2. LÍMITE DE PALABRAS: El diálogo de 'novum' por cada escena NO puede superar las 20 palabras. Sé directo y punzante.\n"
        "3. SIN OUTRO: PROHIBIDO escribir despedidas, cierres o llamadas a la acción (CTAs) como 'sígueme para más'. El vídeo termina abruptamente en el Cliffhanger.\n\n"
        "ESTRUCTURA NARRATIVA (EL EMBUDO):\n"
        "- Escenas 1 y 2 (El GANCHO - 12 seg): Empieza con una afirmación explosiva sobre el artículo. Plantea el problema central de inmediato. Sin introducciones.\n"
        "- Escenas 3, 4 y 5 (Desglose Rápido - 18 seg): Proporciona 3 datos clave, cifras o secretos del artículo. Un solo dato impactante por cada escena.\n"
        "- Escenas 6 y 7 (El GIRO - 12 seg): Eleva la tensión. Muestra el lado sorprendente, complejo o peligroso de la noticia.\n"
        "- Escena 8 o 9 (El CLIFFHANGER - 6 seg): Frena en seco. Deja la pregunta más importante sin responder o avisa de una consecuencia brutal. Ej: 'Pero lo que nadie vio venir fue esto...' o 'El detalle que lo cambia todo es el siguiente...'.\n\n"
        "TU TAREA: Estructurar la respuesta ESTRICTAMENTE así:\n\n"
        "Metadatos\n"
        "Título: (Un título muy corto, visual y SEO para redes).\n"
        "Descripción: (Una descripción misteriosa e intrigante).\n"
        "Hashtags: (3 o 4 separados por comas, ej: novum, IA, shorts).\n\n"
        "Guion del video (DIÁLOGO)\n"
        "[Escena 1]: \"(Texto hablado < 20 palabras en ESPAÑOL)\".\n"
        "... (Repetir para todas las escenas) ...\n"
        "[Escena Final]: \"(Texto hablado Cliffhanger en ESPAÑOL)\".\n\n"
        "Guion de Acciones (STORYBOARD)\n"
        "[Escena 1]: (Descripción breve de lo que hace el personaje en la escena).\n"
        "... (Repetir para todas las escenas) ...\n"
        "[Escena Final]: (Descripción breve de la acción final).\n\n"
        "Guion imágenes (PROMPTS PARA IA)\n"
        "(Un prompt en INGLÉS por cada escena, optimizado para generación de imagen/video).\n\n"
        "REGLAS TÉCNICAS PARA IMÁGENES:\n"
        "- MENCIONES, NO DESCRIPCIONES: El software 'AutoGrok' detecta automáticamente a los personajes. PROHIBIDO describir rostros, ropa, pelo o rasgos físicos. Menciona solo el nombre.\n"
        "- PERSONAJES PERMITIDOS: Usa siempre 'novum' como protagonista. Si la noticia lo requiere, puedes incluir personajes famosos reales (ej: 'elon musk', 'donald trump', 'sam altman') tratándolos solo por su nombre.\n"
        "- REGLA DE ORO DE AUTO-MATCH: Solo nombre exacto del personaje + acción. (Ej: 'novum hacking a server' o 'elon musk laughing in mars').\n"
        "- Separa cada prompt de imagen con una línea en blanco.\n"
        "- Prompts visuales en INGLÉS, diálogos en ESPAÑOL."
    )
    
    user_prompt = f"El tema destacado del día extraído de Google Search Console es: '{topic}'. Genera tu Mega Prompt analizando rápidamente este hito para el humano."
    
    last_error = None
    
    for p in providers:
        if not p["api_key"]:
            continue # Saltamos a este proveedor si no tiene API Key configurada
            
        print(f"🤖 Intentando conectar con {p['name']}...")
        try:
            client = OpenAI(api_key=p["api_key"], base_url=p["base_url"])
            response = client.chat.completions.create(
                model=p["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            print(f"✅ ¡Éxito conectando a través de {p['name']}!")
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Fallo en {p['name']}: {str(e)}")
            last_error = e
            continue # Si falla, sigue al siguiente de la lista
            
    raise RuntimeError(f"TODOS LOS PROVEEDORES LLM FALLARON. Verifica tus API Keys. Último error: {last_error}")
