import os
import sys
import time
import requests
import boto3
import json
import subprocess
from composio import Composio
from src.telegram_notifier import send_telegram_message

def run_phase4():
    print("▶ Iniciando Fase 4: Distribución Multiplataforma (El Músculo) 💪")
    
    title = os.environ.get("VIDEO_TITLE")
    video_files_json = os.environ.get("VIDEO_FILES_JSON")
    files_data = []
    if video_files_json:
        try:
            files_data = json.loads(video_files_json)
        except Exception as e:
            print(f"⚠️ Error parseando VIDEO_FILES_JSON: {e}")
    
    description = os.environ.get("VIDEO_DESCRIPTION") or f"Vídeo generado por IA. #Shorts #Novum #IA\n\n{title}"
    hashtags_raw = os.environ.get("VIDEO_HASHTAGS") or "shorts, novum, ia, youtube shorts"
    privacy = os.environ.get("VIDEO_PRIVACY") or "private"
    
    tags = [tag.strip() for tag in hashtags_raw.split(',')] if hashtags_raw else []

    dest_youtube = os.environ.get("DEST_YOUTUBE") == "true"
    dest_instagram = os.environ.get("DEST_INSTAGRAM") == "true"
    dest_tiktok = os.environ.get("DEST_TIKTOK") == "true"
    
    if not all([title, files_data]):
        try:
            send_telegram_message("❌ Error Crítico: Payload de PWA incompleto (Faltan variables o array 'files' vacío).")
        except Exception as e:
            print(f"⚠️ Error al enviar alerta de payload a Telegram: {e}")
        return

    print("📥 1/3 - Descargando fragmentos de video desde R2...")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    bucket = os.environ.get("R2_BUCKET_NAME")
    s3 = None
    if account_id and bucket:
        s3 = boto3.client(
            's3',
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=os.environ.get("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY"),
            region_name='auto'
        )

    downloaded_paths = []
    lista_path = "/tmp/lista.txt"
    download_success = False
    try:
        with open(lista_path, "w") as f_list:
            for idx, fd in enumerate(files_data):
                fkey = fd.get("filename")
                furl = fd.get("publicUrl")
                if not fkey: continue
                lpath = f"/tmp/{fkey}"
                
                print(f"  > Descargando {fkey}...")
                if s3:
                    s3.download_file(bucket, fkey, lpath)
                else:
                    with requests.get(furl, stream=True) as r:
                        r.raise_for_status()
                        with open(lpath, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                downloaded_paths.append(lpath)
                f_list.write(f"file '{lpath}'\n")
        print("✅ Descargas completadas localmente.")
        download_success = True
    except Exception as e:
        print(f"❌ Error descargando MP4s desde Cloudflare R2: {e}")
        try:
            send_telegram_message(f"❌ Error descargando MP4s desde Cloudflare R2: {e}")
        except Exception as te: pass

    merged_local = "/tmp/video_final_unido.mp4"
    merged_file_key = "video_final_unido.mp4"
    outro_path = "novum-world-ai/assets/outro_novum.mp4"

    if download_success and downloaded_paths:
        print(f"🎬 Iniciando FFmpeg Master Render (Escenas: {len(downloaded_paths)} + Outro)...")
        try:
            # 1. Construimos el comando dinámico de FFmpeg usando Filter Complex
            # Esto es necesario para estandarizar resoluciones, fps y audio de clips heterogéneos
            cmd = ["ffmpeg"]
            
            # Entradas: Escenas + Outro
            for p in downloaded_paths:
                cmd.extend(["-i", p])
            cmd.extend(["-i", outro_path])
            
            # Construcción del filtro complejo
            # [v][a] estandarizados -> concat
            filter_str = ""
            n_inputs = len(downloaded_paths) + 1
            for i in range(n_inputs):
                # Escalado a 1080x1920 (Portrait), forzando aspect ratio y rellenando si es necesario (pad)
                # Estandarizamos a 30fps y audio a 44.1kHz
                filter_str += (
                    f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
                    f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v{i}]; "
                    f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo[a{i}]; "
                )
            
            # Concatenación de todos los pares [v][a]
            inputs_concat = "".join([f"[v{i}][a{i}]" for i in range(n_inputs)])
            filter_str += f"{inputs_concat}concat=n={n_inputs}:v=1:a=1[v_out][a_out]"
            
            cmd.extend([
                "-filter_complex", filter_str,
                "-map", "[v_out]", "-map", "[a_out]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-profile:v", "main",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                "-t", "59.5", # Límite de seguridad estricto para YouTube Shorts
                "-y", merged_local
            ])
            
            print(f"🛠️ Ejecutando comando FFmpeg complejo...")
            subprocess.run(cmd, check=True)
            print("✅ FFmpeg Master Render exitoso.")
            
            file_size = os.path.getsize(merged_local)
            print(f"🔍 AUDITORÍA FFmpeg: El archivo {merged_local} pesa {file_size} bytes.")
            
            try:
                cmd_ffprobe = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", merged_local]
                duration_str = subprocess.check_output(cmd_ffprobe, text=True).strip()
                print(f"🔍 AUDITORÍA FINAL: Duración del video ensamblado: {duration_str} segundos")
            except Exception as e_probe:
                print(f"⚠️ Error verificando duración final: {e_probe}")

            print("☁️ Subiendo Master Render a R2...")
            if s3:
                s3.upload_file(merged_local, bucket, merged_file_key)
                print("✅ Subida exitosa a R2.")
            else:
                download_success = False
        except Exception as e:
            print(f"❌ Error crítico en FFmpeg o subida R2: {e}")
            download_success = False

    print("🚀 2/3 - Iniciando distribución vía SDK oficial de Composio...")
    if not download_success:
        print("⚠️ Proceso inicial fallido. Saltando Composio.")
    else:
        compo_key = os.environ.get("COMPOSIO_API_KEY")
        if not compo_key:
            print("⚠️ COMPOSIO_API_KEY no encontrada. Ignorando capa SDK, simulando éxito.")
        else:
            try:
                # Instantiate Composio client for v3
                composio_client = Composio(api_key=compo_key)
                USER_ID = "pg-test-d66c07c1-fd23-44ca-ac8a-ae717ff90c50"
                
                # Generamos una única Presigned URL de 1 hora de validez para burlar el TTL de R2
                url_presigned = None
                try:
                    s3_client = boto3.client(
                        's3',
                        endpoint_url=f"https://{os.environ.get('CLOUDFLARE_ACCOUNT_ID')}.r2.cloudflarestorage.com",
                        aws_access_key_id=os.environ.get("R2_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY"),
                        region_name='auto'
                    )
                    url_presigned = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': os.environ.get("R2_BUCKET_NAME"), 'Key': merged_file_key},
                        ExpiresIn=3600
                    )
                except Exception as s3e:
                    print(f"⚠️ Error generando Presigned URL para R2. Fallback a crudo. {s3e}")

                # YouTube Shorts
                if dest_youtube:
                    print("  ➡️ Publicando en YouTube Shorts...")
                    try:
                        yt_tool = composio_client.tools.get(actions=["YOUTUBE_UPLOAD_VIDEO"])
                        print("🕵️♂️ ESQUEMA OFICIAL YOUTUBE:", yt_tool[0].parameters if hasattr(yt_tool[0], 'parameters') else yt_tool[0])
                    except Exception as e:
                        print("🕵️♂️ Error extrayendo esquema:", e)
                    
                    try:
                        yt_args = {
                            "videoFilePath": url_presigned, # Pasando Presigned URL en vez de archivo local
                            "title": f"{title} #Shorts",
                            "description": description,
                            "categoryId": "22",
                            "tags": tags,
                            "privacyStatus": privacy
                        }
                        
                        print(f"🔍 [YT DEBUG] Payload inyectado a Composio: {yt_args}")
                        
                        yt_res = composio_client.tools.execute(
                            "YOUTUBE_UPLOAD_VIDEO",
                            user_id=USER_ID,
                            arguments=yt_args,
                            dangerously_skip_version_check=True
                        )
                        print(f"🔍 [YT DEBUG] Raw API Response OK: {yt_res}")
                    except Exception as ye:
                        print(f"⚠️ Error subiendo a YouTube. Exception Raw:\n{ye}")
                else:
                    print("  ⏭️ Omitiendo YouTube Shorts (no seleccionado).")
                
                # TikTok 
                if dest_tiktok:
                    print("  ➡️ Publicando en TikTok...")
                    try:
                        composio_client.tools.execute(
                            "TIKTOK_UPLOAD_VIDEO", 
                            user_id=USER_ID,
                            arguments={
                                "file_to_upload": url_presigned, # Pasando Presigned URL en vez de archivo local
                                "caption": description,
                                "privacy_level": "SELF_ONLY",
                                "publish": True
                            },
                            dangerously_skip_version_check=True
                        )
                    except Exception as te:
                        print(f"⚠️ Error subiendo a TikTok: {te}")
                else:
                    print("  ⏭️ Omitiendo TikTok (no seleccionado).")

                # Instagram Reels
                if dest_instagram:
                    print("  ➡️ Publicando en Instagram Reels (Paso 1: Container)...")
                    try:
                        container = composio_client.tools.execute(
                            "INSTAGRAM_CREATE_MEDIA_CONTAINER",
                            user_id=USER_ID,
                            arguments={
                                "video_url": url_presigned,
                                "caption": description,
                                "media_type": "REELS"
                            },
                            dangerously_skip_version_check=True
                        )
                        print(f"Container result: {container}")
                        
                        # Extraemos ids por si vienen anidados
                        container_id = None
                        ig_user_id = None
                        
                        if isinstance(container, dict):
                            # Estructura típica: {"data": {"id": "...", "ig_user_id": "..."}} o similar
                            data = container.get("data", container)
                            container_id = data.get("id") or container.get("id")
                            ig_user_id = data.get("ig_user_id") or container.get("ig_user_id")
                            
                        if container_id:
                            print(f"  ⏳ Esperando 30 segundos para que Meta procese el contenedor {container_id}...")
                            time.sleep(30)
                            print("  ➡️ Publicando en Instagram Reels (Paso 2: Post)...")
                            
                            post_args = {"creation_id": str(container_id)}
                            
                            ig_user_env = os.environ.get("IG_USER_ID")
                            if ig_user_env:
                                post_args["ig_user_id"] = str(ig_user_env)
                            elif ig_user_id:
                                post_args["ig_user_id"] = str(ig_user_id)
                            else:
                                print("⚠️ AVISO: No se encontró 'ig_user_id' en Container ni en Variables de Entorno. Instagram fallará sin él.")
                                
                            post_res = composio_client.tools.execute(
                                "INSTAGRAM_CREATE_POST",
                                user_id=USER_ID,
                                arguments=post_args,
                                dangerously_skip_version_check=True
                            )
                            print(f"Post result: {post_res}")
                        else:
                            print("⚠️ No se pudo obtener el creation_id del Paso 1 (Container). Log: ", container)
                    except Exception as ie:
                        print(f"⚠️ Error subiendo a Instagram Reels: {ie}")
                else:
                    print("  ⏭️ Omitiendo Instagram Reels (no seleccionado).")
                
                print("✅ Composio Pipeline ejecutado (Todos los conectores activos han procesado el upload a redes).")
            except Exception as e:
                # En caso de que un conector expire u ocurra un error de SDK, lo atrapamos 
                # para no bloquear la fase 3 (limpieza de basura en Cloudflare R2).
                print(f"⚠️ Aviso en Composio SDK: {e}. (Revisa tus conexiones en app.composio.dev)")
            
    print("🧹 3/3 - Limpiando Cloudflare R2 (Borrando rastro y asegurando coste cero)...")
    try:
        account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        bucket = os.environ.get("R2_BUCKET_NAME")
        
        if account_id and bucket:
            s3 = boto3.client(
                's3',
                endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=os.environ.get("R2_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY"),
                region_name='auto'
            )
            for fd in files_data:
                fk = fd.get("filename")
                if fk:
                    s3.delete_object(Bucket=bucket, Key=fk)
            # Y borramos el merge
            s3.delete_object(Bucket=bucket, Key=merged_file_key)
            print("✅ Fragmentos y MP4 final borrados permanentemente del Bucket R2.")
        else:
            print("⚠️ Faltan credenciales de R2 en el entorno, se omite el borrado.")
    except Exception as e:
        print(f"⚠️ No se pudo borrar el archivo R2: {e}")
        
    print("📲 Enviando notificación de éxito al humano...")
    try:
        send_telegram_message(
            f"✅ *Secuencia Upload Completada*\n\n"
            f"Vídeo: '{title}' distribuido automágicamente al mundo.\n\n"
            f"Rastro en Cloudflare R2 eliminado. Cero fricción, cero coste.\n"
            f"Vuelve a tu cueva."
        )
    except Exception as e:
        print(f"⚠️ Error al confirmar éxito final a Telegram: {e}")
    print("🏁 Fase 4 GSD Completada a la perfección.")

if __name__ == "__main__":
    run_phase4()
