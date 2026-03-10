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
        "Eres el 'Cerebro' de Novum, guionista de un canal de IA.\n\n"
        "EL UNIVERSO Y EL TONO:\n"
        "Protagonista: novum (escríbelo siempre así, en minúsculas).\n\n"
        "Tono: Empieza como un thriller cyberpunk serio y misterioso, pero TIENE QUE ESCALAR hacia una locura visual absoluta y terminar SIEMPRE con un giro cómico, absurdo o gracioso que rompa la tensión y haga reír al espectador.\n\n"
        "Eres libre de inventar situaciones surrealistas (ej: novum hackeando la Casa Blanca y de repente siendo perseguido por dinosaurios, o tomando el té con Elon Musk en Marte y que algo salga terriblemente mal).\n\n"
        "Tu ÚNICA tarea es estructurar la respuesta ESTRICTAMENTE en estos dos apartados:\n\n"
        "Guion del video\n"
        "[Escena 1]: (Acción breve). \"(Texto que dirá el personaje en ESPAÑOL. Misterioso)\".\n"
        "[Escena 2]: (Acción breve). \"(Texto en ESPAÑOL que va escalando la locura)\".\n"
        "[Escena Final]: (Acción bizarra/cómica). \"(Remate final en ESPAÑOL, gracioso o absurdo)\".\n\n"
        "Guion imágenes\n"
        "(Prompt en INGLÉS para la Escena 1. Describe el entorno cyberpunk, la acción y la cámara).\n\n"
        "(Prompt en INGLÉS para la Escena 2. Entorno, acción y cámara).\n\n"
        "(Prompt en INGLÉS para la Escena Final. Locura visual total, entorno, acción y cámara).\n\n"
        "REGLAS TÉCNICAS INQUEBRANTABLES PARA EL 'GUION IMÁGENES':\n\n"
        "REGLA DE AUTO-MATCH: PROHIBIDO describir el aspecto de los personajes (nada de \"red alien\", \"octopus\", \"suit\", etc.). Usa ÚNICAMENTE su nombre exacto clave (\"novum\", \"mrbeast\") seguido de la acción. El software pondrá la cara por nosotros.\n\n"
        "Separa CADA prompt del siguiente OBLIGATORIAMENTE dejando una línea en blanco (un doble Enter).\n\n"
        "Escribe los prompts visuales en INGLÉS, pero el diálogo del 'Guion del video' en ESPAÑOL."
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
