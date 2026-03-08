import os
import logging
from gradio_client import Client, handle_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoEngine:
    def __init__(self):
        # Tokens y URLs para los dos espacios Hugging Face
        self.podcast_url = (os.environ.get("HF_SPACE_PODCAST_URL") or "").strip()
        self.action_url = (os.environ.get("HF_SPACE_ACTION_URL") or "").strip()
        self.podcast_token = (os.environ.get("HF_TOKEN_PODCAST") or "").strip()
        self.action_token = (os.environ.get("HF_TOKEN_ACTION") or "").strip()

        if not self.podcast_url or not self.action_url or not self.podcast_token or not self.action_token:
            logger.warning("Faltan credenciales de Hugging Face. Las conexiones podrían fallar.")

    def generate_podcast_video(self, audio_path: str, master_image_path: str, output_path: str = "podcast_output.mp4") -> str:
        """
        Conecta al Space LTX-2 (o similar para Lip-Sync), enviando el audio e imagen maestra.
        """
        if not self.podcast_url:
            raise ValueError("HF_SPACE_PODCAST_URL no configurada.")
            
        logger.info(f"Conectando al Estudio A (Podcast): {self.podcast_url}")
        client = Client(self.podcast_url, token=self.podcast_token)
        
        # Asumimos que los parámetros del gradio client del modelo lip-sync son: imagen maestra, audio.
        # Ajustar los predict endpoints según la API expuesta por el Space concreto.
        logger.info(f"Enviando imagen {master_image_path} y audio {audio_path}...")
        try:
            result = client.predict(
                image_path=handle_file(master_image_path),
                audio_path=handle_file(audio_path),
                prompt="A realistic person speaking naturally",
                negative_prompt="low quality, bad anatomy, worst quality, distorted",
                seed=-1,  # Passing as int in case string is rejected by Space
                api_name="/generate"
            )
            # El client.predict en algunos Spaces devuelve una tupla (video_path, metadata, etc.)
            video_file = result[0] if isinstance(result, (tuple, list)) else result
            os.rename(video_file, output_path)
            logger.info(f"Vídeo de podcast generado exitosamente en: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error en Estudio A (Podcast): {e}")
            try: logger.error(f"Endpoints Podcast: {client.endpoints}")
            except: pass
            raise

    def generate_action_video(self, text_prompt: str, master_image_path: str, output_path: str = "action_output.mp4") -> str:
        """
        Conecta al Space Wan2.2 (Omni Video Factory), enviando el prompt de texto e imagen maestra.
        """
        if not self.action_url:
            raise ValueError("HF_SPACE_ACTION_URL no configurada.")
            
        logger.info(f"Conectando al Estudio B (Acción): {self.action_url}")
        client = Client(self.action_url, token=self.action_token)
        
        # Asumimos que los parámetros del gradio client son: prompt visual, imagen maestra.
        logger.info(f"Enviando imagen {master_image_path} y prompt '{text_prompt}'...")
        try:
            result = client.predict(
                first_frame=handle_file(master_image_path),
                end_frame=handle_file(master_image_path),
                prompt=text_prompt,
                duration=6.0,
                enhance_prompt=False,
                generation_mode="i2v",
                height=720,
                width=1280,
                randomize_seed=True,
                seed=0,
                api_name="/generate_video"
            )
            video_file = result[0] if isinstance(result, (tuple, list)) else result
            os.rename(video_file, output_path)
            logger.info(f"Vídeo de acción generado exitosamente en: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error en Estudio B (Acción): {e}")
            try: logger.error(f"Endpoints Acción: {client.endpoints}")
            except: pass
            raise
