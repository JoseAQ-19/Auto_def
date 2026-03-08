import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY no configurada.")
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"

    def generate_audio(self, text: str, voice_id: str = "qUPtETgSYRhCRb2pfOla", output_path: str = "output.mp3") -> str:
        """
        Llama a ElevenLabs para generar audio a partir del texto y lo guarda en output_path.
        Retorna la ruta del archivo generado.
        """
        url = f"{self.base_url}/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        logger.info(f"Generando audio para el texto ({len(text)} chars) con voz {voice_id}...")
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            logger.info(f"Audio guardado correctamente en: {output_path}")
            return output_path
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 402 and voice_id != "pNInz6obpgDQGcFmaJgB":
                logger.warning(f"Voz {voice_id} bloqueada por plan Free (402). Intentando fallback con voz masculina gratuita por defecto (Adam)...")
                return self.generate_audio(text, "pNInz6obpgDQGcFmaJgB", output_path)
            
            logger.error(f"Error HTTP al generar audio con ElevenLabs: {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al generar audio con ElevenLabs: {e}")
            raise
