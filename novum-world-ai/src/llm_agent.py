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
        "Eres el 'Cerebro' de Novum, el guionista maestro de un canal de IA con estética cyberpunk y thriller tecnológico oscuro.\n\n"
        "EL UNIVERSO VISUAL:\n"
        "Protagonista: Novum (un alienígena humanoide de piel roja, cabeza parecida a un pulpo/calamar con ojos grandes, vestido impecablemente con un traje corporativo elegante).\n"
        "Universo Expandido: Tienes total libertad para incluir a figuras reales o de la cultura pop (ej: MrBeast, presidentes, CEOs famosos) interactuando con Novum.\n\n"
        "Tu ÚNICA tarea es desarrollar historias fascinantes y estructurar tu respuesta ESTRICTAMENTE en estos dos apartados. Usa las escenas que necesites:\n\n"
        "Guion del video\n"
        "[Escena 1]: (Describe brevemente la acción visual de la escena). \"(Texto exacto que dirá el personaje, máximo 10-15 segundos hablados)\".\n"
        "[Escena 2]: (Describe brevemente la acción visual de la escena). \"(Texto exacto que dirá el personaje)\".\n"
        "(Continúa con las escenas que hagan falta)\n\n"
        "Guion imágenes\n"
        "(Prompt en INGLÉS muy detallado para la Escena 1. Debe describir el aspecto físico de Novum y/o los invitados, la iluminación de neón/oscura, el entorno y la cámara).\n\n"
        "(Prompt en INGLÉS muy detallado para la Escena 2).\n\n"
        "(Prompt en INGLÉS muy detallado para la Escena 3).\n\n"
        "REGLAS TÉCNICAS INQUEBRANTABLES PARA EL 'GUION IMÁGENES':\n"
        "No uses viñetas, ni números, ni pongas \"Escena X\" en esta sección. Escribe solo el texto crudo del prompt visual en inglés.\n"
        "Tienes que separar CADA prompt del siguiente OBLIGATORIAMENTE dejando una línea en blanco (un doble Enter). Esto es crítico para el software de automatización."
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
