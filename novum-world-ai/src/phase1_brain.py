import os
import json
import logging
import requests
from data_scanner import DataScanner
from audio_engine import AudioEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase1Brain:
    def __init__(self):
        self.scanner = DataScanner()
        self.audio_engine = AudioEngine()
        self.output_json_path = os.path.join(os.path.dirname(__file__), "..", "shooting_plan.json")
        self.hf_token = os.getenv("HF_TOKEN_CEREBRO", os.getenv("GROQ_API_KEY", ""))

    def get_llm_script(self, prompt_text: str) -> list:
        if not self.hf_token:
            logger.warning("Token de LLM no encontrado. Generando guion por defecto.")
            return [
                {
                    "type": "podcast", 
                    "text": "¡Hola a todos! Este es un guion de prueba generado automáticamente como fallback."
                },
                {
                    "type": "action", 
                    "prompt": "Cinematic shot of neon green data falling like rain, hacker typing rapidly on a holographic keyboard, unreal engine 5 render, 4k"
                }
            ]

        system_prompt = '''Eres el Director Creativo de Novum World.
Tu tarea es tomar una idea de artículo y devolver un array de JSON estricto con las escenas del vídeo.
Formatos permitidos en el array:
- {"type": "podcast", "text": "Texto que Novum locutará a cámara."}
- {"type": "action", "prompt": "Prompt visual hiperdescriptivo para generar B-Roll o de acción."}
Asegúrate de que haya consistencia y no devuelvas NADA MÁS que el JSON (sin backticks ni markdown).'''

        try:
            logger.info("Solicitando guion a Hugging Face Inference API (Cerebro)...")
            response = requests.post(
                "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.hf_token}", "Content-Type": "application/json"},
                json={
                    "model": "meta-llama/Llama-3.3-70B-Instruct",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt_text}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            if content.startswith("```"):
                content = content.replace("```", "").strip()
                
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error parseando o consultando LLM: {e}. Usando guion de respaldo.")
            return [
                {"type": "podcast", "text": "Ha habido un error en la matriz creativa de Novum, pero seguimos adelante."}
            ]

    def execute(self):
        logger.info("--- INICIANDO FASE 1: THE BRAIN ---")
        
        # 1. Escanear GSC
        logger.info("Obteniendo artículo Top de Google Search Console...")
        top_url = self.scanner.get_top_article()
        prompt_guion = self.scanner.compose_prompt_for_script(top_url)
        
        # 2. Obtener Guion del LLM
        plan = self.get_llm_script(prompt_guion)
        
        # 3. Generar Audio para Podcast
        logger.info("Generando tracks de audio para las escenas tipo Podcast...")
        output_plan = []
        podcast_count = 0
        
        # Directorio base para audio
        base_dir = os.path.dirname(self.output_json_path)
        
        for scene in plan:
            if scene.get("type") == "podcast":
                text = scene.get("text", "")
                audio_filename = os.path.join(base_dir, f"audio_scene_{podcast_count}.wav")
                try:
                    actual_audio_path = self.audio_engine.generate_audio(text, output_path=audio_filename)
                    scene["audio_file"] = actual_audio_path
                    podcast_count += 1
                except Exception as e:
                    logger.error(f"Error generando audio para la escena {podcast_count}: {e}")
                    scene["audio_file"] = ""
            
            output_plan.append(scene)
            
        # 4. Guardar archivo shooting plan
        with open(self.output_json_path, "w", encoding="utf-8") as f:
            json.dump(output_plan, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Fase 1 completada. Plan de rodaje guardado en: {self.output_json_path}")
        return self.output_json_path

if __name__ == "__main__":
    brain = Phase1Brain()
    brain.execute()
