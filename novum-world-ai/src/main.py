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
        # GSD: Next step would be sending this prompt to an LLM (Groq/OpenAI) to return JSON.
        # For now, we simulate the LLM structured JSON output.
        logger.info(f"Simulando Cerebro LLM. Prompt puente: {prompt_guion}")
        
        return [
            {
                "type": "podcast", 
                "text": "¡Alarma de ciberseguridad! Hoy destapamos un escándalo."
            },
            {
                "type": "action", 
                "prompt": "Cinematic zoom in to a dark room with green hacker code falling on screens, glowing neon, 4k"
            },
            {
                "type": "podcast", 
                "text": "Protege tus datos, y recuerda: la información es poder. ¡Hasta mañana!"
            }
        ]

    def process_scene(self, scene: dict, master_image_path: str, index: int) -> str:
        """
        Procesa una escena individual y devuelve el path del vídeo generado.
        """
        scene_type = scene.get("type")
        output_video_path = f"scene_{index}.mp4"

        if scene_type == "podcast" or scene_type == "dialogue":
            text = scene.get("text", "")
            logger.info(f"Procesando escena de diálogo [{index}]: {text}")
            audio_path = f"scene_{index}.mp3"
            actual_audio_path = self.audio_engine.generate_audio(text, output_path=audio_path)
            
            # Generar vídeo mediante el podcast studio
            return self.video_engine.generate_podcast_video(
                audio_path=actual_audio_path,
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
        [Actualizado] Une todos los clips usando MoviePy o copia si es solo uno.
        """
        import shutil
        logger.info(f"Ensamblando {len(video_paths)} clips en {final_output}...")
        if len(video_paths) == 1:
            shutil.copy(video_paths[0], final_output)
            return final_output
            
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips
            clips = [VideoFileClip(p) for p in video_paths]
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(final_output, fps=24, logger=None)
            for clip in clips:
                clip.close()
            return final_output
        except Exception as e:
            logger.error(f"Error ensamblando video con moviepy: {e}")
            if video_paths:
                shutil.copy(video_paths[0], final_output)
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
    
    # Path real de la imagen maestra
    master_image = "assets/novum_master.png"
    if not os.path.exists(master_image):
        logger.error(f"No se encontró la imagen maestra en {master_image}. Abortando.")
        exit(1)
            
    director.run_daily_workflow(master_image)
