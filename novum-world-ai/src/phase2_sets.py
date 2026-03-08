import os
import json
import logging
import time
from huggingface_hub import HfApi
from video_engine import VideoEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase2Sets:
    def __init__(self):
        self.video_engine = VideoEngine()
        
        # Búsqueda robusta del plan de rodaje (Trinity Architecture Support)
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "shooting_plan.json"),
            os.path.join(os.getcwd(), "shooting_plan.json"),
            os.path.join(os.getcwd(), "novum-world-ai", "shooting_plan.json"),
            "shooting_plan.json"
        ]
        
        self.plan_path = None
        for p in possible_paths:
            if os.path.exists(p):
                self.plan_path = p
                logger.info(f"🎯 Plan de rodaje localizado en: {p}")
                break
        
        if not self.plan_path:
            self.plan_path = possible_paths[0] # Fallback para reporte de error consistente
            
        self.podcast_repo_id = os.environ.get("HF_SPACE_PODCAST_URL", "").replace("https://huggingface.co/spaces/", "").replace("https://joseaq-video-podcast.hf.space/", "JoseAQ/video-podcast").strip("/") or "JoseAQ/video-podcast"
        self.action_repo_id = os.environ.get("HF_SPACE_ACTION_URL", "").replace("https://huggingface.co/spaces/", "").replace("https://joseaq-video-action.hf.space/", "JoseAQ/video-action").strip("/") or "JoseAQ/video-action"

    def audit_and_fix_space(self, repo_id: str, token: str):
        """
        Intenta arreglar el Space si da 500 o se queda en Process Restarting.
        Usa token Fine-grained con permisos Write para reiniciar o re-buildear components.
        """
        logger.warning(f"🚨 Auditoría Activada 🚨 Intentando reparar Space colapsado: {repo_id}")
        if not token:
            logger.error(f"No hay token HF configurado para reparar {repo_id}")
            return False
            
        try:
            api = HfApi(token=token)
            
            # Opción 1: Intentar un reinicio limpio del servidor hardware en HF
            logger.info(f"Solicitando Hardware Restart en HF para {repo_id}...")
            api.restart_space(repo_id=repo_id)
            
            logger.info("Comando de reinicio enviado. Esperando 15s de gracia...")
            time.sleep(15)
            return True
        except Exception as e:
            logger.error(f"Fallo en reinicio suave de HF Space {repo_id}: {e}")
            logger.info("⚙️ Activando Opción 2: Modificación fantasma en requirements.txt para forzar Docker Re-Build...")
            try:
                api = HfApi(token=token)
                try:
                    c = api.hf_hub_download(repo_id=repo_id, repo_type="space", filename="requirements.txt")
                    with open(c, "r", encoding="utf-8") as f:
                        reqs = f.read()
                except Exception:
                    reqs = "# Requisitos\n"
                    
                reqs += "\n# Auto-trigger build para resolver Error 500"
                api.upload_file(
                    path_or_fileobj=reqs.encode("utf-8"),
                    path_in_repo="requirements.txt",
                    repo_id=repo_id,
                    repo_type="space",
                    commit_message="GSD Auto-fix: Forzando rebuild tras Caída o Error 500 en Gradio"
                )
                logger.info("✅ Push a requirements.txt enviado. Rebuild del Docker en curso en Hugging Face.")
                return True
            except Exception as e2:
                logger.error(f"Falla total al intentar auto-recuperar el Space: {e2}")
                return False

    def execute(self):
        logger.info("--- INICIANDO FASE 2: THE SETS ---")
        
        if not os.path.exists(self.plan_path):
            logger.error(f"No se encontró {self.plan_path}. Ejecuta la Fase 1 primero.")
            return False

        with open(self.plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)

        master_image_path = os.path.join(os.path.dirname(__file__), "..", "assets", "novum_master.png")
        if not os.path.exists(master_image_path):
            logger.warning(f"Master image no encontrada en {master_image_path}. Creando un mock image de textura para evitar crash fatal...")
            os.makedirs(os.path.dirname(master_image_path), exist_ok=True)
            import base64
            # 1x1 pixel PNG válido base64
            b64_img = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
            with open(master_image_path, "wb") as f:
                f.write(base64.b64decode(b64_img))

        base_dir = os.path.dirname(self.plan_path)
        clips_generated = []

        for i, scene in enumerate(plan):
            scene_type = scene.get("type", "")
            output_video_path = os.path.join(base_dir, f"scene_{i}.mp4")

            try:
                if scene_type == "podcast":
                    audio_file = scene.get("audio_file")
                    if not audio_file or not os.path.exists(audio_file):
                        logger.error(f"Omitiendo clip {i}: Falta audio_file válido. Revisa salidad de Fase 1.")
                        continue
                        
                    logger.info(f"🎥 Grabando Podcast [{i}] en el Set A...")
                    try:
                        clip = self.video_engine.generate_podcast_video(
                            audio_path=audio_file,
                            master_image_path=master_image_path,
                            output_path=output_video_path
                        )
                        clips_generated.append(clip)
                        scene["video_file"] = clip
                    except Exception as e:
                        msg = str(e).lower()
                        if "500" in msg or "timeout" in msg or "restarting" in msg or "connect" in msg:
                            self.audit_and_fix_space(self.podcast_repo_id, self.video_engine.podcast_token)
                        logger.error(f"Fallo en Grabación Podcast: {e}")
                        scene["video_file"] = ""

                elif scene_type == "action":
                    prompt = scene.get("prompt", "")
                    logger.info(f"💥 Grabando Action [{i}] en el Set B... Prompt: {prompt[:40]}...")
                    try:
                        clip = self.video_engine.generate_action_video(
                            text_prompt=prompt,
                            master_image_path=master_image_path,
                            output_path=output_video_path
                        )
                        clips_generated.append(clip)
                        scene["video_file"] = clip
                    except Exception as e:
                        msg = str(e).lower()
                        if "500" in msg or "timeout" in msg or "restarting" in msg or "connect" in msg:
                            self.audit_and_fix_space(self.action_repo_id, self.video_engine.action_token)
                        logger.error(f"Fallo en Grabación Acción: {e}")
                        scene["video_file"] = ""

            except Exception as e:
                logger.error(f"Error nativo interno procesando escena {i}: {e}")
                scene["video_file"] = ""

        # Update JSON sequence for Assembly
        with open(self.plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=4, ensure_ascii=False)

        logger.info(f"Fase 2 finalizada. Se han renderizado {len(clips_generated)}/{len(plan)} clips validos para Ensamble.")
        return True

if __name__ == "__main__":
    sets = Phase2Sets()
    sets.execute()
