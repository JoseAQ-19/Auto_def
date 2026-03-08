import os
import logging
from gradio_client import Client, handle_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoEngine:
    def __init__(self):
        # Tokens y URLs para los dos espacios Hugging Face
        self.podcast_url = os.environ.get("HF_SPACE_PODCAST_URL")
        self.action_url = os.environ.get("HF_SPACE_ACTION_URL")
        self.podcast_token = os.environ.get("HF_TOKEN_PODCAST")
        self.action_token = os.environ.get("HF_TOKEN_ACTION")

        if not self.podcast_url or not self.action_url or not self.podcast_token or not self.action_token:
            logger.warning("Faltan credenciales de Hugging Face. Las conexiones podrían fallar.")

    def generate_podcast_video(self, audio_path: str, master_image_path: str, output_path: str = "podcast_output.mp4") -> str:
        """
        Conecta al Space LTX-2 (o similar para Lip-Sync), enviando el audio e imagen maestra.
        """
        if not self.podcast_url:
            raise ValueError("HF_SPACE_PODCAST_URL no configurada.")
            
        logger.info(f"Conectando al Estudio A (Podcast): {self.podcast_url}")
        client = Client(self.podcast_url, hf_token=self.podcast_token)
        
        # Asumimos que los parámetros del gradio client del modelo lip-sync son: imagen maestra, audio.
        # Ajustar los predict endpoints según la API expuesta por el Space concreto.
        logger.info(f"Enviando imagen {master_image_path} y audio {audio_path}...")
        try:
            result = client.predict(
                image=handle_file(master_image_path),
                audio=handle_file(audio_path),
                api_name="/predict"
            )
            # El client.predict guarda el archivo devuelto en un /tmp/ local y devuelve la ruta
            os.rename(result, output_path)
            logger.info(f"Vídeo de podcast generado exitosamente en: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error en Estudio A (Podcast): {e}")
            raise

    def generate_action_video(self, text_prompt: str, master_image_path: str, output_path: str = "action_output.mp4") -> str:
        """
        Conecta al Space Wan2.2 (Omni Video Factory), enviando el prompt de texto e imagen maestra.
        """
        if not self.action_url:
            raise ValueError("HF_SPACE_ACTION_URL no configurada.")
            
        logger.info(f"Conectando al Estudio B (Acción): {self.action_url}")
        client = Client(self.action_url, hf_token=self.action_token)
        
        # Asumimos que los parámetros del gradio client son: prompt visual, imagen maestra.
        logger.info(f"Enviando imagen {master_image_path} y prompt '{text_prompt}'...")
        try:
            result = client.predict(
                prompt=text_prompt,
                image=handle_file(master_image_path),
                api_name="/predict"
            )
            os.rename(result, output_path)
            logger.info(f"Vídeo de acción generado exitosamente en: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error en Estudio B (Acción): {e}")
            raise
