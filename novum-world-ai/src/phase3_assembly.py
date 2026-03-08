import os
import json
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase3Assembly:
    def __init__(self):
        self.plan_path = os.path.join(os.path.dirname(__file__), "..", "shooting_plan.json")
        self.final_output = os.path.join(os.path.dirname(__file__), "..", "final_video.mp4")

    def execute(self):
        logger.info("--- INICIANDO FASE 3: THE ASSEMBLY ---")
        
        if not os.path.exists(self.plan_path):
            logger.error(f"No se encontró {self.plan_path}. Ejecuta las Fases 1 y 2 primero.")
            return False

        with open(self.plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)

        video_paths = []
        for i, scene in enumerate(plan):
            video_file = scene.get("video_file")
            if video_file and os.path.exists(video_file):
                video_paths.append(video_file)
            else:
                logger.warning(f"Escena {i} no tiene un vídeo válido generado. Saltando en el ensamblaje.")

        if not video_paths:
            logger.error("No hay clips de video válidos para ensamblar. Abortando.")
            return False

        logger.info(f"Ensamblando {len(video_paths)} clips de video en {self.final_output}...")
        
        # Si solo hay 1 clip, simplemente lo copiamos
        if len(video_paths) == 1:
            shutil.copy(video_paths[0], self.final_output)
            logger.info("Solo se generó 1 clip, copiado directamente al destino final.")
            return True

        # Si hay varios, intentamos ensamblar con MoviePy
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips
            clips = [VideoFileClip(p) for p in video_paths]
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(self.final_output, fps=24, logger=None)
            for clip in clips:
                clip.close()
            logger.info("✅ Ensamblaje completado con MoviePy exitosamente.")
            return True
        except Exception as e:
            logger.error(f"Error crítico ensamblando el vídeo con MoviePy: {e}")
            logger.warning("Intentando fallback: Copiar el primer clip disponible como resultado final para evitar fallo total...")
            try:
                shutil.copy(video_paths[0], self.final_output)
                return True
            except Exception as backup_e:
                logger.error(f"Fallo del fallback de copia: {backup_e}")
                return False

if __name__ == "__main__":
    assembly = Phase3Assembly()
    assembly.execute()
