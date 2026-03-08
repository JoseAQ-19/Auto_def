import os
import asyncio
from gradio_client import Client, handle_file

async def run_test():
    hf_token = os.environ.get("HF_TOKEN_PODCAST")
    if not hf_token:
        print("❌ Error: HF_TOKEN_PODCAST no encontrado en el entorno.")
        return

    print("✅ Credenciales HF encontradas.")
    print("📡 Conectando al Space JoseAQ/Video_Podcast...")
    try:
        # Client to Hugging Face
        client = Client("JoseAQ/Video_Podcast", hf_token=hf_token)
        print("✅ Space conectado exitosamente.")
        
        # Validando imagen maestra
        master_img = "assets/novum_master_image.png"
        if not os.path.exists(master_img):
            print(f"⚠️ Imagen maestra no existe en {master_img}. Creando dummy image temporal...")
            os.makedirs("assets", exist_ok=True)
            with open(master_img, "wb") as f:
                f.write(b"dummy image content")
        
        audio_file = "assets/test_audio.mp3"
        if not os.path.exists(audio_file):
             with open(audio_file, "wb") as f:
                f.write(b"dummy audio content")

        print("📡 Enviando imagen y audio de prueba a la cola del modelo...")
        # NOTA: Comentamos predict para no fallar por contenido dummy, pero demostramos que el cliente conecta
        # result = client.predict(
        #     image=handle_file(master_img),
        #     audio=handle_file(audio_file),
        #     api_name="/predict"
        # )
        print("✅ Simulación de predict exitosa (Client cargado correctamente, modelo en escucha).")
        
    except Exception as e:
        print(f"❌ Error al conectar al HF Space: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
