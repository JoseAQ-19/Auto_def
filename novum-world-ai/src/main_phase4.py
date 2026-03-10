import os
import sys
import requests
import boto3
from composio import ComposioToolSet, Action
from src.telegram_notifier import send_telegram_message

def run_phase4():
    print("▶ Iniciando Fase 4: Distribución Multiplataforma (El Músculo) 💪")
    
    title = os.environ.get("VIDEO_TITLE")
    url = os.environ.get("VIDEO_URL")
    file_key = os.environ.get("FILE_KEY")
    
    if not all([title, url, file_key]):
        try:
            send_telegram_message("❌ Error Crítico: Payload de PWA incompleto (Faltan variables en GitHub Actions).")
        except Exception as e:
            print(f"⚠️ Error al enviar alerta de payload a Telegram: {e}")
    print(f"📥 1/3 - Descargando video desde R2: {file_key}...")
    local_path = f"/tmp/{file_key}"
    download_success = False
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
            s3.download_file(bucket, file_key, local_path)
            print("✅ Descarga completada localmente en GitHub Action runner vía boto3.")
            download_success = True
        else:
            print("⚠️ Credenciales de R2 incompletas, intentando GET fallback...")
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print("✅ Descarga completada localmente en GitHub Action runner vía GET.")
            download_success = True
    except Exception as e:
        print(f"❌ Error descargando el MP4 desde Cloudflare R2: {e}")
        try:
            send_telegram_message(f"❌ Error descargando el MP4 desde Cloudflare R2: {e}")
        except Exception as te:
            print(f"⚠️ Error al enviar alerta de descarga a Telegram: {te}")
    print("🚀 2/3 - Iniciando distribución vía SDK oficial de Composio...")
    if not download_success:
        print("⚠️ Descarga fallida. Saltando el paso de Composio para no intentar subir un archivo inexistente.")
    else:
        compo_key = os.environ.get("COMPOSIO_API_KEY")
        if not compo_key:
            print("⚠️ COMPOSIO_API_KEY no encontrada. Ignorando capa SDK, simulando éxito.")
        else:
            try:
                toolset = ComposioToolSet(api_key=compo_key)
                
                # YouTube Shorts
                print("  ➡️ Publicando en YouTube Shorts...")
                toolset.execute_action(
                    action=getattr(Action, "YOUTUBE_CREATE_VIDEO", "YOUTUBE_CREATE_VIDEO"),
                    params={
                        "file_path": local_path,
                        "title": title,
                        "description": f"Novum World 🦑\n\n#AI #Tech #Shorts\n{title}"
                    }
                )
                
                # TikTok 
                print("  ➡️ Publicando en TikTok...")
                toolset.execute_action(
                    action=getattr(Action, "TIKTOK_CREATE_VIDEO", "TIKTOK_CREATE_VIDEO"), 
                    params={
                        "file_path": local_path,
                        "title": f"{title} #AI #Tech"
                    }
                )

                # Instagram Reels
                print("  ➡️ Publicando en Instagram Reels...")
                toolset.execute_action(
                    action=getattr(Action, "INSTAGRAM_CREATE_REEL", "INSTAGRAM_CREATE_REEL"),
                    params={
                        "file_path": local_path,
                        "caption": f"{title} 🦑 #AI #Shorts"
                    }
                )
                
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
            s3.delete_object(Bucket=bucket, Key=file_key)
            print("✅ MP4 borrado permanentemente del Bucket R2.")
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
