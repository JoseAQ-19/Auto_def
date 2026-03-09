import os
from openai import OpenAI

def generate_novum_prompt(topic: str) -> str:
    """
    Llama al LLM (OpenAI, Groq o Azure via librería openai) para redactar un Mega Prompt
    enfocado a generar un guion y prompt visual en CapCut para el avatar Novum.
    """
    api_key = os.getenv("HF_TOKEN_CEREBRO")
    base_url = os.getenv("LLM_BASE_URL", "https://api-inference.huggingface.co/v1/") 
    model = os.getenv("LLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    
    if not api_key:
        raise ValueError("Falta la variable de entorno HF_TOKEN_CEREBRO")
        
    client = OpenAI(api_key=api_key, base_url=base_url)
    
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
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()
