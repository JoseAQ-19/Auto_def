import os
import logging
from audio_engine import AudioEngine
from video_engine import VideoEngine
# Importaremos os.system o subprocess para FFmpeg más adelante si es necesario,
# por ahora hacemos el scaffold de la orquestación.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NovumDirector:
    def __init__(self):
        self.audio_engine = AudioEngine()
        self.video_engine = VideoEngine()

    def get_todays_script(self):
        """
        [Actualizado] Devuelve el script generado basado en data_scan.
        """
        from data_scanner import DataScanner
        scanner = DataScanner()
        top_url = scanner.get_top_article()
        prompt_guion = scanner.compose_prompt_for_script(top_url)
        
        logger.info(f"Generando script del día inspirado en GSC...\nPrompt: {prompt_guion}")
        
        return [
            {"type": "dialogue", "text": "¡Hola a todos! Bienvenidos a Novum World."},
            {"type": "dialogue", "text": prompt_guion},
            {"type": "action", "prompt": "Novum tecleando intensamente frente a pantallas holográficas investigando analíticas."},
            {"type": "dialogue", "text": "Este logro nos inspira a seguir construyendo. ¡Hasta mañana!"}
        ]

    def process_scene(self, scene: dict, master_image_path: str, index: int) -> str:
        """
        Procesa una escena individual y devuelve el path del vídeo generado.
        """
        scene_type = scene.get("type")
        output_video_path = f"scene_{index}.mp4"

        if scene_type == "dialogue":
            text = scene.get("text", "")
            logger.info(f"Procesando escena de diálogo [{index}]: {text}")
            audio_path = f"scene_{index}.mp3"
            self.audio_engine.generate_audio(text, output_path=audio_path)
            
            # Generar vídeo mediante el podcast studio
            return self.video_engine.generate_podcast_video(
                audio_path=audio_path,
                master_image_path=master_image_path,
                output_path=output_video_path
            )

        elif scene_type == "action":
            prompt = scene.get("prompt", "")
            logger.info(f"Procesando escena de acción [{index}]: {prompt}")
            
            # Generar vídeo mediante el action set
            return self.video_engine.generate_action_video(
                text_prompt=prompt,
                master_image_path=master_image_path,
                output_path=output_video_path
            )
        else:
            logger.warning(f"Tipo de escena desconocido: {scene_type}")
            return ""

    def assemble_videos(self, video_paths: list, final_output: str="final_video.mp4"):
        """
        [Scaffold] Une todos los clips usando FFmpeg / MoviePy.
        """
        logger.info(f"Ensamblando {len(video_paths)} clips en {final_output}...")
        # En producción: moviepy.editor.concatenate_videoclips o llamada subprocess a ffmpeg.
        with open(final_output, "w") as f:
            f.write("Simulated merged video.")
        return final_output

    def run_daily_workflow(self, master_image_path: str):
        """
        Ejecuta el pipeline completo.
        """
        logger.info("Iniciando Workflow Diario de Novum...")
        script_scenes = self.get_todays_script()
        
        video_clips = []
        for i, scene in enumerate(script_scenes):
            try:
                clip_path = self.process_scene(scene, master_image_path, i)
                if clip_path:
                    video_clips.append(clip_path)
            except Exception as e:
                logger.error(f"Error procesando escena {i}: {e}")
                
        if video_clips:
            final_video = self.assemble_videos(video_clips)
            logger.info(f"Workflow finalizado exitosamente. Vídeo en {final_video}")
            return final_video
        else:
            logger.error("No se generó ningún clip. Abortando ensamblaje.")
            return None

if __name__ == "__main__":
    # Setup mínimo para prueba local
    director = NovumDirector()
    # Usar una imagen dummy si no existe
    dummy_image = "assets/novum_master_image.png"
    if not os.path.exists("assets"):
        os.makedirs("assets")
    if not os.path.exists(dummy_image):
        with open(dummy_image, "w") as f:
            f.write("dummy")
            
    director.run_daily_workflow(dummy_image)
