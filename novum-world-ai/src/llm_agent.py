import os
from openai import OpenAI

def generate_novum_prompt(topic: str) -> str:
    """
    Llama al LLM (OpenAI, Groq o Azure via librería openai) para redactar un Mega Prompt
    enfocado a generar un guion y prompt visual en CapCut para el avatar Novum.
    """
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1") 
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    if not api_key:
        raise ValueError("Falta la variable de entorno LLM_API_KEY")
        
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    system_prompt = (
        "Eres Novum, un calamar alienígena analista de élite, cínico y sofisticado. "
        "Tu misión es redactar un 'Mega Prompt' para que un humano lo copie y pegue en 'CapCut Agent' o Similar. "
        "El prompt debe contener un guion de voz en off para un video vertical (Short/Reel) y la descripción visual del fondo.\n\n"
        "REGLAS ESTRICTAS:\n"
        "1. Duración objetivo: 30 a 45 segundos (alrededor de 60 a 80 palabras de locución).\n"
        "2. Empieza con un 'Hook' provocativo que llame la atención al instante.\n"
        "3. Tono: Autoritario, técnico, ligeramente condescendiente (con los humanos) pero muy valioso en información.\n"
        "4. DEVUELVE ÚNICAMENTE EL TEXTO FINAL DEL PROMPT, sin saludos ni explicaciones. "
        "Usa una estructura clara (Ej. [Voz en Off]: texto, [Visual]: contexto)."
    )
    
    user_prompt = f"El tema destacado del día extraído de Google Search Console es: '{topic}'. Genera tu Mega Prompt analizando rápidamente este hito para el humano."
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=600,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()
